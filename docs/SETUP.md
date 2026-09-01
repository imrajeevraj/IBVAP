# IBVAP — Local Developer & Deployment Setup Guide

This guide provides step-by-step instructions to clone, configure, install dependencies, and run the **IBVAP (Intelligent Border Visual Analytics Platform)** in a clean local development environment.

---

## 1. Prerequisites

- **Operating System:** Ubuntu 22.04 LTS / Debian 12 / Windows 11 with WSL2
- **Python:** Version 3.11+
- **Node.js:** Version 20+ LTS (with npm)
- **Containerization (Optional for Production):** Docker 24+ & Docker Compose v2+
- **GPU Acceleration (Recommended):** NVIDIA GPU with CUDA 12+ & cuDNN (optional: runs on CPU fallback)

---

## 2. Clone Repository

```bash
git clone https://github.com/imrajeevraj/IBVAP.git
cd IBVAP
```

---

## 3. Environment Configuration

Copy the sanitized template file to configure your local runtime environment:

```bash
cp .env.example .env
```

Review `.env` and set appropriate local parameters:
```ini
DATABASE_URL=sqlite:///./ibvap.db
JWT_SECRET=replace-with-at-least-32-random-characters
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-secure-password
API_PORT=8000
API_HOST=0.0.0.0
MODEL_PATH=yolov8n.pt
```

> [!WARNING]
> Never commit `.env` to Git. It is automatically ignored by `.gitignore`.

---

## 4. Backend Setup (Python 3.11)

### 4.1 Create & Activate Virtual Environment

```bash
# Linux / macOS:
python3.11 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4.2 Install Python Dependencies

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4.3 Initialize Database & Apply Migrations

```bash
cd backend
alembic upgrade head
cd ..
```

This creates a fresh local database with all required tables (cameras, events, rules, watchlist).

---

## 5. AI Models Setup

Download the primary lightweight detection weights (YOLOv8 Nano):

```bash
# Automated fetch via Ultralytics CLI
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

Verify that `yolov8n.pt` is present in the project root. For detailed instructions on optional specialized threat weights and InsightFace biometric models, see [`models/README.md`](../models/README.md).

---

## 6. Frontend Setup (React 19 / TypeScript)

### 6.1 Install Node Dependencies

```bash
cd frontend
npm ci
```

### 6.2 Build & Validate Production Bundle

```bash
npm run build
```

---

## 7. Running the Platform Locally

You can launch both backend and frontend concurrently using the provided launcher:

```bash
# From repository root:
npm install
npm run dev
```

Or run them in separate terminal windows:

### Terminal 1: Backend API Server
```bash
# Make sure .venv is activated
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

### Terminal 2: Frontend Tactical Dashboard
```bash
cd frontend
npm run dev
```
- Tactical Command Dashboard: `http://localhost:5173/`

---

## 8. Running Automated Test Suite

```bash
# Backend pytest suite
pytest backend/tests/ -v

# Frontend TypeScript check
npm --prefix frontend run build
```
