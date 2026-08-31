# IBVAP — Intelligent Border Video Analytics Platform

> **Smart India Hackathon 2026 · Problem Statement: SIH26187**  
> **AI-Based Intelligent Video Analytics Platform for Border Surveillance using existing CCTV Infrastructure**  
> **Organization:** Ministry of Home Affairs · **Department:** Sashastra Seema Bal (SSB), Police II Division  
> **Category:** Software · **Theme:** Smart Automation

[![SIH 2026](https://img.shields.io/badge/SIH-2026-0ea5e9)](#smart-india-hackathon-2026)
[![Status](https://img.shields.io/badge/Status-SIH%20Ready-success)](#project-status)
[![Security](https://img.shields.io/badge/Security-GREEN-success)](#security-hardening)
[![Data Integrity](https://img.shields.io/badge/Data%20Integrity-GREEN-success)](#forensic-traceability--data-integrity)
[![Reliability](https://img.shields.io/badge/Reliability-GREEN-success)](#reliability)
[![AI](https://img.shields.io/badge/AI-AMBER-ffb000)](#ai-engine--model-strategy)
[![Performance](https://img.shields.io/badge/Performance-AMBER-ffb000)](#performance-engineering)
[![License](https://img.shields.io/badge/License-TBD-lightgrey)](#license)

---

## 1. What Is IBVAP?

**IBVAP (Intelligent Border Video Analytics Platform)** is a software-defined surveillance platform designed to transform conventional CCTV infrastructure into an intelligent, event-driven border monitoring system.

The central idea is simple:

> **Do not replace the existing CCTV network. Make it intelligent through software.**

IBVAP ingests standard IP-camera/video streams and adds AI-powered analytics such as:

- Human detection and tracking
- Vehicle detection and classification
- Virtual-fence / restricted-zone intrusion detection
- Real-time security alerts
- Event logging and operational dashboards
- ANPR with forensic lineage
- Face-processing integration with safety and review gates
- Evidence capture with cryptographic integrity hashing
- Multi-camera situational awareness
- System-health and infrastructure monitoring
- Live/demo/test data isolation
- Production readiness and security guardrails

The platform is designed around the constraints of remote surveillance environments: limited compute, unreliable networks, many simultaneous cameras, strict auditability, and the need to avoid replacing expensive camera hardware.

---

## 2. Why This Idea Was Chosen

Traditional CCTV systems are excellent at **recording video**, but recording alone does not answer the operator's most important questions:

- **Who entered a restricted area?**
- **Where did the person come from?**
- **Which camera saw them?**
- **Was the movement normal or suspicious?**
- **Was a vehicle involved?**
- **Was the event detected early enough to act?**
- **Can the operator prove what happened later?**

The SIH problem statement specifically targets the conversion of existing IP-based CCTV infrastructure into an AI-driven surveillance network without requiring dedicated smart-camera, FRS, or ANPR hardware.

IBVAP therefore focuses on a **software-first augmentation layer** that can sit on top of existing cameras.

### Core design principle

**Existing CCTV → AI perception → tracking → rules/risk → alert → evidence → operator response → audit**

---

## 3. Problem Statement Mapping

| SIH Requirement | IBVAP Response |
|---|---|
| Human detection and tracking | Detector + multi-object tracker |
| Vehicle detection/classification | Vehicle detector/classifier |
| Face detection / face processing | Dedicated face-processing pipeline with quality gates |
| ANPR | Plate detection + OCR + track-linked provenance |
| Virtual fence intrusion detection | Configurable normalized zones + crossing logic |
| Suspicious activity detection | Rule/risk pipeline built on tracked events |
| Night-time movement | Low-light/night-aware analysis path |
| Real-time alerts | Event/risk engine + dashboard alerts |
| Event logging | Persistent security/event records |
| Existing CCTV infrastructure | Standard IP/video stream ingestion |
| Cost-effective scaling | Shared AI workers, frame decoupling, throttling |
| Command-and-control integration | API/event architecture + operator dashboard |
| Forensic traceability | Source-frame lineage + evidence hashing |

> **Important:** Feature availability and production readiness are not the same thing. IBVAP deliberately exposes unavailable/uncalibrated capabilities rather than fabricating operational truth.

---

## 4. The Real-World Problems We Are Solving

### 4.1 Human monitoring does not scale

An operator cannot reliably watch four, eight, or dozens of feeds continuously and detect every subtle intrusion.

### 4.2 Conventional CCTV is reactive

Most CCTV deployments record video and rely on someone noticing an event in real time or investigating it later.

### 4.3 Smart-camera deployments can be expensive

Replacing a large installed camera network with specialized AI cameras can create significant capital and maintenance costs.

### 4.4 Remote locations have constrained computing

Border posts may not have workstation-class GPUs, unlimited memory, or stable high-bandwidth links.

### 4.5 False alerts are operationally expensive

A system that detects everything—including poles, shadows, reflections, and duplicate events—can become unusable because operators stop trusting it.

### 4.6 AI results must be auditable

A security alert should be traceable to:

`camera → frame → detection → track → rule → event → evidence → operator action`

### 4.7 Demo data must never masquerade as operational truth

Simulation is useful for hackathon demonstrations, but simulated events must not contaminate live statistics, history, alerts, or forensic records.

---

## 5. Proposed Solution

IBVAP uses a layered architecture:

```text
┌───────────────────────────────────────────────────────────────────┐
│                        EXISTING CCTV NETWORK                       │
│      IP Cameras / RTSP / Recorded Surveillance Video              │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                         VIDEO INGESTION                            │
│  Connection control · frame decoding · reconnect · health checks  │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
       ┌───────────────────┐        ┌────────────────────┐
       │ DISPLAY PATH      │        │ AI PATH            │
       │ Latest frame only │        │ Latest AI frame    │
       │ WebRTC/MJPEG      │        │ Queue size = 1     │
       └───────────────────┘        └─────────┬──────────┘
                                             │
                                             ▼
                                ┌─────────────────────────┐
                                │ AI DETECTOR              │
                                │ RF-DETR / benchmarked    │
                                │ model candidates         │
                                └────────────┬────────────┘
                                             │
                                             ▼
                                ┌─────────────────────────┐
                                │ MULTI-OBJECT TRACKER     │
                                │ Camera-qualified IDs     │
                                └────────────┬────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
             Zone / Risk Rules            ANPR             Face Processing
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                                ┌─────────────────────────┐
                                │ EVENT / ALERT ENGINE    │
                                │ Severity + correlation  │
                                └────────────┬────────────┘
                                             │
                         ┌───────────────────┼───────────────────┐
                         │                   │                   │
                         ▼                   ▼                   ▼
                    PostgreSQL            Evidence          WebSocket/API
                         │                   │                   │
                         └───────────────────┼───────────────────┘
                                             ▼
                                ┌─────────────────────────┐
                                │ IBVAP COMMAND CENTER     │
                                │ Live video · alerts      │
                                │ tracks · ANPR · health   │
                                └─────────────────────────┘
```

---

## 6. High-Level Architecture

```mermaid
flowchart LR
    C[IP Cameras / RTSP / Video Files]
    I[Ingestion Layer]
    D[AI Detection]
    T[Multi-Object Tracking]
    R[Rules + Risk Engine]
    A[ANPR]
    F[Face Processing]
    E[Event Service]
    DB[(PostgreSQL)]
    EV[(Evidence Storage)]
    W[Redis]
    API[FastAPI APIs]
    WS[WebSocket Events]
    UI[React + TypeScript Command Center]
    M[Monitoring / Health]

    C --> I
    I --> D
    D --> T
    T --> R
    T --> A
    T --> F
    R --> E
    A --> E
    F --> E
    E --> DB
    E --> EV
    E --> W
    DB --> API
    W --> API
    API --> UI
    WS --> UI
    M --> UI
    I --> M
    D --> M
    DB --> M
    W --> M
```

---

## 7. End-to-End Operational Workflow

```mermaid
sequenceDiagram
    participant Cam as CCTV Camera
    participant In as Ingestion
    participant AI as AI Worker
    participant Tr as Tracker
    participant Rules as Rules/Risk
    participant ANPR as ANPR
    participant Face as Face Pipeline
    participant DB as PostgreSQL
    participant Ev as Evidence
    participant UI as Command Center
    participant Op as Operator

    Cam->>In: Video frame
    In->>AI: Latest frame only
    AI->>Tr: Detections
    Tr->>Rules: Camera-qualified tracks
    Tr->>ANPR: Vehicle/plate candidates
    Tr->>Face: Face candidates
    Rules->>DB: Security event
    ANPR->>DB: Provenance-rich plate event
    Face->>DB: Face-processing event
    Rules->>Ev: Snapshot/clip request
    Ev->>DB: SHA-256 integrity metadata
    DB->>UI: API/event update
    UI->>Op: Alert + visual context
    Op->>UI: Review / acknowledge
```

---

## 8. AI Pipeline

### Detection

The detector answers:

> **What objects are visible in this frame?**

The primary classes for the benchmark are intentionally constrained to:

- `0 = person`
- `1 = vehicle`

The model layer is designed to be replaceable so that the detector can evolve without rewriting the rest of the surveillance stack.

### Tracking

The tracker answers:

> **Is this the same object I saw a moment ago?**

A tracker maintains temporal continuity across frames and reduces repeated counting of the same object.

### Rules and risk

Tracking alone does not create a security incident.

IBVAP converts tracks into operational events through rules such as:

- Restricted-zone crossing
- Virtual-fence crossing
- Persistence/dwell conditions
- Directional movement where calibration exists
- Suspicious movement heuristics
- Night-time movement conditions
- Vehicle/person co-occurrence
- Event cooldown/de-duplication

---

## 9. AI Model Strategy

### Current strategy

IBVAP separates **model experimentation** from the operational platform.

The current baseline reference established a YOLOv11n configuration. RF-DETR is being evaluated as a higher-quality detector candidate.

### Baseline reference

| Parameter | Baseline |
|---|---|
| Detector | YOLOv11n |
| Image size | 320 |
| Confidence | 0.40 |
| AI frame interval | 5 |
| Runtime | PyTorch + Ultralytics |
| Baseline weights SHA-256 | `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` |
| Ultralytics | `8.4.131` |
| PyTorch | `2.13.0+cpu` |
| Baseline Git commit | `6e347ad98fc0e7c467a4377bed3357922687f511` |

### RF-DETR objective

RF-DETR is treated as an experimental replacement candidate, not automatically as the winner.

It must prove improvement on the same frozen benchmark under comparable:

- dataset
- class mapping
- IoU threshold
- confidence policy
- image resolution
- hardware
- measurement methodology

---

## 10. Why a Detector + Tracker Architecture?

A detector tells us **what is present now**.

A tracker gives us **continuity over time**.

For surveillance, continuity matters because the operator needs to see:

```text
CAM-001
   ↓
person detected
   ↓
track created
   ↓
track persists
   ↓
track enters restricted zone
   ↓
alert generated
   ↓
evidence attached
```

Without tracking, the system can repeatedly treat one person as many different detections.

---

## 11. Identity Model

### IBVAP uses camera-qualified track identity

The platform does **not** equate object-tracking identity with human biometric identity.

A surveillance object receives a camera-qualified identifier such as:

```text
CAM-001:P-024
CAM-002:V-007
```

This means:

- `CAM-001` → physical camera/sensor context
- `P-024` → local person track identifier
- `V-007` → local vehicle track identifier

### Why this identity model?

Because a border-surveillance tracker needs a stable **operational reference**, not an unsupported claim that the object is the same real-world person across unrelated cameras.

### Comparison

| Identity approach | Advantage | Disadvantage | IBVAP position |
|---|---|---|---|
| Frame-local detection ID | Very simple | No temporal continuity | Insufficient |
| Global sequential ID | Easy to display | Can collide / lacks camera context | Weak |
| Camera-local tracker ID | Efficient | Only meaningful within camera | Good |
| **Camera-qualified track ID** | Traceable, collision-resistant, audit-friendly | Does not prove cross-camera identity | **Chosen** |
| Face biometric identity | Can identify a person | Privacy, accuracy, pose, lighting, enrollment, legal/governance complexity | Separate gated subsystem |
| Cross-camera re-identification | Potential global continuity | Domain shift, identity errors, costly compute, privacy risk | Future/controlled research |

### Key principle

> **Tracking identity is not the same thing as human identity.**

This separation is especially important for a trustworthy surveillance platform.

---

## 12. Forensic Traceability & Data Integrity

A major differentiator of IBVAP is that the platform does not treat AI output as an isolated prediction.

### ANPR provenance

A plate result can retain:

- Camera ID
- Track ID
- Source frame ID
- Timestamp
- Vehicle bounding box
- Plate bounding box
- OCR confidence
- Raw OCR candidates
- Crop/evidence reference
- Watchlist result

### Face-processing provenance

Face events can retain:

- Source frame ID
- Face bounding box
- Detection/quality score
- Camera/track context
- Review state

### Evidence integrity

Evidence files are associated with:

- SHA-256 hash
- Capture timestamp
- Camera ID
- Event ID
- Data origin

This allows later verification that an evidence artifact was not silently modified.

---

## 13. LIVE / DEMO / TEST Data Isolation

IBVAP explicitly separates data origins.

```text
LIVE
DEMO
TEST
IMPORTED
```

### Why?

A hackathon demonstration often needs synthetic or seeded events. Those records must not alter:

- live alert totals
- live history
- operational risk statistics
- ANPR history
- forensic records presented as real

### Design rule

> **Demo mode must never create fake operational truth.**

---

## 14. Ground-Truth Benchmarking

AI accuracy is not declared from visual impressions.

IBVAP uses a formal ground-truth workflow:

```mermaid
flowchart LR
    V[VIRAT / CCTV Videos]
    S[Representative Frame Sampling]
    A[Human Annotation]
    Q[Annotation Validation]
    F[Frozen Ground Truth]
    B[Baseline Evaluation]
    R[Metric Report]
    O[Model Optimization]
    C[Re-evaluation]

    V --> S --> A --> Q --> F --> B --> R --> O --> C --> F
```

### Benchmark rules

1. Ground truth is human-reviewed.
2. AI predictions remain separate from labels.
3. Prelabels may assist human review but do not become ground truth automatically.
4. The benchmark is frozen before comparing models.
5. Model comparisons use the same evaluation protocol.
6. No metric is fabricated when annotations are missing.

### Prior benchmark snapshot

A previously frozen evaluation cycle reported:

- 196 annotated frames
- 1,098 person boxes
- 102 vehicle boxes
- Person recall: 11.9%
- Vehicle recall: 72.5%
- 23 person false positives

These values are useful as a **historical baseline snapshot**. They should be regenerated whenever the benchmark data is recreated or materially changed.

---

## 15. AI Evaluation Metrics

The benchmark should report, at minimum:

### Per class

- Precision
- Recall
- F1
- mAP@0.50
- mAP@0.50:0.95

### Operational metrics

- False alerts per hour
- Missed zone crossings
- Track ID switches
- Detection latency
- P50/P95 inference latency
- AI FPS
- Frame age
- Dropped AI frames

### Why this matters

A model can have strong mAP and still be unsuitable for operations if:

- it is too slow,
- it causes too many false alarms,
- it drops important small objects,
- it loses tracks under occlusion,
- or it cannot sustain multiple cameras.

---

## 16. Performance Engineering

IBVAP treats video display and AI inference as separate workloads.

### Decoupled frame pipeline

```text
Camera
  │
  ├──► Latest display frame ─────► UI
  │
  └──► Latest AI frame (queue=1)
            │
            ▼
       AI inference
            │
            ▼
         Tracking
            │
            ▼
      Rules / events
```

### Core optimizations

- `AI_INFERENCE_INTERVAL` controls AI density independently of display.
- Only the latest pending AI frame is kept.
- Old AI work is dropped instead of building a latency backlog.
- OpenCV threading is constrained to avoid CPU oversubscription.
- PyTorch threading is bounded.
- One shared model service per process/GPU is preferred over loading a model per camera.
- JPEG/evidence operations should stay off the capture thread.
- Tracker buffers are tuned for occlusion-heavy scenes.
- AI FPS and display FPS are measured separately.

### Why the dashboard can show low AI FPS

The current architecture can run video ingestion above the AI processing rate by design.

For example:

```text
Camera stream: 15 FPS
AI inference: 4 FPS
AI interval: every 5th frame
```

This can still be correct for a resource-constrained deployment, provided:

- the displayed video remains responsive,
- frame age is bounded,
- events are not delayed beyond operational limits,
- dropped-frame behavior is measured,
- and the detector accuracy remains adequate.

---

## 17. Tracking Optimization

Tracking quality affects both accuracy and operator trust.

### Key goals

- Reduce ID switches
- Preserve tracks during short occlusions
- Avoid creating excessive new tracks
- Prevent duplicate alerts
- Maintain camera-qualified identity
- Handle people and vehicles separately where appropriate

### Tracker configuration strategy

IBVAP maintains tracker configuration outside application code so that tuning can be benchmarked and versioned.

Example configuration direction:

```text
Higher track buffer
        ↓
Better short-term occlusion survival
        ↓
Fewer identity switches
        ↓
Potentially more stale-track risk
```

Therefore tracker tuning must be validated against real benchmark sequences rather than chosen by intuition alone.

---

## 18. Virtual Fence / Restricted Zone Logic

Zone definitions are stored in normalized coordinates rather than raw pixels.

```text
Image width  = W
Image height = H

normalized point:
(x / W, y / H)
```

This makes zones portable across resolutions.

### Zone validation should reject

- self-intersecting polygons
- duplicate points
- zero-area polygons
- malformed polygons
- source-resolution mismatch
- degenerate fences

### Operational safeguards

- entry/exit debounce
- cooldowns
- hysteresis
- per-track event state
- configurable severity
- evidence capture
- operator acknowledgment

---

## 19. Dashboard / Command Center

IBVAP provides a command-center interface designed for fast situational awareness rather than generic analytics.

### Core views

- Camera directory
- Live multi-camera grid
- Focused camera view
- Tactical/map view where geospatial data is actually available
- Active alerts
- Tracks
- ANPR
- System health
- Event history
- Evidence context
- Live/demo visibility indicators

### Dashboard design philosophy

The operator should answer these questions in seconds:

1. **What is happening?**
2. **Where is it happening?**
3. **How serious is it?**
4. **Which camera saw it?**
5. **What evidence exists?**
6. **Is the AI/current system healthy?**

### Truthful UI principle

If geographic information is not available, IBVAP explicitly shows:

> **Geospatial view unavailable**

It does not invent coordinates.

---

## 20. Security Architecture

Security is a first-class part of IBVAP because the platform processes surveillance data.

### Implemented / validated hardening

- Fail-fast production secret configuration
- Shorter access-token lifespan
- Secure cookie configuration for HTTPS deployment
- Authenticated WebSocket handshake
- PostgreSQL/Redis host-port isolation in deployment
- Security scanning in CI
- Production guard against PostgreSQL being replaced by SQLite
- Readiness audit script

### Security flow

```mermaid
flowchart TD
    U[Operator] -->|Credentials| Auth[Authentication]
    Auth --> Token[Short-lived Access Token]
    Token --> API[Protected API]
    Token --> WS[Authenticated WSS]
    API --> RBAC[Authorization]
    RBAC --> Events[Security Events]
    RBAC --> Evidence[Evidence Access]
    Events --> Audit[Audit Trail]
    Evidence --> Hash[SHA-256 Integrity]
```

---

## 21. Production Guard Rails

Production is not allowed to silently degrade into an unsafe configuration.

### Example rule

```text
Environment = production
            +
DATABASE_URL = sqlite
            ↓
        FAIL CLOSED
```

The application explicitly rejects this configuration rather than pretending that SQLite is an acceptable shared production database.

### Production readiness checks

The readiness audit covers:

- target data/evidence directories
- filesystem writability
- PostgreSQL connectivity
- Redis connectivity
- insecure/default secret detection
- deployment configuration sanity

---

## 22. Reliability Engineering

IBVAP is designed around failure as a normal operational condition.

### Camera failures

- timeout detection
- frozen-frame detection
- reconnect logic
- exponential backoff
- jitter
- per-camera isolation

### Backend failures

- service health endpoints
- database checks
- Redis checks
- worker lifecycle management
- graceful shutdown

### Observability targets

The operator should be able to see:

- camera count
- display FPS
- AI FPS
- frame age
- P50/P95 latency
- CPU
- RAM
- GPU
- VRAM
- queue state
- database state
- ANPR queue state

---

## 23. Difficulties and How IBVAP Handles Them

| Difficulty | Why it is hard | IBVAP response |
|---|---|---|
| Small/distant persons | Few pixels available | Higher-quality detector experiments + benchmark by object size |
| Occlusion | Objects disappear temporarily | Tracker buffering and lifecycle state |
| Shadows/poles/reflections | Cause false positives | Ground-truth evaluation + hard-negative analysis |
| Night conditions | Low SNR and contrast | Night-specific benchmark and preprocessing path |
| Multi-camera compute | AI can saturate CPU/GPU | Shared model workers + frame decoupling |
| AI backlog | Creates stale alerts | Queue size 1 / latest-frame policy |
| Unreliable camera | Stream may freeze/disconnect | Health checks + reconnect |
| Demo data contamination | Fake events can look real | Explicit data-origin field |
| Forensic integrity | Evidence can be altered | SHA-256 evidence hashes |
| SQLite/PostgreSQL differences | DB extensions differ | PostgreSQL for shared/pilot deployments; SQLite for isolated tests |
| Geospatial uncertainty | Coordinates may be missing | Explicit unavailable state instead of fabrication |
| Face recognition risk | Accuracy/privacy concerns | Quality gates + human review + explicit availability |
| AI benchmark leakage | Model can validate itself | Independent human-reviewed GT |

---

## 24. What Makes IBVAP Unique?

IBVAP is not differentiated simply by "using AI."

The stronger differentiation is the **combination of operational correctness + AI + forensic traceability**.

### 1. Software-defined surveillance

Adds intelligence to existing CCTV instead of assuming that every camera must be replaced.

### 2. Truthful operations

Unavailable geospatial or biometric information is shown as unavailable rather than synthesized.

### 3. Forensic lineage by design

An alert can be traced back to its source frame and evidence.

### 4. Camera-qualified tracking identity

Tracking IDs are explicitly scoped to a sensor context.

### 5. AI evaluation discipline

Models are compared against a frozen human-reviewed benchmark instead of subjective screenshots.

### 6. LIVE/DEMO isolation

Hackathon simulation does not contaminate live operational metrics.

### 7. Resource-aware video AI

AI inference is decoupled from stream display so that AI load does not unnecessarily stall the operator feed.

### 8. Production guardrails

Unsafe configurations are rejected instead of merely documented.

---

## 25. Technology Stack

> This table intentionally separates technologies used in the platform from future/experimental technologies.

| Layer | Technology / Approach |
|---|---|
| Frontend | React + TypeScript |
| Styling/UI | Tailwind CSS / reusable dashboard components |
| Backend API | FastAPI |
| Database | PostgreSQL |
| Cache / messaging | Redis |
| AI runtime | PyTorch |
| Baseline detector | Ultralytics YOLOv11n |
| Candidate detector | RF-DETR |
| Tracking | Multi-object tracking with configurable tracker |
| Computer vision | OpenCV |
| ANPR | Plate detection + OCR pipeline |
| Face processing | Dedicated face pipeline with quality gates |
| Evidence integrity | SHA-256 |
| Migrations | Alembic |
| Containers | Docker / Docker Compose |
| Testing | Pytest |
| Frontend validation | npm build |
| CI/CD | GitHub Actions |
| Security scanning | Bandit + npm audit and related CI gates |
| Streaming direction | WebRTC / MediaMTX preferred; MJPEG compatibility path |
| Benchmark format | YOLO annotation format |

---

## 26. Suggested Repository Structure

```text
IBVAP/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── stores/
│       ├── hooks/
│       └── ...
│
├── configs/
│   └── bytetrack.yaml
│
├── scripts/
│   ├── extract_benchmark_frames.py
│   ├── format_benchmark_structure.py
│   ├── generate_prelabels.py
│   ├── validate_ground_truth_annotations.py
│   ├── evaluate_baseline.py
│   └── check_production_readiness.py
│
├── benchmark/
│   ├── images/
│   ├── labels/
│   ├── annotations/
│   │   └── prelabels/
│   ├── data.yaml
│   └── results/
│
├── docs/
│   ├── benchmark/
│   ├── validation/
│   └── ...
│
├── data/
│   ├── videos/
│   └── evidence/
│
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── package.json
└── README.md
```

> Adjust this tree to the exact repository layout before publishing a final version. README structure must never claim files that do not exist.

---

## 27. Development Workflow

```mermaid
flowchart TD
    P[Problem Analysis] --> A[Architecture]
    A --> I[Implementation]
    I --> T[Automated Tests]
    T --> B[Benchmark Dataset]
    B --> G[Human Ground Truth]
    G --> E[AI Evaluation]
    E --> O[Optimization]
    O --> E
    E --> V[Production Validation]
    V --> D[SIH Demonstration]
```

---

## 28. Validation Strategy

IBVAP uses five controlled phases.

| Phase | Goal | Exit condition |
|---|---|---|
| P0 | Truthful demo + buildable platform | UI/build/tests/health/data isolation |
| P1 | Security hardening | No default secrets, authenticated WSS, secure deployment path |
| P2 | Data integrity | Full event/evidence lineage |
| P3 | AI + performance | Measured detection accuracy and stable multi-camera performance |
| P4 | Production readiness | Soak/load/security/recovery/DR evidence |

### Current validation status

| Area | Status |
|---|---|
| Security | GREEN |
| AI | AMBER |
| Performance | AMBER |
| Data Integrity | GREEN |
| Reliability | GREEN |
| SIH Demo | READY |
| Pilot | READY |
| Production | CONDITIONAL |

A previous project assessment recorded **95/100** overall with **0 critical** and **0 high** unresolved issues. The score should be treated as a validation snapshot, not a permanent guarantee.

---

## 29. Known Limitations

IBVAP intentionally documents limitations rather than hiding them.

### AI accuracy

The model must continue to be evaluated on representative border-like CCTV footage, including difficult conditions.

### Performance

A physical multi-camera soak test on the actual deployment hardware is still the strongest route to a GREEN performance rating.

### Model integrity

A startup checksum verification pipeline for AI weights should remain part of the production hardening roadmap.

### Backup and recovery

PostgreSQL and evidence backup/restore orchestration must be operationally tested, not merely designed.

### HTTPS/WSS

A local reverse proxy such as NGINX or Traefik should be used to physically validate the full TLS/WebSocket deployment path.

### Biometric capabilities

Face recognition should remain explicitly gated by quality, governance, and human-review requirements.

---

## 30. Security, Privacy and Ethical Principles

IBVAP should never turn a technically possible feature into an unjustified claim.

### Principles

- Minimize retained biometric data.
- Do not silently enroll unknown faces.
- Require appropriate human review for sensitive actions.
- Separate detection from identity claims.
- Keep audit trails for sensitive evidence access.
- Use configurable retention/deletion policies.
- Encrypt sensitive evidence at rest for pilot/production.
- Do not present simulated records as live truth.
- Do not fabricate coordinates or identities.

---

## 31. Future Scope

### Near term

- Complete RF-DETR benchmark comparison
- Fine-tune detector on the frozen IBVAP ground truth and expanded hard-negative dataset
- Add difficult-condition evaluation buckets
- Add model checksum verification at startup
- Complete physical multi-camera soak testing
- Add automated database/evidence backup and restore drills
- Validate HTTPS/WSS behind a reverse proxy

### Medium term

- Better small-object detection
- Camera-specific calibration
- Improved night/low-light processing
- Cross-camera object re-identification under strict confidence controls
- Advanced suspicious-activity modeling
- Predictive camera/network health
- Edge inference optimization
- ONNX/TensorRT or equivalent deployment optimization where supported

### Long term

- Federated multi-BOP surveillance
- Sensor fusion
- Thermal-camera integration
- Drone-assisted perimeter awareness
- Advanced geospatial intelligence
- Privacy-preserving biometric search
- Multi-site command-and-control federation
- Hardware-accelerated edge appliances

---

## 32. Why Not Just Use a Larger Model?

A larger model is not automatically a better surveillance system.

Increasing model size may improve detection quality but can also increase:

- inference latency
- memory usage
- GPU requirements
- thermal/power requirements
- deployment cost
- queue pressure

IBVAP therefore optimizes for:

```text
Accuracy
   ×
Latency
   ×
Reliability
   ×
Resource efficiency
   ×
Operational usefulness
```

The best model is the one that delivers the required operational outcome under the declared deployment constraints.

---

## 33. Why Not Use AI-Generated Ground Truth?

Because that creates a circular benchmark.

```text
Model A creates labels
       ↓
Model B is evaluated against those labels
       ↓
Metrics can reflect shared model bias
```

IBVAP instead uses:

```text
Human-reviewed ground truth
       ↓
Frozen benchmark
       ↓
Independent model predictions
       ↓
Objective evaluation
```

AI-generated prelabels are acceptable as **annotation assistance**, but only after human verification and approval.

---

## 34. Demo Scenario

A strong SIH demonstration should show one complete operational story rather than a collection of disconnected screens.

### Suggested demo narrative

```text
1. Standard CCTV feed is opened
        ↓
2. Person/vehicle detected
        ↓
3. Track established
        ↓
4. Subject approaches restricted zone
        ↓
5. Virtual-fence crossing is detected
        ↓
6. Risk/alert event generated
        ↓
7. Evidence snapshot/clip captured
        ↓
8. SHA-256 integrity metadata recorded
        ↓
9. Alert appears in Command Center
        ↓
10. Operator reviews and acknowledges
```

This tells the judge **what happened, why it matters, how AI contributed, and how the system proves the event afterward.**

---

## 35. What an AI Judge May Ask — and the Answers

### Q1. What problem are you solving?

We convert conventional CCTV into software-defined intelligent surveillance so operators do not have to manually monitor every feed continuously.

### Q2. Why existing CCTV?

Because installed camera infrastructure is valuable and replacing every camera with specialized smart hardware is costly and operationally difficult.

### Q3. What makes IBVAP different?

The combination of multi-camera AI perception, camera-qualified tracking identity, truthful operational UI, forensic evidence lineage, cryptographic integrity, live/demo isolation, and resource-aware inference.

### Q4. Why RF-DETR?

It is being evaluated as a higher-quality detector candidate against the immutable baseline. It must prove improvement on the same ground-truth benchmark before being promoted.

### Q5. Why not YOLO?

YOLOv11n is an established baseline in IBVAP. It remains the reference model until another detector demonstrates measurable improvement under the same conditions.

### Q6. How do you measure accuracy?

Using human-reviewed ground truth and reporting Precision, Recall, F1, mAP@0.50, mAP@0.50:0.95, false alerts, missed events, and tracking metrics.

### Q7. How do you prevent stale AI frames?

The AI queue is deliberately bounded; old pending frames are dropped so latency does not grow indefinitely.

### Q8. How do you handle many cameras?

Inference is decoupled from display, model services are shared per worker/GPU process, processing density is configurable, and resource usage is continuously monitored.

### Q9. Can you prove an alert really came from a camera?

Yes. Event records can maintain source frame/camera/track context, while evidence is stored with SHA-256 integrity metadata.

### Q10. Are simulated alerts mixed with live alerts?

No. Data origin is explicitly tracked so DEMO and LIVE records remain separated.

### Q11. Can the map show any camera anywhere?

No. If geospatial metadata/calibration is unavailable, the UI explicitly says geospatial view is unavailable instead of inventing coordinates.

### Q12. Can tracking identity identify a real human?

No. A camera-qualified tracker identity means temporal object continuity within a sensor context. Biometric identity is a separate gated subsystem.

### Q13. What happens if the camera disconnects?

The platform should detect the failure, expose the degraded state, attempt controlled reconnects, and avoid presenting stale frames as current truth.

### Q14. Why is production only conditional?

Because production readiness must include physical soak testing, backup/restore drills, actual HTTPS/WSS validation, model-integrity verification, and deployment-hardware evidence.

---

## 36. Testing

### Backend

```bash
pytest -q
```

### Frontend

```bash
npm run build
```

### Ground-truth validation

```bash
python scripts/validate_ground_truth_annotations.py
```

### Baseline evaluation

```bash
python scripts/evaluate_baseline.py
```

### Production readiness

```bash
python scripts/check_production_readiness.py
```

> Run commands from the repository root or the exact paths defined by the current project layout.

---

## 37. Benchmark Lifecycle

```text
RAW VIDEOS
   ↓
Representative frame extraction
   ↓
Dataset structure normalization
   ↓
Human annotation
   ↓
Annotation validation
   ↓
Ground-truth freeze
   ↓
Baseline detector
   ↓
RF-DETR candidate
   ↓
Fine-tuning
   ↓
Objective comparison
   ↓
Champion model selection
   ↓
Deployment validation
```

### Golden rule

> **Never change the benchmark to make a model look better.**

---

## 38. Reproducibility

Every serious benchmark should record:

- Git commit
- Model weights checksum
- Model architecture/version
- Runtime versions
- Device
- Image size
- Confidence threshold
- IoU threshold
- Dataset version
- Ground-truth version
- Tracker configuration
- AI frame interval
- Timestamp
- Hardware details

This makes model comparisons reproducible and defensible.

---

## 39. Model Promotion Policy

A new AI model should be promoted only when it:

1. Beats the baseline on the same frozen ground truth.
2. Does not introduce unacceptable false-alert rates.
3. Maintains or improves tracking continuity.
4. Meets the latency/resource budget.
5. Passes difficult-condition evaluation.
6. Has a recorded model checksum.
7. Has a reproducible evaluation record.

### Example

```text
RF-DETR
  │
  ├─ Accuracy ↑
  ├─ False alerts ↓
  ├─ ID switches ↓
  ├─ Latency acceptable
  ├─ Memory acceptable
  └─ Deployment stable
          ↓
     PROMOTE
```

Otherwise:

```text
REJECT / RETUNE / RE-EVALUATE
```

---

## 40. Project Status

### SIH

**READY**

### Pilot

**READY**

### Production

**CONDITIONAL**

### Current priorities

1. Physical multi-camera performance validation
2. RF-DETR accuracy evaluation and fine-tuning
3. Model checksum enforcement
4. Automated backup/recovery
5. End-to-end HTTPS/WSS validation

---

## 41. Documentation Map

Recommended documentation locations:

```text
docs/
├── benchmark/
│   ├── GROUND_TRUTH_DATASET.md
│   ├── ANNOTATION_GUIDELINES.md
│   ├── ANNOTATION_PROGRESS.md
│   ├── BENCHMARK_VERSION.md
│   ├── BASELINE_MODEL_STATE.md
│   └── BASELINE_AI_EVALUATION_REPORT.md
│
└── validation/
    ├── P0_REMEDIATION_REPORT.md
    ├── P3_PERFORMANCE_VALIDATION.md
    └── IBVAP_FINAL_VALIDATION_REPORT.md
```

Keep these reports synchronized with the actual repository contents.

---

## 42. Recommended GitHub Presentation

For the public repository, the first screen should communicate:

```text
IBVAP
Intelligent Border Video Analytics Platform

Existing CCTV
        +
AI Detection
        +
Tracking
        +
Virtual Fence
        +
ANPR
        +
Forensic Evidence
        =
Actionable Border Surveillance
```

Recommended repository sections:

- Project overview
- Problem statement
- Architecture
- Feature list
- AI pipeline
- Benchmark methodology
- Results
- Security
- Deployment
- Demo screenshots/video
- Limitations
- Future roadmap
- FAQ
- Team
- License

---

## 43. Important Honesty Rule

This README is intended to be **judge-ready and technically defensible**.

Do not claim:

- production-scale performance without measured hardware evidence
- face-recognition accuracy without a validated benchmark
- geolocation without camera metadata/calibration
- a model is better merely because it visually looks better
- 24-hour reliability without a 24-hour test
- perfect detection
- zero false positives
- production readiness when required deployment controls are still conditional

For a surveillance platform, a truthful limitation is stronger than an exaggerated claim.

---

## 44. References

### Smart India Hackathon 2026

Problem statement reference:

- **SIH26187 — AI-Based Intelligent Video Analytics Platform for Border Surveillance using existing CCTV Infrastructure**
- Ministry of Home Affairs
- Department: SSB, Police II Division
- Category: Software
- Theme: Smart Automation

Reference source used while preparing this README: SIH 2026 problem-statement archive and project validation material.

### Project validation sources

Use the repository's own validation artifacts as the authoritative project evidence:

- `docs/validation/P0_REMEDIATION_REPORT.md`
- `docs/validation/P3_PERFORMANCE_VALIDATION.md`
- `docs/validation/IBVAP_FINAL_VALIDATION_REPORT.md`
- `docs/benchmark/BASELINE_AI_EVALUATION_REPORT.md`
- `docs/benchmark/BASELINE_MODEL_STATE.md`

---

## 45. Conclusion

IBVAP is designed around one operational objective:

> **Turn existing CCTV into trustworthy, scalable, AI-assisted situational awareness.**

The project does not treat AI detection as the end product.

The complete value chain is:

```text
Video
  ↓
Perception
  ↓
Tracking
  ↓
Context
  ↓
Risk
  ↓
Alert
  ↓
Evidence
  ↓
Operator Decision
  ↓
Auditability
```

That is the foundation of IBVAP's approach to intelligent border surveillance.

---

## License

Add the final project license before public release. For a university/hackathon repository, choose a license that matches the team's ownership, institutional rules, third-party model/data licenses, and any restrictions attached to surveillance datasets or model weights.

---

## Disclaimer

IBVAP is a research/prototype platform developed for the Smart India Hackathon 2026 context. Public documentation must distinguish prototype capability, benchmark evidence, pilot readiness, and production readiness. Any deployment involving real surveillance or biometric data must comply with applicable law, policy, security controls, data-retention requirements, and organizational authorization.
