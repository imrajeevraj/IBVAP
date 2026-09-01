import time
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger("TrackingService")

class KalmanBoxTracker:
    """
    Lightweight 2D Kalman Filter for bounding box tracking and velocity prediction.
    State: [x_center, y_center, aspect_ratio, height, vx, vy, va, vh]
    """
    count = 0
    def __init__(self, bbox: List[float], class_name: str, confidence: float):
        # bbox: [x1, y1, x2, y2]
        x1, y1, x2, y2 = bbox
        w = max(1.0, x2 - x1)
        h = max(1.0, y2 - y1)
        self.x = (x1 + x2) / 2.0
        self.y = (y1 + y2) / 2.0
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        
        self.class_name = class_name
        self.confidence = confidence
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        
        self.time_since_update = 0
        self.hits = 1
        self.hit_streak = 1
        self.age = 0
        self.history = []
        self.last_update_time = time.time()

    def predict(self, dt: float = 0.033):
        """Predict bounding box at current timestamp."""
        # Simple constant velocity motion model
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        
        x1 = self.x - self.w / 2.0
        y1 = self.y - self.h / 2.0
        x2 = self.x + self.w / 2.0
        y2 = self.y + self.h / 2.0
        return [x1, y1, x2, y2]

    def update(self, bbox: List[float], confidence: float, dt: float = 0.1):
        """Update state with newly observed detection."""
        x1, y1, x2, y2 = bbox
        new_w = max(1.0, x2 - x1)
        new_h = max(1.0, y2 - y1)
        new_x = (x1 + x2) / 2.0
        new_y = (y1 + y2) / 2.0
        
        # Exponential moving average velocity update
        if dt > 0.001:
            measured_vx = (new_x - self.x) / dt
            measured_vy = (new_y - self.y) / dt
            alpha = 0.6  # Smoothing factor
            self.vx = alpha * self.vx + (1 - alpha) * measured_vx
            self.vy = alpha * self.vy + (1 - alpha) * measured_vy

        # Smooth position and size
        pos_alpha = 0.8
        self.x = pos_alpha * new_x + (1 - pos_alpha) * self.x
        self.y = pos_alpha * new_y + (1 - pos_alpha) * self.y
        self.w = pos_alpha * new_w + (1 - pos_alpha) * self.w
        self.h = pos_alpha * new_h + (1 - pos_alpha) * self.h

        self.confidence = confidence
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        self.last_update_time = time.time()
        
        # Store trajectory history (limit to 50 points)
        self.history.append((self.x, self.y + self.h / 2.0))
        if len(self.history) > 50:
            self.history.pop(0)

    def get_state(self) -> List[float]:
        """Return current bounding box [x1, y1, x2, y2]."""
        return [
            self.x - self.w / 2.0,
            self.y - self.h / 2.0,
            self.x + self.w / 2.0,
            self.y + self.h / 2.0
        ]


def compute_iou(bb_test: List[float], bb_gt: List[float]) -> float:
    """Compute Intersection over Union (IoU) between two bounding boxes."""
    xx1 = max(bb_test[0], bb_gt[0])
    yy1 = max(bb_test[1], bb_gt[1])
    xx2 = min(bb_test[2], bb_gt[2])
    yy2 = min(bb_test[3], bb_gt[3])
    w = max(0.0, xx2 - xx1)
    h = max(0.0, yy2 - yy1)
    inter = w * h
    area_test = max(1.0, (bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1]))
    area_gt = max(1.0, (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1]))
    union = area_test + area_gt - inter
    return inter / union if union > 0 else 0.0


