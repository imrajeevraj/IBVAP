# IBVAP — AI Models & Neural Network Weights Specification

## 1. Intentional Repository Exclusion
Pretrained deep learning weights (`*.pt`, `*.pth`, `*.onnx`, `*.engine`, `*.safetensors`) are **strictly excluded from this GitHub repository**. 

Weights are binary artifacts that should be downloaded or built locally from authoritative checkpoints to ensure supply-chain integrity.

---

## 2. Models Used in IBVAP

IBVAP employs a dual-model real-time computer vision pipeline:

| Model Role | Checkpoint Name | Framework / Architecture | Purpose | Status | Expected Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Baseline Detector** | `yolov8n.pt` / `yolov8n.onnx` | Ultralytics YOLOv8 Nano | High-speed edge detection of persons, vehicles, animals | **Required** | `./yolov8n.pt` or `models/yolov8n.pt` |
| **Enhanced Baseline Detector** | `yolo11n.pt` | Ultralytics YOLOv11 Nano | Low-power optimized edge inference | **Optional** | `./yolo11n.pt` or `models/yolo11n.pt` |
| **Specialized Threat Detector** | `border_threat_yolo.pt` | Fine-tuned YOLO on border threats | Micro-drone, weapon, and contraband detection | **Optional** | `./border_threat_yolo.pt` or `models/` |
| **Biometric Face Re-ID** | `buffalo_l` | InsightFace (ArcFace ResNet50 + 2D/3D landmarks) | 512-dim facial embedding vector extraction for watchlists | **Optional** | `app/data/insightface/models/buffalo_l/` |

---

## 3. Automated Download & Acquisition

### 3.1 Primary YOLO Detectors
Ultralytics automatically downloads official YOLO checkpoints upon first invocation:
```python
from ultralytics import YOLO

# Automatically fetches official Ultralytics weights if not present locally
model = YOLO("yolov8n.pt")
```

To export to ONNX for TensorRT acceleration:
```bash
python backend/scripts/export_onnx.py --model yolov8n.pt --format onnx
```

### 3.2 InsightFace Biometric Model Pack (`buffalo_l`)
InsightFace models are fetched via `insightface.app.FaceAnalysis`:
```python
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l", root="app/data/insightface")
app.prepare(ctx_id=0, det_size=(640, 640))
```
- **License:** InsightFace models are subject to the InsightFace research license (non-commercial research and testing).
- **Official Source:** [InsightFace Model Zoo](https://github.com/deepinsight/insightface)

---

## 4. Cryptographic SHA-256 Verification Procedure

To safeguard against corrupted or tampered model weights in production border deployments, IBVAP validates model checksums against `.env` configuration:

```bash
# In .env:
MODEL_PATH=yolov8n.pt
MODEL_SHA256=F59B3D833E2FF32E194B5BB8E08D211DC7C5BDF144B90D2C8412C47CCFC83B36
```

To compute the SHA-256 hash of a local model weight file:
```powershell
# Windows PowerShell:
Get-FileHash -Algorithm SHA256 yolov8n.pt

# Linux / macOS:
sha256sum yolov8n.pt
```

The startup routine validates that the calculated hash matches the expected hash before allocating GPU VRAM.
