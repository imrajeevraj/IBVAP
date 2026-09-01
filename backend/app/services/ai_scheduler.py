import time
import threading
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
import numpy as np

from backend.app.services.detection_service import detection_service
from backend.app.services.tracking_service import tracking_service
from backend.app.services.border_rules_service import border_rules_service
from backend.app.services.anpr.anpr_service import anpr_service
from backend.app.services.behavior_service import behavior_service
from backend.app.services.face_service import face_service

logger = logging.getLogger("AIScheduler")

class CameraAIState:
    """State and metrics tracking for a single camera stream."""
    def __init__(self, camera_id: str, target_ai_fps: float = 8.0):
        self.camera_id = camera_id
        self.target_ai_fps = target_ai_fps
        self.min_interval = 1.0 / target_ai_fps
        self.last_inference_time = 0.0
        
        # Bounded buffer: stores only the latest frame
        self.latest_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        self.has_new_frame = False
        
        # Current active tracked detections
        self.current_detections: List[Dict[str, Any]] = []
        self.detections_lock = threading.Lock()
        
        # Stage Profiling Metrics
        self.capture_ms = 0.0
        self.preprocess_ms = 0.0
        self.inference_ms = 0.0
        self.postprocess_ms = 0.0
        self.tracking_ms = 0.0
        self.zone_ms = 0.0
        self.event_ms = 0.0
        self.total_pipeline_ms = 0.0
        
        self.detector_fps = 0.0
        self.inference_count = 0
        self.fps_timer = time.time()
        self.last_ai_result_at: Optional[datetime] = None

    def submit_frame(self, frame: np.ndarray, capture_ms: float = 0.0):
        """Latest-Frame-Wins submission: immediately overwrites older unconsumed frames."""
        with self.frame_lock:
            self.latest_frame = frame
            self.has_new_frame = True
            self.capture_ms = capture_ms

    def get_latest_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            if self.has_new_frame and self.latest_frame is not None:
                self.has_new_frame = False
                return self.latest_frame
            return None

    def update_metrics(self, inference_ms: float, tracking_ms: float, zone_ms: float, total_ms: float):
        self.inference_ms = round(inference_ms, 1)
        self.tracking_ms = round(tracking_ms, 1)
        self.zone_ms = round(zone_ms, 1)
        self.total_pipeline_ms = round(total_ms, 1)
        self.last_ai_result_at = datetime.utcnow()
        self.inference_count += 1
        
        now = time.time()
        elapsed = now - self.fps_timer
        if elapsed >= 2.0:
            self.detector_fps = round(self.inference_count / elapsed, 1)
            self.inference_count = 0
            self.fps_timer = now


class AIScheduler:
    """
    Central asynchronous multi-camera AI scheduler.
    Pulls latest frames from camera buffers, runs centralized GPU inference,
    updates per-camera trackers, and evaluates security rules without blocking video playback.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cameras: Dict[str, CameraAIState] = {}
            cls._instance.running = False
            cls._instance.worker_thread = None
            cls._instance.lock = threading.Lock()
        return cls._instance

    def register_camera(self, camera_id: str, target_ai_fps: float = 8.0):
        with self.lock:
            if camera_id not in self.cameras:
                self.cameras[camera_id] = CameraAIState(camera_id, target_ai_fps)
                logger.info(f"Registered camera {camera_id} with target AI rate: {target_ai_fps} FPS")

    def unregister_camera(self, camera_id: str):
        with self.lock:
            if camera_id in self.cameras:
                del self.cameras[camera_id]
                logger.info(f"Unregistered camera {camera_id}")

    def submit_frame(self, camera_id: str, frame: np.ndarray, capture_ms: float = 0.0):
        if camera_id in self.cameras:
            self.cameras[camera_id].submit_frame(frame, capture_ms)

    def get_detections(self, camera_id: str) -> List[Dict[str, Any]]:
        state = self.cameras.get(camera_id)
        if state:
            with state.detections_lock:
                return list(state.current_detections)
        return []

    def get_metrics(self, camera_id: str) -> Dict[str, Any]:
        state = self.cameras.get(camera_id)
        if state:
            return {
                "detector_fps": state.detector_fps,
                "inference_ms": state.inference_ms,
                "tracking_ms": state.tracking_ms,
                "zone_ms": state.zone_ms,
                "total_pipeline_ms": state.total_pipeline_ms,
                "last_ai_result_at": state.last_ai_result_at,
                "age_seconds": round((datetime.utcnow() - state.last_ai_result_at).total_seconds(), 1) if state.last_ai_result_at else None
            }
        return {}

    def start(self):
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, name="Central-AI-Worker", daemon=True)
        self.worker_thread.start()
        logger.info("Central AI Worker Thread started.")

    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def _worker_loop(self):
        """Continuous scheduling loop across all active cameras."""
        log_timer = time.time()
        
        while self.running:
            now = time.time()
            work_done = False

            with self.lock:
                camera_states = list(self.cameras.values())

            for state in camera_states:
                # Rate-limiting check: only process if time since last inference exceeds min_interval
                if now - state.last_inference_time < state.min_interval:
                    continue

                frame = state.get_latest_frame()
                if frame is None:
                    continue

                work_done = True
                state.last_inference_time = now
                pipe_start = time.perf_counter()

                try:
                    # 1. Detection Forward Pass
                    raw_dets, inference_ms = detection_service.predict_raw(frame, imgsz=640)

                    # 2. Tracking Association
                    t0_track = time.perf_counter()
                    tracker = tracking_service.get_tracker(state.camera_id)
                    tracked_dets = tracker.update_detections(raw_dets)
                    tracking_ms = (time.perf_counter() - t0_track) * 1000.0

                    with state.detections_lock:
                        state.current_detections = tracked_dets

                    # 3. Security Rules & Behavioral Evaluation
                    t0_zone = time.perf_counter()
                    border_rules_service.process_detections(state.camera_id, tracked_dets, frame)
                    anpr_service.process_frame(frame, state.camera_id, tracked_dets)
                    behavior_service.process_detections(state.camera_id, tracked_dets, frame)
                    face_service.process_detections(state.camera_id, tracked_dets, frame)
                    zone_ms = (time.perf_counter() - t0_zone) * 1000.0

                    total_pipe_ms = (time.perf_counter() - pipe_start) * 1000.0
                    state.update_metrics(inference_ms, tracking_ms, zone_ms, total_pipe_ms)

                except Exception as exc:
                    logger.error(f"[{state.camera_id}] Error in AI pipeline: {exc}", exc_info=False)

            # Periodic structured logging every 10 seconds
            if now - log_timer >= 10.0:
                log_timer = now
                summary = []
                for state in camera_states:
                    summary.append(f"[{state.camera_id}] AI_FPS={state.detector_fps:.1f} Inf={state.inference_ms:.1f}ms Trk={state.tracking_ms:.1f}ms Tot={state.total_pipeline_ms:.1f}ms")
                if summary:
                    logger.info("AI PIPELINE TELEMETRY: " + " | ".join(summary))

            # Small sleep to prevent 100% CPU spinning when idle
            if not work_done:
                time.sleep(0.005)

ai_scheduler = AIScheduler()
