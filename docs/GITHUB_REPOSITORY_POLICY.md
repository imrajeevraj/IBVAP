# IBVAP — GitHub Repository Governance & Inclusion Policy

## 1. Scope & Objective
This document governs the contribution, staging, and version control policies for the **IBVAP (Intelligent Border Visual Analytics Platform)** repository. 

IBVAP is an enterprise software platform designed for border surveillance intelligence under Smart India Hackathon 2026 (Problem Statement ID: **SIH26187**). The primary objective of the public GitHub repository is to track and distribute **production software, automation scripts, test suites, architecture schemas, database migrations, and benchmark methodologies**.

Under no circumstances should large binary runtime data, proprietary video datasets, biometric embeddings, surveillance evidence, or neural network weights be checked into the Git version control system.

---

## 2. File Classification Matrix

All files within the IBVAP project boundary are classified into the following 12 operational categories:

| Category | Description | Policy | Destination / Handling |
| :--- | :--- | :--- | :--- |
| **A. SOURCE** | Application code in backend, frontend, scripts | **COMMIT** | Git tracking (`backend/app`, `frontend/src`, `scripts`) |
| **B. TEST** | Unit, integration, and security test suites | **COMMIT** | Git tracking (`backend/tests/`, `pytest.ini`) |
| **C. DOCUMENTATION** | Architectural blueprints, setup guides, policies | **COMMIT** | Git tracking (`docs/`, `README.md`, `SYSTEM_ARCHITECTURE.md`) |
| **D. CONFIG TEMPLATE**| Sanitized YAML configuration files with defaults | **COMMIT** | Git tracking (`configs/*.yaml`, `.env.example`) |
| **E. MIGRATION** | Alembic database migration scripts & schemas | **COMMIT** | Git tracking (`backend/alembic/versions/`) |
| **F. CI/CD** | Automated GitHub Actions workflow pipelines | **COMMIT** | Git tracking (`.github/workflows/ci.yml`) |
| **G. REPRODUCIBILITY**| Checksums, dataset manifests, labels | **COMMIT** | Git tracking (`benchmark/checksums/`, `benchmark/labels/`) |
| **H. LOCAL RUNTIME** | Generated logs, temporary SQLite tables, sessions | **IGNORE** | Local storage only (`ibvap.db`, `logs/`, `output/`) |
| **I. LARGE DATASET** | Raw surveillance footage (e.g. VIRAT, PETS2009) | **IGNORE** | Local storage (`data/videos/virat/`) or external storage |
| **J. MODEL WEIGHTS** | Pretrained neural weights (`.pt`, `.onnx`, `.engine`) | **IGNORE** | Local storage (`models/`, `app/data/insightface/`) or S3/GCS |
| **K. EVIDENCE** | Snapshots, incident crops, alert video clips | **IGNORE** | Local storage (`data/evidence/`, `snapshots/`) |
| **L. SECRETS** | API keys, database credentials, JWT secrets, keys | **NEVER COMMIT** | Local environment files (`.env`, credentials vault) |

---

## 3. Strict Exclusion Boundaries

### 3.1 Surveillance Videos & Media
- **Prohibited Extensions:** `*.mp4`, `*.avi`, `*.mov`, `*.mkv`, `*.webm`, `*.mts`, `*.m2ts`, `*.ts`, `*.flv`
- **Prohibited Directories:** `data/videos/`, `recordings/`, `benchmark/images/`, `benchmark/rfdetr_dataset/`
- **Rationale:** Video files rapidly bloat repository history, breach GitHub's 100 MB per-file hard limit, and may violate data governance, privacy, or dataset licensing agreements.

### 3.2 Databases & Storage Dumps
- **Prohibited Extensions:** `*.db`, `*.sqlite`, `*.sqlite3`, `*.db-journal`, `*.db-wal`, `*.db-shm`, `*.dump`, `*.backup`, `*.sql`
- **Prohibited Files:** `ibvap.db`, `backend/empty.db`, `data/database/*`
- **Rationale:** Live databases contain ephemeral state, operator session details, and potential PII. Schemas must be represented strictly through code-driven Alembic migrations.

### 3.3 AI Model Weights & Checkpoints
- **Prohibited Extensions:** `*.pt`, `*.pth`, `*.onnx`, `*.engine`, `*.weights`, `*.ckpt`, `*.safetensors`, `*.bin`, `*.tflite`
- **Prohibited Directories:** `models/*.pt`, `app/data/insightface/models/`, `backend/data/`
- **Rationale:** Deep learning weights are binary artifacts that belong in artifact registries, model zoos, or object storage (Hugging Face, Google Cloud Storage, AWS S3).

### 3.4 Cryptographic Secrets & Environment Configuration
- **Prohibited Files:** `.env`, `.env.local`, `*.pem`, `*.key`, `*.cert`, `credentials.json`
- **Mandated Alternative:** `.env.example` containing standardized placeholder values.
- **Scanning Protocol:** Pre-commit hooks and CI Bandit security scans prevent accidental credential exposure.

---

## 4. Enforcement & Audit Workflow

1. **Pre-Staging Inspection:** Developers must run `git status` and verify all unstaged assets prior to staging.
2. **Cache Untracking:** If an excluded file was inadvertently tracked previously, it must be untracked using `git rm --cached <path>` without deleting local files.
3. **Continuous Integration Verification:** GitHub Actions verifies that no build artifacts, binary models, or credentials exist in the committed tree.
