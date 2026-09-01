"""Lightweight rolling evidence capture for the demonstration workflow."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
import threading
import time
from typing import Deque

import cv2
import numpy as np

from backend.app.core.database import SessionLocal
from backend.app.models.event import SecurityEvent

logger = logging.getLogger("EvidenceService")


@dataclass
class CaptureJob:
    camera_id: str
    event_id: int
    started_at: float
    frames: list[np.ndarray] = field(default_factory=list)


class EvidenceService:
    """Keeps five seconds of sampled frames and records seven seconds after an alert.

    The resulting clip is approximately 12 seconds at 5 FPS, which keeps the
    demo responsive without retaining a high-resolution recording of every feed.
    """

    SAMPLE_INTERVAL_SECONDS = 0.2
    PRE_EVENT_SECONDS = 5
    POST_EVENT_SECONDS = 7
    EVIDENCE_FPS = 5
    MAX_FRAME_WIDTH = 960

    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[3] / "data" / "evidence"
        self.buffers: dict[str, Deque[np.ndarray]] = defaultdict(
            lambda: deque(maxlen=self.PRE_EVENT_SECONDS * self.EVIDENCE_FPS)
        )
        self.jobs: dict[int, CaptureJob] = {}
        self.last_sample_at: dict[str, float] = {}
        self.lock = threading.Lock()
        
        # Start cleanup daemon
        threading.Thread(target=self._cleanup_daemon, daemon=True).start()

    def _cleanup_daemon(self) -> None:
        """Periodically remove evidence older than 7 days."""
        while True:
            try:
                if self.root.exists():
                    now = time.time()
                    for f in self.root.glob("**/*"):
                        if f.is_file() and (now - f.stat().st_mtime) > 7 * 86400:
                            f.unlink(missing_ok=True)
            except Exception as e:
                logger.error("Evidence cleanup failed: %s", e)
            time.sleep(3600)  # Check every hour

    def _scaled_frame(self, frame: np.ndarray) -> np.ndarray:
        height, width = frame.shape[:2]
        if width <= self.MAX_FRAME_WIDTH:
            return frame.copy()
        scale = self.MAX_FRAME_WIDTH / width
        return cv2.resize(frame, (self.MAX_FRAME_WIDTH, int(height * scale)))

    def record_frame(self, camera_id: str, frame: np.ndarray) -> None:
        """Sample a frame and advance any active post-event capture jobs."""
        now = time.monotonic()
        if now - self.last_sample_at.get(camera_id, 0) < self.SAMPLE_INTERVAL_SECONDS:
            return
        self.last_sample_at[camera_id] = now
        sampled = self._scaled_frame(frame)
        finished: list[CaptureJob] = []
        with self.lock:
            self.buffers[camera_id].append(sampled)
            for job in list(self.jobs.values()):
                if job.camera_id != camera_id:
                    continue
                job.frames.append(sampled.copy())
                if now - job.started_at >= self.POST_EVENT_SECONDS:
                    finished.append(job)
                    del self.jobs[job.event_id]
        for job in finished:
            threading.Thread(target=self._write_clip, args=(job,), daemon=True).start()

    def capture_event(self, camera_id: str, event_id: int, frame: np.ndarray | None) -> tuple[str | None, str | None]:
        """Write a snapshot immediately and start a rolling post-event clip."""
        folder = self.root / camera_id
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S_%f")
        snapshot_rel = f"data/evidence/{camera_id}/event_{event_id}_{stamp}.jpg"
        snapshot_abs = self.root.parents[1] / snapshot_rel

        image = self._scaled_frame(frame) if frame is not None else None
        if image is None:
            with self.lock:
                if self.buffers[camera_id]:
                    image = self.buffers[camera_id][-1].copy()
        if image is not None:
            cv2.imwrite(str(snapshot_abs), image, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            import hashlib
            from backend.app.models.event import Evidence
            h = hashlib.sha256()
            with open(str(snapshot_abs), 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
                    
            db = SessionLocal()
            try:
                ev = Evidence(
                    event_id=event_id,
                    camera_id=camera_id,
                    integrity_hash=h.hexdigest(),
                    file_path=snapshot_rel,
                    data_origin="LIVE"
                )
                db.add(ev)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to record evidence: {e}")
                if db: db.rollback()
            finally:
                if db: db.close()
        else:
            snapshot_rel = None

        with self.lock:
            frames = [item.copy() for item in self.buffers[camera_id]]
            if image is not None:
                frames.append(image.copy())
            self.jobs[event_id] = CaptureJob(
                camera_id=camera_id,
                event_id=event_id,
                started_at=time.monotonic(),
                frames=frames,
            )
        return snapshot_rel, None

    def _write_clip(self, job: CaptureJob) -> None:
        if len(job.frames) < 2:
            return
        folder = self.root / job.camera_id
        folder.mkdir(parents=True, exist_ok=True)
        clip_rel = f"data/evidence/{job.camera_id}/event_{job.event_id}.mp4"
        clip_abs = self.root.parents[1] / clip_rel
        height, width = job.frames[0].shape[:2]
        writer = cv2.VideoWriter(str(clip_abs), cv2.VideoWriter_fourcc(*"mp4v"), self.EVIDENCE_FPS, (width, height))
        try:
            for frame in job.frames:
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))
                writer.write(frame)
        finally:
            writer.release()
            
        import hashlib
        from backend.app.models.event import Evidence
        h = hashlib.sha256()
        with open(str(clip_abs), 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)

        db = SessionLocal()
        try:
            event = db.query(SecurityEvent).filter(SecurityEvent.id == job.event_id).first()
            if event:
                event.video_clip_path = clip_rel
                ev = Evidence(
                    event_id=job.event_id,
                    camera_id=job.camera_id,
                    integrity_hash=h.hexdigest(),
                    file_path=clip_rel,
                    data_origin="LIVE"
                )
                db.add(ev)
                db.commit()
        except Exception:
            db.rollback()
            logger.exception("Unable to persist evidence clip for event %s", job.event_id)
        finally:
            db.close()


evidence_service = EvidenceService()
