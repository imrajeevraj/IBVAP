import os
import yaml
import logging
import math
import threading
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from backend.app.core.database import SessionLocal
from backend.app.models.event import SecurityEvent
from backend.app.services.risk_engine import risk_engine
from backend.app.services.evidence_service import evidence_service
from backend.app.services.alert_dispatch import alert_dispatch

logger = logging.getLogger("BorderRulesService")

class BorderRulesService:
    def __init__(self, config_path: str = "configs/zones.yaml"):
        self.config_path = config_path
        self.zones_config = {}
        self.load_config()
        
        # Track previous states: { camera_id: { track_id: { 'zones': {zone_id: bool}, 'point': (x,y), 'last_event_time': float } } }
        self.track_states = {}
        self.db_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="DB-Event-Worker")

    def reset_camera(self, camera_id: str):
        if camera_id in self.track_states:
            self.track_states[camera_id] = {}

    def load_config(self):
        try:
            abs_path = os.path.abspath(self.config_path)
            if os.path.exists(abs_path):
                with open(abs_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                    candidate = config.get("zones", {})
                    self._validate_config(candidate)
                    self.zones_config = candidate
                logger.info("Zones configuration loaded successfully.")
            else:
                logger.warning(f"Zones config not found at {abs_path}")
        except Exception as e:
            logger.error(f"Failed to load zones config: {e}")

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        if not isinstance(config, dict):
            raise ValueError("zones must be a mapping")
        for camera_id, camera_config in config.items():
            if not isinstance(camera_config, dict):
                raise ValueError(f"camera config {camera_id} must be a mapping")
            for zone in camera_config.get("restricted_zones", []):
                polygon = zone.get("polygon") if isinstance(zone, dict) else None
                if not isinstance(polygon, list) or len(polygon) < 3:
                    raise ValueError(f"zone polygon for {camera_id} must have at least 3 points")
                for point in polygon:
                    if not isinstance(point, (list, tuple)) or len(point) != 2:
                        raise ValueError(f"zone polygon for {camera_id} contains an invalid point")
                    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in point):
                        raise ValueError(f"zone polygon for {camera_id} contains a non-finite point")
            for fence in camera_config.get("virtual_fences", []):
                line = fence.get("line") if isinstance(fence, dict) else None
                if not isinstance(line, list) or len(line) != 2:
                    raise ValueError(f"fence line for {camera_id} must have 2 points")
                if not all(isinstance(point, (list, tuple)) and len(point) == 2 for point in line):
                    raise ValueError(f"fence line for {camera_id} contains an invalid point")

    def get_camera_config(self, camera_id: str) -> Dict:
        return self.zones_config.get(camera_id, {"restricted_zones": [], "virtual_fences": []})

    @staticmethod
    def is_point_in_polygon(x: float, y: float, polygon: List[List[float]]) -> bool:
        """Ray casting algorithm to determine if a point is inside a polygon."""
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    @staticmethod
    def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> bool:
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    def do_lines_intersect(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                           p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
        return self.ccw(p1, p3, p4) != self.ccw(p2, p3, p4) and self.ccw(p1, p2, p3) != self.ccw(p1, p2, p4)

    def process_detections(self, camera_id: str, detections: List[Dict[str, Any]], frame=None):
        if camera_id not in self.track_states:
            self.track_states[camera_id] = {}
            
        cam_config = self.get_camera_config(camera_id)
        restricted_zones = cam_config.get("restricted_zones", [])
        virtual_fences = cam_config.get("virtual_fences", [])
        
        if not restricted_zones and not virtual_fences:
            return
            
        current_tracks = set()
        new_events = []

        for det in detections:
            track_id = det.get("track_id")
            if not track_id:
                continue
                
            current_tracks.add(track_id)
            obj_type = det.get("class", "UNKNOWN").upper()
            conf = det.get("confidence", 0.0)
            
            # Use bottom-center point of bounding box
            x1, y1, x2, y2 = det.get("box", [0, 0, 0, 0])
            bx = (x1 + x2) / 2.0
            by = float(y2)
            current_point = (bx, by)
            
            if track_id not in self.track_states[camera_id]:
                self.track_states[camera_id][track_id] = {
                    "zones": {},
                    "point": current_point,
                    "fences_crossed": set()
                }
                
            state = self.track_states[camera_id][track_id]
            prev_point = state["point"]
            
            # Check restricted zones (State Transitions: OUTSIDE -> INSIDE -> OUTSIDE)
            for zone in restricted_zones:
                zone_id = zone.get("id")
                polygon = zone.get("polygon")
                if not polygon: continue
                
                is_inside = self.is_point_in_polygon(bx, by, polygon)
                was_inside = state["zones"].get(zone_id, False)
                
                # Only trigger on state change (entry or exit)
                if is_inside and not was_inside:
                    new_events.append(self._create_event_dict(
                        "ZONE_ENTRY", camera_id, zone_id, track_id, obj_type, None, bx, by, conf
                    ))
                elif not is_inside and was_inside:
                    new_events.append(self._create_event_dict(
                        "ZONE_EXIT", camera_id, zone_id, track_id, obj_type, None, bx, by, conf
                    ))
                    
                state["zones"][zone_id] = is_inside
                
            # Check virtual fences (line segment crossing)
            for fence in virtual_fences:
                fence_id = fence.get("id")
                line = fence.get("line")
                if not line or len(line) < 2: continue
                
                p3 = (line[0][0], line[0][1])
                p4 = (line[1][0], line[1][1])
                
                if fence_id not in state["fences_crossed"]:
                    if prev_point != current_point and self.do_lines_intersect(prev_point, current_point, p3, p4):
                        vA = (p4[0]-p3[0], p4[1]-p3[1])
                        vB = (current_point[0]-prev_point[0], current_point[1]-prev_point[1])
                        cross_product = vA[0]*vB[1] - vA[1]*vB[0]
                        direction = "INWARD" if cross_product > 0 else "OUTWARD" if cross_product < 0 else "UNKNOWN"
                        
                        new_events.append(self._create_event_dict(
                            "VIRTUAL_FENCE_CROSSING", camera_id, fence_id, track_id, obj_type, direction, bx, by, conf
                        ))
                        state["fences_crossed"].add(fence_id)
            
            state["point"] = current_point
            
        # Clean up expired tracks
        lost_tracks = set(self.track_states[camera_id].keys()) - current_tracks
        for lt in lost_tracks:
            del self.track_states[camera_id][lt]
            
        # Non-blocking async DB persistence
        if new_events:
            self.db_executor.submit(self._persist_events_async, new_events, camera_id, frame.copy() if frame is not None else None)

    def _persist_events_async(self, events: List[Dict[str, Any]], camera_id: str, frame):
        """Execute database writes and WebSocket broadcasts in background thread pool."""
        try:
            db = SessionLocal()
            persisted_events = []
            for evt in events:
                augmented_evt = risk_engine.evaluate_event(evt)
                db_event = SecurityEvent(**augmented_evt)
                db.add(db_event)
                persisted_events.append(db_event)
            db.commit()

            # Trigger evidence snapshots
            for db_event in persisted_events:
                db.refresh(db_event)
                try:
                    snapshot_url, _ = evidence_service.capture_event(camera_id, db_event.id, frame)
                    if snapshot_url:
                        db_event.snapshot_path = snapshot_url
                        db.commit()
                except Exception as ev_err:
                    logger.error(f"Evidence capture failed: {ev_err}")

            # Notify WebSockets
            try:
                from backend.app.api.ws import manager
                import asyncio
                for db_event in persisted_events:
                    evt_dict = {
                        "id": f"evt-{db_event.id}",
                        "event_type": db_event.event_type,
                        "camera_id": db_event.camera_id,
                        "timestamp": db_event.timestamp.isoformat(),
                        "severity": db_event.severity,
                        "risk_score": db_event.risk_score,
                        "risk_reasons": db_event.risk_reasons,
                        "object_type": db_event.object_type,
                        "track_id": db_event.track_id,
                        "zone_id": db_event.zone_id,
                        "direction": db_event.direction,
                        "status": db_event.status,
                        "snapshot_url": f"/api/events/{db_event.id}/evidence/snapshot" if db_event.snapshot_path else None,
                        "video_clip_url": f"/api/events/{db_event.id}/evidence/clip" if db_event.video_clip_path else None
                    }
                    asyncio.run(manager.broadcast(evt_dict))
                    
                    # Dispatch to external systems
                    alert_dispatch.dispatch_event(evt_dict)
            except Exception as ws_err:
                logger.debug(f"WS notification failed: {ws_err}")

        except Exception as e:
            logger.error(f"Failed to persist events: {e}")
            if db: db.rollback()
        finally:
            if db: db.close()

    def _create_event_dict(self, event_type: str, camera_id: str, zone_id: str, 
                           track_id: str, object_type: str, direction: str, 
                           x: float, y: float, conf: float) -> Dict[str, Any]:
        return {
            "event_type": event_type,
            "camera_id": camera_id,
            "zone_id": zone_id,
            "track_id": track_id,
            "object_type": object_type,
            "direction": direction,
            "x": int(x),
            "y": int(y),
            "confidence": float(conf),
            "timestamp": datetime.utcnow()
        }

border_rules_service = BorderRulesService()
