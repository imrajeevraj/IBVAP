# IBVAP — GitHub Upload & Repository Cleanliness Report

## Executive Summary
This document provides the formal audit and verification certification for the GitHub repository upload of **IBVAP (Intelligent Border Visual Analytics Platform)**, developed under Smart India Hackathon 2026 for Problem Statement ID **SIH26187** (Ministry of Home Affairs / Sashastra Seema Bal).

---

## 1. Repository & Branch Metadata

- **Repository Name:** `IBVAP`
- **Target Remote:** `https://github.com/imrajeevraj/IBVAP.git`
- **Target Branch:** `main`
- **Base Remote Commit:** `d8a39dc` (Remote GitHub head containing initial single markdown fixture)
- **New Release Commit:** Clean fast-forward commit introducing core software and architecture

---

## 2. Inclusion & Exclusion Audit Summary

| Audit Item | Status | Verified Details |
| :--- | :--- | :--- |
| **Surveillance Videos Excluded** | **PASS (YES)** | `data/videos/virat/*.mp4` (4.14 GB) excluded; `data/videos/README.md` committed |
| **Databases Excluded** | **PASS (YES)** | `ibvap.db` (3.5 MB), `empty.db` excluded; Alembic migrations committed |
| **AI Model Weights Excluded** | **PASS (YES)** | `*.pt`, `*.onnx`, `buffalo_l` (500+ MB) excluded; `models/README.md` committed |
| **Forensic Evidence Excluded** | **PASS (YES)** | `data/evidence/*` (thousands of clips/snapshots) excluded; README committed |
| **Secrets & Keys Excluded** | **PASS (YES)** | `.env` untracked & uncommitted; sanitized `.env.example` committed |
| **Python Virtual Environments** | **PASS (YES)** | `.venv/`, `__pycache__/`, `.pytest_cache/` excluded |
| **Frontend Dependencies & Builds**| **PASS (YES)** | `node_modules/`, `frontend/dist/` excluded; `package-lock.json` committed |
| **Benchmark Datasets Excluded** | **PASS (YES)** | `benchmark/images/` (213 MB), `rfdetr_dataset/` (426 MB) excluded |
| **Ground Truth Metadata Tracked**| **PASS (YES)** | Checksum manifests & 330 annotation `.txt` files tracked in `benchmark/` |

---

## 3. Large File & Secret Scans

### 3.1 Largest Committed Files in Release
All committed objects are verified to be under 100 KB:
1. `frontend/package-lock.json` — 99.8 KB (Dependency lockfile)
2. `README.md` — 51.0 KB (Comprehensive project documentation)
3. `frontend/src/index.css` — 41.9 KB (Design system & styling tokens)
4. `backend/app/services/risk_engine.py` — 17.5 KB (Risk scoring engine)
5. `benchmark/checksums/images.sha256` — 16.4 KB (Reproducibility manifest)
6. `benchmark/checksums/labels.sha256` — 16.4 KB (Reproducibility manifest)

**Result:** Zero files exceeding 100 KB. Fully compliant with GitHub's 100 MB hard ceiling and 50 MB recommendation.

### 3.2 Secret Scan Audit
- Scanned all configuration templates (`configs/*.yaml`), Dockerfiles, and `.env.example`.
- Verified zero real API tokens, private RSA/ECDSA keys, live passwords, or camera credentials exist in the Git index.
- Sanitized placeholders (`CHANGE_ME`, `replace-with-at-least-32-random-characters`) enforced throughout.

---

## 4. Test & Build Verification

- **Frontend Production Build:** **PASS**
  - Executed `npm --prefix frontend run build`
  - Vite v8.2.2 + TypeScript compilation succeeded (`✓ 1542 modules transformed`, bundle generated in `dist/`).
- **NPM Vulnerability Audit:** **PASS**
  - `npm audit` returned 0 vulnerabilities.
- **Backend Test Suite (Pytest):** **DOCUMENTED**
  - 9 tests passed.
  - 2 test failures noted:
    1. `test_camera_stream_thread_success`: Expected a local video file (`data/videos/phase1_test.mp4`), which was excluded per data policy.
    2. `test_system_health_route_has_single_api_prefix`: Route prefix composition expectation.
  - Source code preserved without modification per safety guidelines.

---

## 5. Local Data Safety Guarantee

All local video files, database records, test runs, and deep learning model weights remain intact on disk at:
- `c:\Users\rajee\Downloads\SIH 2026\IBVAP\data\videos\virat\`
- `c:\Users\rajee\Downloads\SIH 2026\IBVAP\data\evidence\`
- `c:\Users\rajee\Downloads\SIH 2026\IBVAP\ibvap.db`
- `c:\Users\rajee\Downloads\SIH 2026\IBVAP\yolov8n.pt`, `yolo11n.pt`, `border_threat_yolo.pt`
- `c:\Users\rajee\Downloads\SIH 2026\IBVAP\app\data\insightface\`
Zero local files were deleted during repository preparation.

---

## 6. Release Verification & Push Execution

- **Committed Files:** 471 files
- **Total Release Payload:** ~700 KB (Zero files exceeding 100 KB)
- **Commit Hash:** `05abc93d0a719dfe9492784c189a61d914e03e8a`
- **Parent Commit:** `d8a39dcff5cb528fd2f3866c1bfc4d8d946d312f` (`origin/main`)
- **Fast-Forward Compatible:** **YES (Clean single-step fast-forward)**
- **Push Command:**
  ```bash
  git push origin main
  ```

