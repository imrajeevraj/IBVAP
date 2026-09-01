import os
import sys
import time

sys.stdout.reconfigure(line_buffering=True)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

print("1. Python starting...", flush=True)

print("2. Importing torch...", flush=True)
import torch
print(f"   Torch version: {torch.__version__}, CUDA: {torch.cuda.is_available()}", flush=True)

print("3. Importing cv2...", flush=True)
import cv2
print(f"   cv2 version: {cv2.__version__}", flush=True)

print("4. Importing database SessionLocal...", flush=True)
from backend.app.core.database import SessionLocal
print("   SessionLocal imported.", flush=True)

print("5. Importing models...", flush=True)
from backend.app.models.camera import Camera
print("   Camera model imported.", flush=True)

print("6. Importing detection_service...", flush=True)
from backend.app.services.detection_service import detection_service
print("   detection_service imported.", flush=True)

print("7. Importing tracking_service...", flush=True)
from backend.app.services.tracking_service import tracking_service
print("   tracking_service imported.", flush=True)

print("8. Importing ai_scheduler...", flush=True)
from backend.app.services.ai_scheduler import ai_scheduler
print("   ai_scheduler imported.", flush=True)

print("9. Importing camera_manager...", flush=True)
from backend.app.services.camera_manager import camera_manager
print("   camera_manager imported.", flush=True)

print("10. Testing database query...", flush=True)
db = SessionLocal()
try:
    cams = db.query(Camera).all()
    print(f"   Database query successful, found {len(cams)} cameras.", flush=True)
finally:
    db.close()

print("ALL IMPORTS & DB TESTS PASSED!", flush=True)
