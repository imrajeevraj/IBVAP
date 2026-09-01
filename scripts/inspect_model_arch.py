import os
import sys
import torch

sys.stdout.reconfigure(line_buffering=True)

from ultralytics import YOLO

for name in ["border_threat_yolo.pt", "yolo11n.pt", "yolov8n.pt"]:
    if not os.path.exists(name): continue
    m = YOLO(name)
    params = sum(p.numel() for p in m.model.parameters())
    print(f"Model: {name}")
    print(f"  Type: {type(m.model).__name__}")
    print(f"  Total Parameters: {params:,}")
    print(f"  Number of layers: {len(list(m.model.modules()))}")
    if hasattr(m.model, 'yaml'):
        print(f"  YAML config: {m.model.yaml.get('backbone', '')}")