class CameraTracker:
    """
    High-performance real-time tracker for a single camera stream.
    Decoupled from detector execution:
    - Runs Kalman prediction on display frames at 30 FPS (smooth motion)
    - Associates new AI detections when available (8-10 FPS)
    """
    def __init__(self, camera_id: str, max_age: int = 15, min_hits: int = 1, iou_threshold: float = 0.3):
        self.camera_id = camera_id
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: List[KalmanBoxTracker] = []
        self.frame_count = 0
        self.last_predict_time = time.time()

    def reset(self):
        self.trackers.clear()
        self.frame_count = 0

    def predict_tracks(self) -> List[Dict[str, Any]]:
        """
        Advance all track states using velocity prediction.
        Called on every displayed video frame (30 FPS) for buttery-smooth visualization.
        """
        now = time.time()
        dt = max(0.005, min(0.1, now - self.last_predict_time))
        self.last_predict_time = now

        active_tracks = []
        for trk in self.trackers:
            predicted_box = trk.predict(dt)
            if trk.time_since_update <= self.max_age:
                prefix = self._get_prefix(trk.class_name)
                track_id = f"{self.camera_id}:{prefix}-{trk.id:03d}"
                active_tracks.append({
                    "class": trk.class_name,
                    "confidence": trk.confidence,
                    "box": [round(v, 1) for v in predicted_box],
                    "track_id": track_id,
                    "trajectory": list(trk.history)
                })
        return active_tracks

    def update_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Associate newly arrived AI detections with existing tracks (called at AI FPS).
        """
        self.frame_count += 1
        now = time.time()
        
        # Get predicted locations from existing trackers
        trks = [t.get_state() for t in self.trackers]
        dets = [d["box"] for d in detections]
        
        matched_indices = []
        unmatched_dets = list(range(len(detections)))
        unmatched_trks = list(range(len(self.trackers)))
        
        if len(trks) > 0 and len(dets) > 0:
            iou_matrix = np.zeros((len(dets), len(trks)), dtype=np.float32)
            for d_idx, det_box in enumerate(dets):
                for t_idx, trk_box in enumerate(trks):
                    # Only match if same class or compatible
                    if detections[d_idx]["class"] == self.trackers[t_idx].class_name:
                        iou_matrix[d_idx, t_idx] = compute_iou(det_box, trk_box)
                    else:
                        iou_matrix[d_idx, t_idx] = 0.0

            # Greedy matching
            while True:
                if iou_matrix.size == 0 or np.max(iou_matrix) < self.iou_threshold:
                    break
                max_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                d_idx, t_idx = max_idx
                matched_indices.append((d_idx, t_idx))
                if d_idx in unmatched_dets:
                    unmatched_dets.remove(d_idx)
                if t_idx in unmatched_trks:
                    unmatched_trks.remove(t_idx)
                iou_matrix[d_idx, :] = -1.0
                iou_matrix[:, t_idx] = -1.0

        # Update matched trackers
        for d_idx, t_idx in matched_indices:
            det = detections[d_idx]
            dt = max(0.01, now - self.trackers[t_idx].last_update_time)
            self.trackers[t_idx].update(det["box"], det["confidence"], dt)

        # Create new trackers for unmatched detections
        for d_idx in unmatched_dets:
            det = detections[d_idx]
            trk = KalmanBoxTracker(det["box"], det["class"], det["confidence"])
            self.trackers.append(trk)

        # Remove dead trackers
        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        # Format output detections
        return self.get_current_tracks()

    def get_current_tracks(self) -> List[Dict[str, Any]]:
        results = []
        for trk in self.trackers:
            if trk.time_since_update <= 3:  # Only output recent tracks
                prefix = self._get_prefix(trk.class_name)
                track_id = f"{self.camera_id}:{prefix}-{trk.id:03d}"
                results.append({
                    "class": trk.class_name,
                    "confidence": round(trk.confidence, 2),
                    "box": [round(v, 1) for v in trk.get_state()],
                    "track_id": track_id,
                    "trajectory": list(trk.history)
                })
        return results

    @staticmethod
    def _get_prefix(class_name: str) -> str:
        prefix_map = {
            "person": "P", "car": "V", "motorcycle": "V", "bus": "V", "truck": "V",
            "drone": "D", "weapon": "W", "knife": "W", "gun": "W",
            "backpack": "I", "suitcase": "I", "handbag": "I", "cell phone": "I"
        }
        return prefix_map.get(class_name.lower(), "U")


class TrackingService:
    """Singleton tracking manager maintaining independent trackers per camera."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.trackers = {}
        return cls._instance

    def get_tracker(self, camera_id: str) -> CameraTracker:
        if camera_id not in self.trackers:
            self.trackers[camera_id] = CameraTracker(camera_id)
        return self.trackers[camera_id]

    def reset_camera(self, camera_id: str):
        if camera_id in self.trackers:
            self.trackers[camera_id].reset()

tracking_service = TrackingService()
