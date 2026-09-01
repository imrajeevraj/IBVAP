import os
import sys
from ultralytics import YOLO

# Ensure we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def main():
    model_path = settings.MODEL_PATH
    
    # Locate model relative to root
    if not os.path.isfile(model_path):
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", settings.MODEL_PATH))
        if not os.path.isfile(model_path):
            print(f"Model not found: {settings.MODEL_PATH}")
            return
    
    print(f"Loading {model_path} for ONNX export...")
    model = YOLO(model_path)
    
    print("Exporting to ONNX (FP16)...")
    exported_path = model.export(format="onnx", half=True, dynamic=False)
    print(f"Successfully exported to {exported_path}")

if __name__ == "__main__":
    main()
