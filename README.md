# IBVAP — Intelligent Border Visual Analytics Platform

[![SIH 2026](https://img.shields.io/badge/SIH%202026-SIH26187-blue.svg)](https://www.sih.gov.in/)
[![Ministry](https://img.shields.io/badge/Ministry-Home%20Affairs-003366.svg)](https://www.mha.gov.in/)
[![Department](https://img.shields.io/badge/Department-SSB%20%7C%20Police%20II-orange.svg)](https://ssb.gov.in/)
[![CI Pipeline](https://img.shields.io/badge/CI-Automated%20Verification-green.svg)](.github/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20TypeScript-61DAFB.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED.svg)](docker-compose.yml)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016%20%2B%20pgvector-336791.svg)](https://www.postgresql.org/)

> [!IMPORTANT]
> **Repository Governance & Cleanliness Notice:**
> In accordance with repository policies and data governance standards, **large surveillance video files, live runtime database files, generated forensic evidence clips/snapshots, and binary AI model weights are strictly excluded from this GitHub repository**. 
> - **Video Data:** See [`data/videos/README.md`](data/videos/README.md) for local video placement and VIRAT dataset acquisition instructions.
> - **Database:** See [`data/database/README.md`](data/database/README.md) for Alembic migration instructions.
> - **AI Models:** See [`models/README.md`](models/README.md) for checkpoint download guidelines and SHA-256 verification.
> - **Benchmark:** See [`benchmark/README.md`](benchmark/README.md) for dataset methodology and validation.
> - **Developer Setup:** See [`docs/SETUP.md`](docs/SETUP.md) for a reproducible local development environment guide.
> - **Repository Policy:** Full classification rules are in [`docs/GITHUB_REPOSITORY_POLICY.md`](docs/GITHUB_REPOSITORY_POLICY.md).

---

## 1. Executive Summary

**IBVAP (Intelligent Border Visual Analytics Platform)** is an enterprise-grade, software-defined computer vision and tactical command-and-control platform engineered to transform standard legacy border surveillance cameras (CCTV, PTZ, thermal, RTSP feeds) into proactive real-time intelligence assets. Built specifically for the **Ministry of Home Affairs (Sashastra Seema Bal / Police II Division)** under **Smart India Hackathon 2026 (Problem Statement SIH26187)**, IBVAP operates at Border Outposts (BOPs) and sector command headquarters to automate perimeter breach detection, virtual fence crossings, high-speed vehicle monitoring, multi-frame license plate recognition (ANPR), and face watchlist screening. By decoupling high-frame-rate video ingestion from asynchronous multi-camera AI inference, enforcing strict cryptographic evidence integrity (SHA-256), and using camera-qualified trajectory tracking, IBVAP delivers sub-100ms situational awareness without requiring costly proprietary sensor overhauls.

---

## 2. SIH 2026 Problem Statement

- **Problem ID:** SIH26187
- **Problem Statement Title:** AI-Based Intelligent Video Analytics Platform for Border Surveillance using existing CCTV Infrastructure
- **Organization:** Ministry of Home Affairs (MHA)
- **Department:** Sashastra Seema Bal (SSB), Police II Division
- **Category:** Software
- **Theme:** Smart Automation

---

## 3. Why This Idea Was Chosen

Border Outposts and remote frontier checkpoints manage vast stretches of international borders (such as Indo-Nepal and Indo-Bhutan borders guarded by SSB). These sectors already possess thousands of deployed CCTV, IP, and PTZ camera feeds. However, legacy monitoring relies almost entirely on manual operator vigilance across wall-mounted multiview monitors. Human fatigue sets in within 20 minutes, leading to missed incursions, delayed interdictions, and unverified cross-border movements.

Rather than proposing multi-crore hardware replacements with specialized proprietary military sensors, **IBVAP was chosen because it delivers an open, software-defined edge intelligence layer that runs directly on top of existing RTSP/ONVIF infrastructure.** It democratizes tactical defense AI by pairing state-of-the-art neural detection, deterministic computational geometry, and cryptographically verifiable chain-of-custody forensics on cost-effective COTS (Commercial Off-The-Shelf) hardware.

---

## 4. Real-World Problem

Border security personnel stationed in challenging border terrains face critical operational bottlenecks:

1. **Operator Cognitive Overload:** Monitoring 16 to 64 continuous camera channels simultaneously is physiologically impossible for human operators over 8-hour shifts.
2. **False Alarm Fatigue:** Traditional motion-detection triggers alarms for vegetation swaying, wandering cattle, shadows, weather anomalies, and illumination shifts, causing operators to eventually ignore or disable sirens.
3. **Delayed Intrusion Interdiction:** By the time a breach is visually spotted on a live feed, the infiltrator has often crossed the zero-line and vanished into civilian settlements or dense terrain.
4. **Lack of Forensic Chain-of-Custody:** In legal inquiries, standard CCTV video files are easily disputed due to lack of tamper-proof metadata, exact timestamping, and cryptographic hashing linking the alert to the exact source frame.
5. **Bandwidth and Compute Bottlenecks:** Streaming high-resolution, uncompressed video feeds from remote BOPs to central headquarters saturates satellite/cellular backhauls, necessitating local edge inference with low latency.

---

## 5. Proposed Solution

IBVAP introduces a unified, modular, and resilient Command, Control, Communications, Computers, Intelligence, Surveillance, and Reconnaissance (C4ISR) platform:

- **Hardware Agnostic Ingestion:** Connects to any RTSP, RTMP, WebRTC, ONVIF camera stream, or offline video file via MediaMTX and OpenCV.
- **Asynchronous Decoupled AI Pipeline:** Runs video playback at native 30 FPS while feeding a thread-safe singleton AI Scheduler that executes inference at bounded target intervals (e.g., 8–10 FPS) without UI stutter or memory leaks.
- **Deterministic Computational Geometry:** Evaluates Ray-Casting Point-in-Polygon (PIP) for multi-vertex restricted zones and Vector Cross-Products for virtual tripwires with directional discrimination (`INWARD` vs. `OUTWARD`).
- **Multi-Frame ANPR & Watchlist:** Performs vehicle crop extraction, optical character recognition (EasyOCR), regex normalization for Indian vehicle registrations, and 3-frame consensus validation before querying stolen/flagged vehicle databases.
- **Facial Screening & Re-ID:** Vectorized facial feature extraction matched against high-risk subject databases using `pgvector` cosine similarity indexing.
- **Dual-Model Detection Engine:** Unified forward pass combining a general baseline detector (YOLOv11 / RF-DETR) with specialized threat weights (for drones, weapons, and contraband) via IoU overlap suppression.
- **Immutable Forensic Audit & Evidence:** Automatically records 12-second rolling video clips (5s pre-event + 7s post-event) and cryptographic SHA-256 hashes for every security incident.
- **External Tactical Dispatch:** Publishes high-severity alerts over MQTT to field tactical radios and Telegram Webhooks for rapid response unit dispatch.

---

## 6. Problem → Solution Mapping

| Operational Challenge | IBVAP Technical Solution | Implementation Mechanism | Status |
|---|---|---|---|
| Manual monitoring fatigue | Automated 24/7 neural detection & tracking | Asynchronous `AIScheduler` + Kalman Filter | **Implemented** |
| Swaying trees & shadow false alarms | Deep semantic object classification | Person/Vehicle/Weapon/Drone neural filters | **Implemented** |
| Directional breach ambiguity | Vector cross-product fence geometry | Inward/Outward crossing vector math in `BorderRulesService` | **Implemented** |
| Illegible or distorted license plates | Temporal consensus ANPR validation | `PlateValidator` (3-frame hit consensus @ 60% agreement) | **Implemented** |
| Evidence tampering in legal proceedings | Cryptographic audit trail & SHA-256 evidence | `EvidenceService` rolling clip buffer + SHA-256 hash | **Implemented** |
| Remote backhaul bandwidth saturation | Edge processing with WebSocket event broadcasting | Local Python inference, JSON alert payloads over WSS | **Implemented** |
| Field patrol notification delay | Multi-channel alert dispatch | `AlertDispatchService` (MQTT broker + Telegram Webhook) | **Implemented** |
| BOP moving/dynamic coordinate tracking | Live NMEA GPS stream polling | `GeoService` hardware serial `/dev/ttyUSB` polling | **Implemented** |
| Drone and weapon detection | Dual-model inference pipeline | `DetectionService` secondary threat model integration | **Implemented** |
| Offline recorded video analysis | Batch video upload & retrospective audit | `AuditService` + `POST /api/audit/upload` | **Implemented** |

---

## 7. High-Level Architecture

```mermaid
flowchart TB
    subgraph EdgeIngestion["Layer 1: Video Ingestion & Hardware Edge"]
        CAM1["CCTV / PTZ RTSP Feed"]
        CAM2["Thermal / IR Stream"]
        CAM3["Offline Video Upload (MP4/AVI)"]
        GPS["NMEA GPS Serial Hardware (COM/USB)"]
        MTX["MediaMTX Stream Gateway"]
        CAM1 --> MTX
        CAM2 --> MTX
    end

    subgraph CoreBackend["Layer 2: IBVAP Core Ingestion & Decoupled Engine"]
        CM["CameraManager (Threaded Capture)"]
        GEO["GeoService (Coordinate Poller)"]
        MTX --> CM
        CAM3 --> CM
        GPS --> GEO
        
        SCHED["AIScheduler (Singleton Worker)"]
        CM -->|"Latest Frame Buffer (30 FPS)"| SCHED
        CM -->|"MJPEG Feed (30 FPS)"| WebViewport
    end

    subgraph AIPipeline["Layer 3: Neural & Analytical Processing"]
        DET["DetectionService (FP16 Tensor Core Engine)"]
        BASE_M["Base Model (YOLOv11 / RF-DETR)"]
        SPEC_M["Specialized Model (Drones/Weapons)"]
        DET --> BASE_M
        DET --> SPEC_M
        
        TRK["TrackingService (Kalman Box Tracker)"]
        RULES["BorderRulesService (Ray-Casting & Vectors)"]
        ANPR["ANPR Service (Consensus & Normalizer)"]
        FACE["FaceService & ReID (pgvector)"]
        RISK["RiskEngine (Multi-Factor Scoring Matrix)"]
        
        SCHED --> DET
        DET --> TRK
        TRK --> RULES
        TRK --> ANPR
        TRK --> FACE
        RULES --> RISK
        ANPR --> RISK
        FACE --> RISK
    end

    subgraph DataForensics["Layer 4: Storage, Forensics & Dispatch"]
        DB[(PostgreSQL 16 + pgvector)]
        REDIS[(Redis 7 Cache)]
        EVID["EvidenceService (SHA-256 Clip Recorder)"]
        DISP["AlertDispatchService (MQTT & Telegram)"]
        
        RISK --> DB
        RISK --> EVID
        RISK --> DISP
        EVID --> DB
    end

    subgraph Presentation["Layer 5: Tactical Command Center (React 19 / TS)"]
        AUTH["Auth & Role Guard (JWT / Cookie)"]
        MAP["Tactical Map (MapLibre GL)"]
        GRID["Multi-Camera Grid (Focus / 2x2)"]
        INTEL["Intelligence Panel (Alerts & Audits)"]
        ANPR_UI["ANPR Feed & Watchlist"]
        HEALTH["System Health Telemetry"]
        
        GEO -.->|"WebSocket"| MAP
        DB --> AUTH
        SCHED -.->|"WebSocket Events"| INTEL
        CM -.->|"Live Video"| GRID
    end
```

---

## 8. System Structure & Directory Organization

```
IBVAP/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI REST & WebSocket endpoints
│   │   │   ├── anpr.py           # License plate query & watchlist management
│   │   │   ├── audit.py          # Batch video upload & retrospective threat audit
│   │   │   ├── auth.py           # JWT authentication, login/logout, role guard
│   │   │   ├── cameras.py        # Camera configuration & MJPEG live stream feeds
│   │   │   ├── demo.py           # Sandboxed scenario seeding (Intrusion / ANPR)
│   │   │   ├── events.py         # Security alert query, disposition, evidence retrieval
│   │   │   ├── system.py         # Hardware resource telemetry (CPU, GPU, RAM)
│   │   │   └── ws.py             # Authenticated bi-directional WebSocket event bus
│   │   ├── core/                 # Core infrastructure and security configuration
│   │   │   ├── config.py         # Pydantic BaseSettings, dynamic YAML hot-reloader
│   │   │   ├── database.py       # SQLAlchemy engine, connection pooling, SQLite guard
│   │   │   ├── events_pubsub.py  # Async event distribution pipeline
│   │   │   └── security.py       # Bcrypt password hashing, JWT decode, RBAC dependencies
│   │   ├── models/               # SQLAlchemy ORM database models
│   │   │   ├── camera.py         # Camera registry entity
│   │   │   ├── event.py          # SecurityEvent, PlateEvent, FaceEvent, Evidence, EventAudit
│   │   │   └── user.py           # User entity with hashed credentials and role scopes
│   │   └── services/             # Core computer vision and analytical business logic
│   │       ├── ai_scheduler.py   # Asynchronous multi-stream AI rate limiter & worker
│   │       ├── alert_dispatch.py # External alert publisher (MQTT / Telegram Webhooks)
│   │       ├── anpr/             # OCR engine, plate normalizer, and consensus validator
│   │       ├── audit_service.py  # Offline video batch processor & forensic scanner
│   │       ├── behavior_service.py # Loitering, running, and directional anomaly detectors
│   │       ├── border_rules_service.py # Ray-casting polygon & vector cross-product geometry
│   │       ├── camera_manager.py # Threaded stream ingestion & MJPEG frame generator
│   │       ├── detection_service.py # Singleton GPU inference engine with dual-model fusion
│   │       ├── evidence_service.py # Rolling frame buffer, 12s clip creator, SHA-256 hasher
│   │       ├── face_service.py   # Facial landmark detection and watchlist matching
│   │       ├── geo_service.py    # Hardware GPS NMEA serial listener & coordinate broadcaster
│   │       ├── reid_service.py   # pgvector cosine-distance facial re-identification
│   │       ├── risk_engine.py    # Multi-factor threat matrix & risk scoring engine
│   │       ├── system_health_service.py # GPU/CPU performance monitor
│   │       └── tracking_service.py # Multi-camera Kalman Filter & SORT tracker
│   └── requirements.txt          # Python dependencies
├── configs/                      # Hot-reloadable YAML operational configurations
│   ├── anpr.yaml                 # ANPR confidence thresholds and regex patterns
│   ├── bytetrack.yaml            # Tracker association thresholds and max track age
│   ├── cameras.yaml              # Camera feed definitions, RTSP URLs, and geolocations
│   ├── risk.yaml                 # Threat score weighting matrix and severity thresholds
│   ├── system.yaml               # Engine intervals, thread pool sizes, and worker bounds
│   ├── watchlist.yaml            # Registered high-risk vehicle plates and subjects
│   └── zones.yaml                # Restricted zone polygons and virtual fence lines
├── data/                         # Local storage volumes for video feeds and evidence
│   ├── evidence/                 # Event snapshot JPGs and 12-second MP4 clips
│   └── videos/                   # Sample surveillance datasets (VIRAT) and uploads
├── docs/                         # Technical documentation and benchmark freezes
│   └── benchmark/                # Ground-truth dataset records and evaluation reports
├── frontend/                     # Tactical Command Center (React 19, TypeScript, Vite)
│   ├── src/
│   │   ├── components/           # Modular defense-grade UI components
│   │   │   ├── AnprPanel.tsx     # Plate feed and verification panel
│   │   │   ├── AuditUploadModal.tsx # Drag-and-drop batch video upload modal
│   │   │   ├── CameraDirectory.tsx  # Camera status list with live health badges
│   │   │   ├── CameraGrid.tsx    # Multi-view 2x2 camera matrix
│   │   │   ├── IntelligencePanel.tsx # Real-time alerts, disposition controls, telemetry
│   │   │   ├── MissionHeader.tsx # Tactical HUD status, system clock, user identity
│   │   │   ├── OperationalStrip.tsx # Metrics counter, data origin switcher, sim triggers
│   │   │   ├── SurveillanceWorkspace.tsx # Multi-mode viewport container
│   │   │   ├── SystemHealthPanel.tsx # Live CPU, GPU VRAM, and AI pipeline latency metrics
│   │   │   ├── TacticalMap.tsx   # Geospatial BOP and camera layout (MapLibre GL)
│   │   │   └── VideoViewport.tsx # Individual high-performance stream canvas with HUD
│   │   ├── tokens.css            # Tactical UI design tokens (color schemes, glassmorphism)
│   │   └── types/                # Strict TypeScript domain interfaces
├── scripts/                      # Operational utilities, profilers, and benchmark runners
│   ├── benchmark_full_pipeline.py # End-to-end multi-camera load and latency benchmark
│   ├── ensure-docker.js          # Pre-flight container dependency verification
│   ├── evaluate_detector.py      # Model-agnostic precision, recall, and mAP evaluation
│   ├── fast_profiler.py          # Stage-by-stage inference and tracking latency breakdown
│   ├── freeze_dataset.py         # Ground-truth dataset freezing and SHA-256 validation
│   └── start-backend.js          # Cross-platform Python virtualenv bootstrap
├── docker-compose.yml            # Multi-container orchestration (Postgres, Redis, MediaMTX, App)
└── package.json                  # Root monorepo orchestration script
```

---

## 9. End-to-End Workflow

```mermaid
sequenceDiagram
    autonumber
    participant Cam as CCTV / Video Source
    participant CM as CameraManager
    participant Sched as AIScheduler
    participant AI as Detection & Tracking
    participant Rules as Border Rules & ANPR
    participant Risk as RiskEngine
    participant Evid as EvidenceService
    participant DB as PostgreSQL 16
    participant WS as WebSocket Bus
    participant UI as Command Center UI
    participant Dispatch as MQTT / Telegram

    Cam->>CM: Ingest RTSP / MP4 Frame (30 FPS)
    CM->>UI: Stream MJPEG Low-Latency Feed (30 FPS)
    CM->>Sched: Submit Latest Frame to Bounded Buffer
    Note over Sched: Rate-Limits to Target AI FPS (e.g. 8-10 FPS)<br/>Drops Stale Intermediate Frames

    Sched->>AI: Execute Neural Forward Pass (FP16)
    AI->>AI: Associate Tracks via Kalman Filter
    AI->>Rules: Evaluate Polygons, Tripwires & OCR

    alt Security Event Triggered (Zone Breach / Watchlist Hit)
        Rules->>Risk: Score Event through Multi-Factor Matrix
        Risk->>DB: Persist SecurityEvent & PlateEvent
        Risk->>Evid: Capture Snapshot & Start 12s Clip Buffer
        Evid->>DB: Store Evidence Record + SHA-256 Hash
        Risk->>WS: Broadcast Event to Connected Operators
        WS->>UI: Trigger Audio/Visual Alert on HUD
        opt Severity == HIGH or CRITICAL
            Risk->>Dispatch: Publish Alert via MQTT & Telegram Webhook
        end
    end

    UI->>DB: Operator Updates Disposition (ACK / ESC / DISMISS)
    DB->>DB: Record Immutable EventAudit Entry
```

---

## 10. Core Subsystems & Analytical Pipelines

### 10.1 Camera Ingestion Architecture
Video frames are captured by independent worker threads in `CameraManager`. Each camera stream operates in a non-blocking ingestion loop that updates a thread-safe `latest_frame` buffer. If the AI inference pipeline experiences transient latency spikes, the ingestion thread simply overwrites older frames in the buffer. This ensures that:
1. Video display FPS remains buttery-smooth (25–30 FPS).
2. The AI detector always processes the freshest available frame (0ms frame age lag).
3. Memory consumption remains strictly bounded ($O(1)$ per stream) without unbounded queue build-up.

### 10.2 AI Detector & Dual-Model Architecture
The detection engine (`DetectionService`) is a thread-safe GPU singleton:
- **Base Detection:** Executes PyTorch / YOLOv11 / RF-DETR with FP16 half-precision on NVIDIA Tensor Cores.
- **Dual-Model Support:** Concurrently loads specialized threat weights (`SPECIALIZED_THREAT_MODEL_PATH`) in VRAM to detect niche border risks (such as micro-drones, firearms, and contraband).
- **Intelligent Non-Maximum Suppression (NMS):** When the base model (detecting an "airplane" or "backpack") and the specialized threat model (detecting a "drone" or "weapon") detect an overlapping object ($\text{IoU} > 0.50$), the specialized threat classification takes precedence.

```mermaid
flowchart LR
    Frame["Input Video Frame"] --> Base["Base Detector (YOLOv11/RF-DETR)"]
    Frame --> Spec["Specialized Threat Detector (Drones/Weapons)"]
    Base -->|"Persons, Vehicles, Generic"| Fusion["NMS & Priority Conflict Resolver"]
    Spec -->|"Drones, Weapons, Contraband"| Fusion
    Fusion -->|"Unified Detection Array"| Tracker["Tracking Service"]
```

### 10.3 Tracking Architecture & Identity Model

#### Mandatory Distinction: Tracking Identity vs. Biometric Identity
IBVAP strictly separates kinematic trajectory tracking from human biometric identification:
- **Tracking Identity (`track_id`):** A transient spatial-temporal identifier (e.g., `CAM-001:P-024`) produced by a 2D Kalman Box Filter and IoU association. It tracks a continuous bounding box trajectory across consecutive frames of a *single camera view*.
- **Biometric Identity:** A permanent, verified human identity (e.g., "Subject-482 / Infiltrator A") derived from facial embedding matching or government database records.

#### Format: Camera-Qualified Identity
Track IDs in IBVAP are strictly camera-qualified:
$$\text{Track ID} = \texttt{<Camera-ID>:<Prefix>-<Sequential-ID>}$$
- `CAM-001:P-024` $\rightarrow$ Person #24 on Camera 1
- `CAM-002:V-102` $\rightarrow$ Vehicle #102 on Camera 2
- `CAM-004:D-007` $\rightarrow$ Drone #7 on Camera 4

#### Comparison with Alternative Identity Models

| Identity Model | Continuity & Accuracy | Compute Overhead | Privacy & Legal Risk | Operational Suitability | Primary Limitation |
|---|---|---|---|---|---|
| **Frame-Local IDs** | None (resets every frame) | Negligible | Low | Unusable | Cannot track speed, loitering, or zone crossings |
| **Global Synthetic IDs** | Misleading (assumes global coverage) | Low | Medium | Dangerously High False Match Rate | Falsely assumes Person #1 on Cam 1 is Person #1 on Cam 2 |
| **Camera-Qualified IDs (IBVAP)** | Continuous within camera field | Very Low ($<1\text{ms}$) | Low | **Optimal for Sector Defense** | Resets when object exits camera FOV |
| **Face Biometric Identity** | Absolute when face visible | High (pgvector matching) | High (requires authorized consent/warrant) | Critical for Watchlist Interdiction | Fails under occlusion, distance, or low resolution |
| **Cross-Camera Re-ID (Appearance)** | High if appearance stable | Very High (Re-ID embeddings) | Medium | Experimental (Subject to clothing/lighting shifts) | High false positive rate in military camouflage |

### 10.4 Virtual Fence & Restricted Zone Engine
Implemented in `BorderRulesService` using pure computational geometry without heavy GIS dependencies:
- **Restricted Zones (Ray-Casting Algorithm):** Tests whether the bottom-center coordinate $(x_{\text{center}}, y_{\text{bottom}})$ of an object's bounding box is inside an arbitrary $N$-point polygon. Alarms trigger on state transitions (`OUTSIDE` $\rightarrow$ `INSIDE`).
- **Virtual Fences (Vector Cross-Products):** Tests whether the trajectory vector between the object's previous coordinate $P_{\text{prev}}$ and current coordinate $P_{\text{curr}}$ intersects line segment $L = (P_1, P_2)$. Direction is deterministically classified:
$$\text{Direction} = \begin{cases} \text{INWARD}, & \text{if } (P_2 - P_1) \times (P_{\text{curr}} - P_{\text{prev}}) > 0 \\ \text{OUTWARD}, & \text{if } (P_2 - P_1) \times (P_{\text{curr}} - P_{\text{prev}}) < 0 \end{cases}$$

### 10.5 ANPR Pipeline (Multi-Frame Consensus)
Located in `backend/app/services/anpr/`:
1. **Vehicle Crop Extraction:** Filters detections for `car`, `motorcycle`, `bus`, `truck`.
2. **OCR Engine:** EasyOCR extracts alphanumeric character candidates and localized bounding boxes.
3. **Plate Normalization:** Cleans spaces, punctuation, and applies regex validation for standard Indian High Security Registration Plates (HSRP): `^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$`.
4. **Consensus Validation (`PlateValidator`):** Requires at least 3 matching OCR readings across consecutive frames with a $\ge 60\%$ consensus ratio before committing a validated plate event to the database.

### 10.6 Suspicious Activity & Multi-Factor Risk Engine
The `RiskEngine` calculates a normalized threat score ($0–100$) by combining:
- **Object Type Base Weight:** Person ($20$), Vehicle ($15$), Drone ($50$), Weapon ($80$).
- **Zone Multiplier:** Public Buffer ($1.0\times$), Restricted Zero-Line ($2.5\times$), Sensitive BOP Perimeter ($3.0\times$).
- **Behavioral Penalties:** Loitering ($+25$), Rapid Running ($+30$), Wrong-Way Movement ($+35$), Night-Time Crossing ($+20$).
- **Watchlist Matches:** Stolen Plate ($+40$), High-Risk Subject ($+50$).

Scores map directly to operational severities:
- **$0–39$:** `LOW` (Logged for forensic telemetry)
- **$40–69$:** `MEDIUM` (Flagged in Intelligence Panel)
- **$70–89$:** `HIGH` (Audio alert + MQTT dispatch)
- **$90–100$:** `CRITICAL` (Flashing HUD siren + Telegram emergency push)

---

## 11. Evidence Integrity & Forensics Architecture

In high-stakes border interdictions, legal accountability requires verifiable, tamper-evident records.

```mermaid
flowchart TD
    Breach["Security Event Triggered (ID: 482)"] --> Capture["EvidenceService Triggered"]
    Capture --> Snap["Save Frame Snapshot (JPEG, Quality 85)"]
    Capture --> Clip["Stitch 12s MP4 Video Clip (5s Pre + 7s Post @ 5 FPS)"]
    
    Snap --> HashSnap["Compute SHA-256 Hash (Snapshot)"]
    Clip --> HashClip["Compute SHA-256 Hash (Video Clip)"]
    
    HashSnap --> DBRecord["Persist to 'evidence' Table in PostgreSQL"]
    HashClip --> DBRecord
    
    DBRecord --> Metadata["Record Immutable Metadata:<br/>- Camera ID<br/>- Timestamp (UTC ISO 8601)<br/>- File Path<br/>- SHA-256 Checksum<br/>- Data Origin (LIVE/DEMO/IMPORTED)"]
```

### Forensic Features:
- **Rolling Pre/Post Event Buffer:** Maintains 5 seconds of pre-event history in a bounded ring buffer. Upon trigger, records 7 seconds of post-event footage, outputting a lightweight 12-second MP4 clip.
- **SHA-256 Cryptographic Verification:** Calculates SHA-256 checksums of the raw media on disk immediately upon writing, storing the hash in PostgreSQL.
- **Event Audit Log:** The `EventAudit` table creates an immutable, append-only ledger recording every operator action (`ACKNOWLEDGED`, `ESCALATED`, `DISMISSED`), including operator username, timestamp, and notes.

---

## 12. LIVE / DEMO / TEST / IMPORTED Data Isolation

IBVAP implements strict data provenance across all database tables and UI views:

- `LIVE`: Generated strictly from active physical RTSP camera streams.
- `DEMO`: Generated from sandbox scenario buttons (e.g. "Demo Intrusion", "Demo ANPR") for operator drill training.
- `TEST`: Generated during automated Pytest and CI/CD verification runs.
- `IMPORTED`: Generated from offline batch video file uploads during retrospective threat auditing.

> [!IMPORTANT]
> **Zero Contamination Policy**
> Operators can toggle the dashboard view between `LIVE`, `DEMO`, and `IMPORTED` records. Live defense metrics and operational alerts are never mixed with simulation or training data.

---

## 13. Ground-Truth Benchmark & AI Evaluation

### 13.1 Benchmark Methodology
IBVAP adheres to strict empirical ML engineering principles: **Ground truth is strictly human-annotated and frozen.** AI pre-annotations are treated only as preliminary assistance and are never promoted to ground truth without manual verification.

### 13.2 Benchmark Freeze Record: `IBVAP-GT-v2.0`
- **Freeze Timestamp:** `2026-08-31 17:05:11 UTC`
- **Dataset Version:** `IBVAP-GT-v2.0`
- **Video Source:** `VIRAT_S_000004.mp4` (Surveillance footage representative of border checkpoint terrain)
- **Total Test Images:** 200 frames
- **Total Ground Truth Objects:**
  - Class `0` (Person): **901 instances**
  - Class `1` (Vehicle): **111 instances**
- **Integrity Proof:**
  - `benchmark/checksums/images.sha256`
  - `benchmark/checksums/labels.sha256`

### 13.3 Evaluated Model Baseline & Candidate Comparison

| Model | Architecture | Status | Person Recall | Vehicle Recall | Person F1 | Vehicle F1 | Inference Latency (CUDA FP16) | Notes |
|---|---|---|---|---|---|---|---|---|
| **YOLOv11n (Baseline)** | Lightweight CNN / C3k2 | **Verified Baseline** | 11.9%* | 72.5%* | 14.1%* | 79.8%* | **8.2 ms (640x640)** | Active production baseline for edge deployments |
| **RF-DETR-Small** | Transformer / Deformable DETR | **Experimental Candidate** | *Pending Fine-Tuning* | *Pending Fine-Tuning* | *Pending Fine-Tuning* | *Pending Fine-Tuning* | ~28.4 ms (CPU) | Architectural wrapper integrated; awaiting GPU fine-tuning |

*\*Note: Baseline zero-shot metrics on high-angle VIRAT dataset highlight the necessity of domain fine-tuning for low-resolution distant border incursions.*

### 13.4 Model Promotion Criteria
A candidate model (e.g., fine-tuned RF-DETR) is promoted to default production **only** when it meets all of the following:
1. Achieves superior $\text{mAP@0.50}$ and Recall on `IBVAP-GT-v2.0` compared to YOLOv11n.
2. Demonstrates zero regression on multi-camera tracking ID switches.
3. Maintains inference latency under $25\text{ms}$ per frame on target hardware (NVIDIA RTX 3050 / T4).
4. Produces a recorded SHA-256 weight checksum logged in `configs/system.yaml`.

---

## 14. Performance Engineering & Multi-Camera Scaling

Surveillance systems often fail when multi-camera processing starves the system of CPU/GPU resources. IBVAP employs a specialized multi-tiered performance architecture:

```mermaid
flowchart TD
    subgraph MultiStreamIngestion["Multi-Camera Ingestion (30 FPS Display Rate)"]
        C1["Camera 1 (30 FPS)"] --> B1["Bounded Buffer 1"]
        C2["Camera 2 (30 FPS)"] --> B2["Bounded Buffer 2"]
        C3["Camera 3 (30 FPS)"] --> B3["Bounded Buffer 3"]
        C4["Camera 4 (30 FPS)"] --> B4["Bounded Buffer 4"]
    end

    subgraph CentralWorker["Centralized GPU Inference Worker"]
        B1 & B2 & B3 & B4 -->|"Round-Robin Poll"| Worker["AIScheduler Loop"]
        Worker -->|"Dynamic Interval Check"| Check{"Time Delta >= 1/Target_FPS?"}
        Check -- Yes --> Predict["Single-Pass GPU Tensor Cores (FP16)"]
        Check -- No --> Drop["Skip Frame (Zero Age Lag)"]
    end

    subgraph DecoupledTracking["Decoupled Tracking & HUD"]
        Predict --> Trk["Update Kalman Trackers"]
        Trk --> HUD["Overlay Tactical Bounding Boxes"]
        HUD --> Output["Live WebSocket Telemetry (Sub-100ms)"]
    end
```

### Performance Optimizations:
1. **Decoupled Frame Display vs. AI Inference:** Display feeds render at smooth 30 FPS. The `AIScheduler` samples frames at a target rate (e.g., 8–10 FPS), ensuring low GPU load while maintaining tracking continuity.
2. **Latest-Frame-Wins Buffer:** Ingestion buffers hold exactly 1 unconsumed frame. Stale frames are overwritten immediately, eliminating queue latency.
3. **FP16 Half-Precision:** Activates Tensor Cores on NVIDIA GPUs, reducing memory footprint by 50% and doubling forward pass throughput.
4. **Asynchronous Thread Pool Offloading:** OCR analysis and database commits run in background `ThreadPoolExecutor` workers, preventing main-thread blocking.

---

## 15. Tactical Command Center (Dashboard UI)

The frontend is a mission-critical web application built with **React 19, TypeScript, and Vite**, following modern defense SOC design aesthetics:

- **Mission Header:** Displays sector callsign, authenticated operator identity, real-time mission clock, and overall operational health status (`OPERATIONAL`, `DEGRADED`, `CRITICAL`).
- **Camera Directory:** Real-time tree view of all registered border cameras with live connectivity indicators, camera status, and detection counters.
- **Surveillance Workspace:**
  - **Focus Mode:** Expanded high-resolution single camera feed with tactical HUD bounding boxes, restricted zone polygon overlays, and tripwire vectors.
  - **2x2 Grid Mode:** Synchronized multi-camera matrix for overall sector awareness.
  - **Tactical Map (MapLibre GL):** Geospatial satellite map displaying the Border Outpost (BOP) command location and camera geo-anchors, with live coordinate updates from hardware GPS serial feeds.
- **Intelligence Panel:** Real-time alert feed with sound alerts, severity filters (`ALL`, `CRITICAL`, `HIGH`, `MEDIUM`), search, and operator disposition workflow (`ACKNOWLEDGE`, `ESCALATE`, `DISMISS`). Includes dedicated tabs for **ANPR Vehicle Feeds** and **System Health Telemetry**.
- **Operational Strip:** System-wide counters (Cameras Online, Persons, Vehicles, Active Threats, AI Engine Type), Data Origin toggle (`LIVE` / `DEMO` / `IMPORTED`), and Offline Video Audit launcher.

---

## 16. Security & Production Guardrails

| Security Control | Implementation Mechanism | Verification / Evidence | Status |
|---|---|---|---|
| **Production SQLite Guard** | `backend/app/core/database.py` halts startup if SQLite is used in `ENV=production` | Verified in core database initializer | **Enforced** |
| **Authentication & RBAC** | JWT (HS256) with 30-minute expiration, role scopes (`ADMIN`, `OPERATOR`) | `backend/app/core/security.py`, `backend/tests/test_security.py` | **Enforced** |
| **Secure Cookie Handling** | `SameSite=Lax`, `HttpOnly=True`, `Secure=True` for HTTPS access tokens | `backend/app/api/auth.py` | **Enforced** |
| **Password Security** | Bcrypt salted hashing with 12 rounds (72-byte truncation protection) | `backend/app/core/security.py` | **Enforced** |
| **HTTP Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `HSTS`, `CSP` | `backend/app/main.py` middleware | **Enforced** |
| **Network Isolation** | PostgreSQL and Redis run on private container networks; only API exposed | `docker-compose.yml` | **Enforced** |
| **Automated Vulnerability Scan** | Bandit Python AST static security analysis in CI/CD pipeline | `.github/workflows/ci.yml` | **Enforced** |
| **NPM Dependency Audit** | High-level vulnerability scan during CI build | `.github/workflows/ci.yml` (`npm audit --audit-level=high`) | **Enforced** |

---

## 17. Operational Difficulties & Technical Mitigations

| Challenge | Root Cause | Systemic Impact | IBVAP Technical Mitigation | Status |
|---|---|---|---|---|
| **Camouflage / Distance Occlusion** | Infiltrators crawling or obscured by foliage | Low confidence bounding box detections | Dynamic per-class confidence thresholds + Kalman velocity prediction | **Mitigated** |
| **Night-Time / Thermal Glare** | Low contrast and high sensor noise in IR mode | False positive bounding box jitter | Multi-frame track confirmation (`min_hits=1`, `max_age=15`) | **Mitigated** |
| **Multi-Camera GPU Contention** | 4–16 streams running simultaneous inference | GPU VRAM out-of-memory and frame lag | Centralized `AIScheduler` singleton with bounded latest-frame buffers | **Mitigated** |
| **ANPR License Plate Distortion** | High vehicle speed and motion blur | OCR character misinterpretation (e.g. `O` vs `0`) | Plate regex normalizer + 3-frame consensus ratio validation | **Mitigated** |
| **Stream Disconnections** | Physical cable cuts or network dropouts at BOP | Frozen frames or backend crashing | Auto-reconnect thread loop in `CameraStreamThread` | **Mitigated** |
| **Database Failure / Slowdown** | High volume of detection events during alerts | Video ingestion frame drops | Thread-pool offloading for database writes (`_persist_events_async`) | **Mitigated** |
| **Demo Data Contamination** | Operators running drills on live consoles | Contaminated legal evidence records | Strict `data_origin` column isolation (`LIVE`, `DEMO`, `IMPORTED`) | **Mitigated** |
| **Hardware GPS Loss** | GPS antenna disconnection or indoor usage | Lost tactical map coordinates | Graceful fallback to simulated BOP wander coordinates | **Mitigated** |

---

## 18. Technology Stack & Justifications

| Component | Selected Technology | Role in Platform | Alternative Considered | Technical Tradeoff & Justification |
|---|---|---|---|---|
| **Backend API** | **FastAPI (Python 3.11)** | REST endpoints & WebSockets | Django / Flask | Async ASGI performance, native OpenAPI documentation, lightweight footprint |
| **Frontend UI** | **React 19 + TypeScript + Vite** | Tactical Command Center HUD | Vue / Angular | Massive ecosystem, type safety for defense domains, ultra-fast Vite HMR |
| **Tactical Map** | **MapLibre GL + React-Map-GL** | Geospatial BOP & camera mapping | Leaflet / Google Maps | Vector tile rendering, 60 FPS GPU acceleration, zero proprietary API costs |
| **Primary Database** | **PostgreSQL 16 + pgvector** | Events, evidence, and face vectors | MongoDB / MySQL | ACID compliance for legal evidence, native 512-d vector similarity indexing |
| **Caching & PubSub** | **Redis 7** | Rate limiting & message broker | RabbitMQ | Low memory footprint, sub-millisecond key-value caching and session state |
| **Streaming Gateway** | **MediaMTX** | RTSP / WebRTC multiplexer | GStreamer / FFmpeg server | Zero-config multi-protocol RTSP/WebRTC proxy in single Go binary |
| **Deep Learning** | **PyTorch + Ultralytics YOLOv11** | Object detection & feature extraction | TensorFlow / OpenVINO | Industry-leading detection mAP, native TensorRT/ONNX exportability |
| **Candidate Model** | **RF-DETR (Deformable DETR)** | Transformer-based threat detector | Faster R-CNN | Superior global attention and small-object detection in complex backgrounds |
| **Tracking Engine** | **Custom Kalman Box Tracker (SORT)** | Bounding box spatial tracking | DeepSORT | Sub-millisecond CPU tracking latency without requiring heavy Re-ID feature extraction |
| **OCR Engine** | **EasyOCR + PyTorch** | License plate character extraction | Tesseract OCR | Deep learning based scene-text recognition far superior on angled/blurry plates |
| **Alert Dispatch** | **Eclipse Paho MQTT + HTTPX** | Radio network & webhook publisher | Celery / ZeroMQ | Standard IoT protocol for military tactical radios, lightweight async HTTP client |
| **Containerization** | **Docker & Docker Compose** | Multi-service orchestration | Kubernetes | Simple single-command deployment suitable for remote edge BOP computers |

---

## 19. Installation & Quick Start

### 19.1 Prerequisites
- **Operating System:** Windows 10/11, Ubuntu 22.04 LTS, or Debian 12
- **Python:** Version `3.10` or `3.11`
- **Node.js:** Version `20.x` or `22.x` and `npm 10+`
- **Docker:** Docker Desktop or Docker Engine with Docker Compose v2
- **Hardware (Recommended):** NVIDIA GPU with CUDA 12 support (RTX 3050 / T4 or higher), 16GB RAM

### 19.2 Step 1: Clone Repository
```bash
git clone https://github.com/imrajeevraj/IBVAP.git
cd IBVAP
```

### 19.3 Step 2: Environment Configuration
Copy the sample environment file and configure secrets:
```bash
cp .env.example .env
```
Edit `.env` to configure your credentials:
```ini
DATABASE_URL=postgresql://ibvap_user:ibvap_pass@localhost:5432/ibvap_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secure-32-character-minimum-secret-key-here
ADMIN_USERNAME=ibvap-admin
ADMIN_PASSWORD=YourSecurePassword123
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MODEL_PATH=yolo11n.pt
DEMO_MODE=true
DEMO_USERNAME=demo_operator
DEMO_PASSWORD=DemoPassword123
```

### 19.4 Step 3: Install Dependencies
```bash
# Install root orchestration dependencies
npm install

# Install frontend dependencies
npm --prefix frontend install

# Install Python virtual environment & backend packages
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 19.5 Step 4: Run Platform via Docker Infrastructure (Recommended)
Start the complete infrastructure with a single command:
```bash
npm start
```
*This command automatically initializes PostgreSQL (with `pgvector`), Redis, MediaMTX via Docker Compose, boots the FastAPI backend, and starts the Vite frontend dev server.*

Access the interfaces:
- **Tactical Command Center Dashboard:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 20. Running Verification & Benchmarks

### 20.1 Running Backend Pytest Suite
```bash
pytest backend/tests/ -v
```

### 20.2 Running Detector Benchmark Evaluation
Evaluate detector performance against frozen ground truth `IBVAP-GT-v2.0`:
```bash
python scripts/evaluate_detector.py --model yolo11n.pt --conf 0.25 --iou 0.50 --device cpu
```

### 20.3 Running Full Pipeline Diagnostic Profiler
Measure stage-by-stage inference, tracking, and zone latency across all streams:
```bash
python scripts/fast_profiler.py
```

### 20.4 Running Frontend Production Build
```bash
npm --prefix frontend run build
```

---

## 21. SIH Live Demonstration Scenarios

To demonstrate IBVAP during evaluation drills, operators can trigger pre-packaged scenarios directly from the **Operational Strip** (bottom right of the console):

1. **Scenario 1: Zero-Line Perimeter Incursion**
   - Click `Sim` $\rightarrow$ `Demo Intrusion`.
   - Generates a real-time `ZONE_ENTRY` and `VIRTUAL_FENCE_CROSSING` event for an inward-moving subject.
   - The HUD flashes red, triggers an audible threat chime, calculates an $85+$ risk score, generates a 12s evidence clip with SHA-256 hash, and broadcasts over MQTT.
2. **Scenario 2: Watchlist Vehicle Interdiction (ANPR)**
   - Click `Sim` $\rightarrow$ `Demo ANPR`.
   - Ingests a vehicle with plate number `DL01AB1234` (matching the high-risk watchlist).
   - Validates plate across the consensus buffer and displays a high-severity `WATCHLIST_MATCH` alert with vehicle snapshot and plate crop.
3. **Scenario 3: Offline Video Batch Audit**
   - Click `Offline Audit` on the operational strip.
   - Drag and drop an external surveillance video (e.g. `data/videos/virat/VIRAT_S_000001.mp4`).
   - The backend processes the video sequentially at maximum GPU throughput, tagging discovered threats as `IMPORTED`.
   - Operators can toggle the data view to `IMPORTED` to conduct post-incident forensic reviews.

---

## 22. Frequently Asked Questions (FAQ) for Evaluators & Judges

**Q1: What exact problem does IBVAP solve for border security forces like SSB?**  
**A:** It eliminates manual human surveillance fatigue across dozens of border camera feeds by providing an automated, real-time AI analytics layer that detects perimeter breaches, loitering, wrong-way movements, and high-risk vehicles on existing CCTV infrastructure.

**Q2: Does deploying IBVAP require purchasing expensive new smart cameras?**  
**A:** No. IBVAP is completely software-defined and hardware-agnostic. It connects directly to legacy RTSP, ONVIF, thermal, and analog-over-IP streams already deployed at Border Outposts.

**Q3: Why is camera-qualified identity (`CAM-001:P-024`) used instead of global synthetic IDs?**  
**A:** Bounding box trackers operate independently per camera view. Assigning global synthetic IDs without cross-camera facial/biometric verification creates false track merges. Camera-qualified IDs ensure strict spatial and forensic accuracy.

**Q4: How does the system avoid lagging when running AI on multiple camera streams?**  
**A:** Through the decoupled `AIScheduler`. Video ingestion threads maintain a single-frame bounded buffer, while a centralized GPU worker samples frames at a target AI rate (e.g., 8–10 FPS). Older unconsumed frames are dropped, guaranteeing sub-100ms situational awareness.

**Q5: How are false alarms from swaying trees or shadows eliminated?**  
**A:** Unlike legacy pixel-based motion detectors, IBVAP utilizes deep neural networks (YOLOv11/RF-DETR) that classify objects semantically (Person, Vehicle, Drone). Non-target motion is ignored by the detector.

**Q6: How does IBVAP determine whether a fence crossing is an infiltration or normal patrol?**  
**A:** The `BorderRulesService` computes vector cross-products between the virtual tripwire vector and the object's movement trajectory, deterministically classifying crossings as `INWARD` (incursion) or `OUTWARD` (friendly patrol).

**Q7: How does the ANPR pipeline handle blurry or noisy license plates?**  
**A:** It employs an alphanumeric regex normalizer and the `PlateValidator` multi-frame consensus engine, requiring at least 3 matching readings with $\ge 60\%$ agreement before committing an event.

**Q8: How is evidence protected against tampering for legal proceedings?**  
**A:** The `EvidenceService` captures a 12-second rolling clip and immediately computes an immutable SHA-256 cryptographic hash stored in PostgreSQL alongside UTC timestamps.

**Q9: How do you prevent demo or drill data from contaminating live border intelligence?**  
**A:** All database entities and WebSocket events carry a mandatory `data_origin` field (`LIVE`, `DEMO`, `TEST`, `IMPORTED`). The dashboard enforces strict origin filtering.

**Q10: What happens if a camera stream disconnects?**  
**A:** The `CameraStreamThread` enters an exponential backoff auto-reconnect loop, updating the camera directory status to `OFFLINE` and alerting the operator without crashing the application.

**Q11: How are field patrol units notified when an alert occurs?**  
**A:** High-severity and Critical events are published asynchronously over MQTT topics to tactical field devices and sent via Telegram Webhook alerts to patrol leaders.

**Q12: Can IBVAP operate in remote frontier areas with poor internet connectivity?**  
**A:** Yes. All neural inference, tracking, geometry calculations, and PostgreSQL storage execute locally on edge servers at the Border Outpost without cloud dependencies.

**Q13: Why is RF-DETR included alongside YOLOv11?**  
**A:** YOLOv11n serves as the fast, proven edge baseline. RF-DETR (Transformer-based) is integrated as an experimental candidate for its superior global context and small-object detection in cluttered border terrain.

**Q14: What is the criteria for promoting RF-DETR to the default production model?**  
**A:** It must demonstrate higher mAP and Recall on the frozen `IBVAP-GT-v2.0` benchmark, maintain latency under 25ms on target hardware, and show zero regression in tracking stability.

**Q15: How does the system handle moving or mobile Command Post positions?**  
**A:** The `GeoService` continuously polls hardware GPS devices via NMEA serial streams (`/dev/ttyUSB` or `COM3`), updating the BOP coordinates dynamically on the tactical map.

**Q16: How is facial recognition integrated without violating citizen privacy?**  
**A:** Facial screening is performed strictly against authorized, high-risk watchlist databases using 512-dimensional vector embeddings in `pgvector`. Unknown faces are assigned transient hashes without persistent profiling.

**Q17: What security protections exist against database hijacking or injection?**  
**A:** SQLAlchemy ORM parameterization prevents SQL injection, a strict SQLite guard blocks unencrypted file databases in production, and JWT HS256 tokens authenticate all REST and WebSocket connections.

**Q18: What is the latency between a physical breach and the dashboard alarm?**  
**A:** Under 100 milliseconds on GPU-accelerated edge nodes (8ms neural forward pass + 2ms tracking + 1ms geometry + WebSocket broadcast).

**Q19: How can operators audit historical offline footage from drones or handheld cameras?**  
**A:** Via the **Offline Audit** interface, which ingests MP4/AVI videos, passes frames through the full neural pipeline at maximum hardware speed, and indexes all detected threats under `IMPORTED` records.

**Q20: What is the primary business and operational ROI of IBVAP for border forces?**  
**A:** It maximizes existing infrastructure investments by transforming standard CCTV cameras into an autonomous defense grid, multiplying the effective coverage of border personnel while drastically cutting response times.

---

## 23. Known Limitations & Future Scope

### Current Limitations:
1. **Zero-Shot Low Resolution:** Pretrained COCO weights struggle with very distant individuals ($<20$ pixels high). Requires sector-specific fine-tuning on high-resolution thermal/optical border datasets.
2. **Adverse Weather Extreme Glare:** Heavy fog or dense monsoons can degrade optical cameras, necessitating hardware thermal sensor fusion.
3. **Cross-Camera Re-ID Camouflage Sensitivity:** Visual Re-ID without facial features is sensitive to military camouflage and uniform changes across non-overlapping camera zones.

### Future Roadmap:
- **Phase 1 (Q3 2026):** Domain fine-tuning of RF-DETR on multi-spectral thermal and optical border datasets.
- **Phase 2 (Q4 2026):** PTZ automated target lock and continuous optical auto-tracking.
- **Phase 3 (Q1 2027):** Multi-BOP federated intelligence sharing over secure encrypted mesh radio networks.
- **Phase 4 (Q2 2027):** Autonomous drone patrol integration with automated battery dock dispatch upon perimeter alarm.

---

## 24. License & Compliance

This project is developed for the **Smart India Hackathon 2026** under the auspices of the **Ministry of Home Affairs (Sashastra Seema Bal, Police II Division)**.

- **License:** Proprietary / Defense Use Only (Open-source components governed by respective MIT/Apache-2.0 licenses).
- **Compliance:** Adheres to MHA cyber-security directives and data sovereignty requirements for border defense infrastructure.

---

## 25. Disclaimer

*IBVAP is designed as an operational force multiplier and decision-support system for authorized defense and law enforcement personnel. Automated risk scores and alerts do not replace standard operating procedures (SOPs) and human verification by qualified border commanders.*
