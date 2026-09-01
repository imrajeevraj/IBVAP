import os
import sys
import time
import psutil
import torch

sys.stdout.reconfigure(line_buffering=True)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.services.camera_manager import camera_manager
from backend.app.services.ai_scheduler import ai_scheduler

def test_live():
    print("Starting all camera streams...", flush=True)
    camera_manager.start_all()
    
    print("Streams started. Running 10-second live test across all 4 cameras...", flush=True)
    for i in range(10):
        time.sleep(1.0)
        line = f"Sec {i+1:02d}: "
        for cam_id in ["CAM-001", "CAM-002", "CAM-003", "CAM-004"]:
            st = camera_manager.get_camera_status(cam_id)
            metrics = ai_scheduler.get_metrics(cam_id)
            fps = st["fps"]
            ai_fps = metrics.get("detector_fps", 0.0)
            inf_ms = metrics.get("inference_ms", 0.0)
            dets = len(st["detections"])
            line += f"[{cam_id} FPS={fps:.1f} AI={ai_fps:.1f} Inf={inf_ms:.1f}ms Dets={dets}] "
        print(line, flush=True)

    print("\nStopping camera streams...", flush=True)
    camera_manager.stop_all()
    print("Live test completed successfully!", flush=True)

if __name__ == "__main__":
    test_live()
