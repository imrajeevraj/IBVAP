# IBVAP — Forensic Evidence Storage & Chain-of-Custody

## 1. Intentional Repository Exclusion
Surveillance evidence artifacts generated during runtime are **strictly excluded from this GitHub repository**:
- Alert snapshot frames (`*.jpg`, `*.png`)
- High-resolution vehicle license plate crops
- Biometric facial crops and candidate extracts
- Intrusion event video clips (`*.mp4`)
- Forensic audit packages

---

## 2. Evidence Architecture & Chain-of-Custody

In operational border deployments, IBVAP generates cryptographically verifiable evidence packages whenever an intrusion, tripwire violation, or watchlist match occurs:

```
data/evidence/
├── README.md                  # (This guidance file - tracked in Git)
├── CAM-001/                   # Camera specific event directory
│   ├── event_1001.mp4         # 10-second rolling buffer video clip (pre/post incident)
│   ├── event_1001_frame.jpg   # High-resolution keyframe at moment of breach
│   ├── event_1001_plate.jpg   # ANPR vehicle crop
│   └── event_1001_face.jpg    # Facial detection crop
└── CAM-002/
```

---

## 3. Cryptographic Integrity

Each evidence event stored by `backend/app/services/evidence_service.py` is hashed with **SHA-256**:
1. At the instant of alert generation, the raw frame buffer is written to disk.
2. The SHA-256 cryptographic digest of the file is calculated and recorded directly into the `events` database record.
3. The cryptographic hash ensures that footage presented during military inquiry or legal prosecution cannot be repudiated or tampered with after the incident.
