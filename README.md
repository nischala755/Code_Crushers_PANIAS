# UBID Mesh — Unified Business Identity & Active Intelligence Platform

> **A production-grade government intelligence system for entity resolution, business monitoring, and cross-departmental data unification across Karnataka state.**

[![Live Demo - Frontend](https://img.shields.io/badge/Frontend-Vercel-black)](https://ubidmesh.vercel.app)
[![Live Demo - Backend](https://img.shields.io/badge/Backend-Render-blue)](https://ubidmesh-api.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com)

---

## Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [System Architecture](#-system-architecture)
- [Core Features](#-core-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Demo Flow](#-demo-flow)
- [API Documentation](#-api-documentation)
- [AI/ML Pipeline](#-aiml-pipeline)
- [Data Model](#-data-model)
- [Deployment](#-deployment)
- [Team](#-team)

---

## 🎯 Problem Statement

In India, businesses register independently across multiple government departments — Shops & Establishment, Factories & Boilers, Labour, and Pollution Control Board. Each department maintains its own siloed database with no cross-referencing. This leads to:

- **Duplicate identities**: Same business registered with slight name/address variations across departments
- **No unified view**: Officers cannot see the complete regulatory picture of a business
- **Undetected dormancy**: Inactive or closed businesses remain in active registries
- **Missed inspections**: No cross-departmental visibility into compliance gaps
- **Manual reconciliation**: Officers spend hours manually matching records

**UBID Mesh solves this** by creating a unified identity layer that automatically links business records across departments using AI-powered entity resolution.

---

## 💡 Solution Overview

UBID Mesh is a **Unified Business Identity (UBID)** platform that:

1. **Ingests records** from 4 Karnataka state departments
2. **Resolves entities** using weighted multi-signal matching (PAN, GSTIN, name similarity, address overlap, phone)
3. **Assigns unique UBIDs** — a single identity per business, regardless of how many departments it appears in
4. **Classifies activity** — Active, Dormant, or Closed based on event history
5. **Scores risk** — Low, Medium, High with actionable recommendations
6. **Enables natural language queries** — Officers can ask questions in plain English
7. **Provides explainable AI** — Every match decision shows signal-level breakdown
8. **Learns from reviewers** — System weights adjust based on human feedback

### Key Differentiators

| Feature | Description |
|---------|-------------|
| **Explainable Matching** | Every match shows PAN, GSTIN, name, address, phone signal scores |
| **Learning Effect** | Reviewer decisions adjust system weights in real-time |
| **Activity Inference** | Classifies businesses using multi-department event analysis |
| **Risk Intelligence** | Composite risk scoring with inspection gap detection |
| **Natural Language Queries** | Mistral AI-powered query interpretation |
| **Full Audit Trail** | Append-only log of all system actions and decisions |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  Dashboard │ Registry │ Review │ Query │ Graph │ Audit   │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────┐
│                   BACKEND (FastAPI)                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │           Entity Resolution Engine                │    │
│  │  Normalizer → Blocker → Matcher → Resolver        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐    │
│  │  Activity    │ │   Risk       │ │   Learning     │    │
│  │  Inference   │ │   Scoring    │ │   Simulator    │    │
│  └─────────────┘ └──────────────┘ └────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Mistral AI Integration                    │    │
│  │    Query Interpretation │ Explanation Generation   │    │
│  └──────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                  DATA LAYER (SQLite)                      │
│  DepartmentRecords │ UBIDs │ MatchEvidence │ Events      │
│  ActivityClassification │ ReviewDecisions │ AuditLog     │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│              SYNTHETIC DATA GENERATOR                    │
│  300+ records │ 4 departments │ Realistic Indian data    │
│  Deliberate overlaps │ Name/address variations           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔥 Core Features

### 1. Entity Resolution Pipeline

The core AI engine that links business records across departments.

| Stage | Method | Details |
|-------|--------|---------|
| **Normalize** | Regex + rules | Name cleaning (remove Pvt Ltd, etc.), address standardization (Rd→Road, Blr→Bengaluru) |
| **Block** | Multi-key | Name prefix + pincode, PAN, phone number, name + city |
| **Match** | Weighted scoring | PAN (35%), GSTIN (25%), Name-Jaro Winkler (20%), Address-Jaccard (10%), Phone (10%) |
| **Cluster** | Union-Find | Transitive closure for multi-record groups |
| **Assign** | Sequential | KA-UBID-00001 format, primary record selection |

**Decision Thresholds:**
- `≥ 0.85` → Auto-linked (no human review needed)
- `0.60 – 0.85` → Review (sent to reviewer queue)
- `< 0.60` → Separate (different businesses)

### 2. Explainable Matching Engine

Every match pair shows:
- Individual signal scores (PAN, GSTIN, Name, Address, Phone)
- Visual signal bars with color coding
- Weighted total score
- Decision category (Auto-linked / Review / Separate)

### 3. UBID Registry

Central screen showing all unified business identities:
- Filterable by department, activity status, risk level, city
- Click-through to full detail with linked records, evidence, activity, risk
- Sortable columns with pagination

### 4. Reviewer Workflow

- Queue of pending review pairs sorted by confidence
- Side-by-side record comparison modal
- Signal breakdown visualization
- One-click actions: **Confirm Merge** / **Reject** / **Defer**
- Learning effect banner after each decision

### 5. Learning Effect (Simulated)

When a reviewer confirms or rejects a match:
- System adjusts matching weights (±2% learning rate)
- Shows before/after confidence scores
- Displays updated weight distribution
- Audit log records the learning event

### 6. Activity Inference Engine

Classifies each UBID based on aggregated event history:
- **Active**: Event within last 6 months
- **Dormant**: No event in 6–24 months
- **Closed**: No event in 24+ months or explicit closure

Shows reasoning: last activity date, days since activity, signals present/missing.

### 7. Risk Intelligence

Composite risk scoring based on:
- Activity status (dormant/closed = higher risk)
- Missing inspections (>18 months = high risk)
- Data inconsistencies across departments
- Low linking confidence
- Missing compliance signals (license renewal, ESI/PF)

Output: **Low / Medium / High** + reasons + recommendation (Inspect / Monitor / No Action)

### 8. Natural Language Query Interface

Officers can type queries like:
- *"Active factories in pincode 560058 with no inspection in 18 months"*
- *"Dormant businesses in Bengaluru"*
- *"High risk establishments in Mysuru"*

Powered by **Mistral AI** for query interpretation with keyword-based fallback.

### 9. Graph View

Interactive D3.js force-directed network graph:
- Nodes = department records (color-coded by department)
- UBID nodes = dark cluster centers
- Edges = similarity scores
- Drag, zoom, and hover interactions
- Department color legend

### 10. Audit Log

Append-only audit trail tracking:
- Entity resolution runs
- Reviewer decisions (confirm/reject/defer)
- System learning events
- Filterable by category (System, Review, Merge)

---

## 🧠 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.11, FastAPI | REST API, business logic |
| **Database** | SQLite (SQLAlchemy ORM) | Persistent storage, zero-config |
| **Entity Resolution** | Jellyfish (Jaro-Winkler), custom scoring | Name similarity, weighted matching |
| **AI/LLM** | Mistral AI (mistral-small-latest) | Query interpretation, explanations |
| **Frontend** | React 18, Vite | Single-page application |
| **Visualization** | D3.js (d3-force) | Network graph |
| **HTTP Client** | Axios | API communication |
| **Routing** | React Router v6 | Client-side navigation |

---

## 📁 Project Structure

```
PANIAS_DEMO/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLite + SQLAlchemy setup
│   ├── seed.py                 # Database seeder (runs full pipeline)
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy ORM models (9 tables)
│   │   └── schemas.py          # Pydantic request/response schemas
│   ├── engine/
│   │   ├── normalizer.py       # Name/address cleaning
│   │   ├── blocker.py          # Multi-key blocking
│   │   ├── matcher.py          # Weighted signal matching
│   │   ├── resolver.py         # Full ER pipeline + UBID assignment
│   │   ├── activity.py         # Activity inference engine
│   │   ├── risk.py             # Risk scoring engine
│   │   └── learner.py          # Learning effect simulator
│   ├── routes/
│   │   ├── registry.py         # UBID registry endpoints
│   │   ├── reviewer.py         # Review workflow endpoints
│   │   ├── query.py            # NL query endpoints
│   │   ├── graph.py            # Graph data endpoints
│   │   └── audit.py            # Audit log endpoints
│   └── services/
│       └── mistral_service.py  # Mistral AI integration
├── datagen/
│   ├── generator.py            # Main dataset generator
│   ├── indian_data.py          # Indian names, addresses, IDs
│   └── event_generator.py      # Activity event history
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx            # React entry point
│       ├── App.jsx             # Router setup
│       ├── index.css           # Government design system
│       ├── api/client.js       # Axios API client
│       ├── components/
│       │   └── Layout.jsx      # Sidebar + header layout
│       └── pages/
│           ├── Dashboard.jsx   # System overview
│           ├── Registry.jsx    # UBID registry table
│           ├── EntityDetail.jsx # Full UBID detail view
│           ├── ReviewQueue.jsx  # Reviewer workflow
│           ├── QueryInterface.jsx # NL query
│           ├── GraphView.jsx   # Network graph
│           └── AuditLog.jsx    # Audit trail
├── data/                       # Generated data + SQLite DB
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### 1. Clone the Repository

```bash
git clone https://github.com/nischala755/Code_Crushers_PANIAS.git
cd Code_Crushers_PANIAS
```

### 2. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Seed the Database

This generates synthetic data, runs entity resolution, activity inference, and risk scoring:

```bash
python -m backend.seed
```

Expected output:
```
=== UBID Mesh Database Seeder ===
Seeding 300 records into database...
[OK] Seeded 300 department records
[ER] Entity resolution complete. 191 UBIDs created.
[ACTIVITY] Classification complete: {ACTIVE: 122, DORMANT: 42, CLOSED: 27}
[RISK] Risk scoring complete: {MEDIUM: 70, LOW: 112, HIGH: 9}
=== Seeding Complete ===
```

### 4. Start the Backend

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

API available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 6. Start the Frontend

```bash
npm run dev
```

Frontend available at: `http://localhost:5173`

---

## 🎬 Demo Flow

Follow this sequence for the hackathon demo:

### Step 1: Dashboard Overview
Navigate to the **Dashboard**. Shows total UBIDs, records, pending reviews, activity distribution, and risk breakdown.

### Step 2: UBID Registry
Click **UBID Registry**. Browse the master table of all unified identities. Use filters (department, status, risk) to narrow down.

### Step 3: Entity Detail
Click any UBID row to see:
- Business information (PAN, GSTIN, owner, address)
- All linked department records
- Match evidence with signal breakdown bars
- Activity classification with reasoning
- Risk intelligence with recommendation

### Step 4: Reviewer Workflow
Navigate to **Review Queue**. Click "Review" on any pending pair:
- See side-by-side record comparison
- View signal breakdown (PAN, Name, Address, etc.)
- Click **Confirm Merge** to approve

### Step 5: Learning Effect
After confirming, observe:
- "System learning: confidence improved" banner
- Before/after confidence scores
- Adjusted weight distribution

### Step 6: Natural Language Query
Navigate to **Query Interface**. Try:
```
Active factories in pincode 560058 with no inspection in 18 months
```
See interpreted filters, results table, and activity reasoning.

### Step 7: Graph View
Navigate to **Graph View**. See the entity resolution network with color-coded department nodes and UBID clusters.

### Step 8: Audit Log
Navigate to **Audit Log**. See the complete trail of system actions, reviewer decisions, and learning events.

---

## 📡 API Documentation

### Registry Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/registry/stats` | Dashboard statistics |
| `GET` | `/api/registry/` | Paginated UBID list with filters |
| `GET` | `/api/registry/count` | Total count for pagination |
| `GET` | `/api/registry/{ubid_code}` | Full UBID detail |

### Review Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/review/queue` | Pending review pairs |
| `GET` | `/api/review/{evidence_id}` | Pair detail with records |
| `POST` | `/api/review/{evidence_id}/decide` | Submit decision |

### Query Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query/` | Natural language query |

### Graph & Audit

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/graph/` | Graph nodes and edges |
| `GET` | `/api/audit/` | Audit log entries |

---

## 🤖 AI/ML Pipeline

### Entity Resolution Algorithm

```
Input: Raw department records (300+)
  │
  ▼
Normalize
  ├── Name: lowercase, remove "Pvt Ltd", normalize whitespace
  └── Address: expand abbreviations (Rd→Road), extract pincode
  │
  ▼
Block (Multi-key)
  ├── Name prefix (4 chars) + Pincode
  ├── PAN (full match)
  ├── Phone number
  └── Name prefix (3 chars) + City
  │
  ▼
Match (Weighted Scoring)
  ├── PAN exact match ────── weight: 0.35
  ├── GSTIN match ─────────  weight: 0.25
  ├── Name (Jaro-Winkler) ── weight: 0.20
  ├── Address (Jaccard) ──── weight: 0.10
  └── Phone exact match ──── weight: 0.10
  │
  ▼
Decide
  ├── ≥ 0.85 → AUTO_LINKED
  ├── 0.60-0.85 → REVIEW
  └── < 0.60 → SEPARATE
  │
  ▼
Cluster (Union-Find with transitive closure)
  │
  ▼
Output: UBIDs with linked records + evidence
```

### Activity Inference

```
For each UBID:
  Aggregate events from all linked records
  │
  Find most recent event date
  │
  ├── Within 6 months ──────── ACTIVE
  ├── 6-24 months gap ──────── DORMANT
  ├── >24 months gap ───────── CLOSED
  └── Explicit closure event ── CLOSED
  │
  Generate reasoning (signals present/missing)
```

### Risk Scoring (0-100)

```
Factor                          Points
──────────────────────────────────────
Dormant status                    +30
No inspection >18 months          +25
No inspection records             +20
Multiple PAN numbers              +15
Low linking confidence (<70%)     +15
Inconsistent names                +10
Missing license renewal           +10
Missing ESI/PF contributions       +5
──────────────────────────────────────
≥60 = HIGH  │  30-59 = MEDIUM  │ <30 = LOW
```

---

## 📊 Data Model

### Synthetic Dataset

- **120 base businesses** → 300+ department records
- **4 departments**: Shop & Establishment, Factories, Labour, Pollution Board
- **~40% overlap**: Same business in 2+ departments with realistic variations
- **Indian data**: Karnataka names, addresses, valid PAN/GSTIN formats
- **Event history**: 8-20 events per business across license renewals, inspections, filings, contributions

### Database Schema (9 tables)

| Table | Records | Description |
|-------|---------|-------------|
| `department_records` | ~300 | Raw records from each department |
| `ubids` | ~190 | Unified business identities |
| `ubid_links` | ~300 | Links UBIDs to department records |
| `match_evidence` | ~450 | Signal-level match scores |
| `activity_events` | ~3000+ | Business activity events |
| `activity_classifications` | ~190 | Inferred activity status |
| `review_decisions` | variable | Reviewer actions |
| `audit_entries` | variable | Append-only audit log |
| `system_weights` | variable | Matching weight history |

---

## ☁️ Deployment

### Backend on Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect the GitHub repository
3. Set **Root Directory** to the project root
4. **Build Command**: `pip install -r backend/requirements.txt && python -m backend.seed`
5. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Environment: Python 3.11

### Frontend on Vercel

1. Import the repository on [vercel.com](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`
5. Add environment variable in `frontend/.env.production`:
   ```
   VITE_API_URL=https://your-render-url.onrender.com/api
   ```

---

## 🧪 Quality Assurance Checklist

### Backend Tests

- [ ] `python -m backend.seed` completes without errors
- [ ] `GET /api/registry/stats` returns valid statistics
- [ ] `GET /api/registry/` returns paginated UBID list
- [ ] `GET /api/registry/{ubid_code}` returns full detail with linked records
- [ ] `GET /api/review/queue` returns pending review pairs
- [ ] `POST /api/review/{id}/decide` processes decision and returns learning effect
- [ ] `POST /api/query/` interprets natural language query
- [ ] `GET /api/graph/` returns nodes and edges
- [ ] `GET /api/audit/` returns audit log entries

### Frontend Tests

- [ ] Dashboard loads with correct statistics
- [ ] Registry table displays all UBIDs with pagination
- [ ] Filters (department, status, risk, search) work correctly
- [ ] Click on UBID row navigates to detail page
- [ ] Entity detail shows all panels (business info, activity, risk, evidence, linked records, timeline)
- [ ] Signal breakdown bars render with correct colors and widths
- [ ] Review queue lists pending pairs
- [ ] Review modal shows side-by-side comparison
- [ ] Confirm/Reject/Defer buttons work
- [ ] Learning effect banner appears after decision
- [ ] Query interface accepts natural language input
- [ ] Example query buttons populate and execute
- [ ] Graph view renders D3 network with zoom/drag
- [ ] Audit log table loads with category filter
- [ ] Sidebar navigation works across all pages
- [ ] No console errors in browser

### Data Quality Tests

- [ ] 300+ records generated across 4 departments
- [ ] Realistic Indian names, Karnataka addresses, valid PAN/GSTIN
- [ ] Deliberate overlaps (~40% businesses in 2+ departments)
- [ ] Name/address variations introduced (typos, abbreviations)
- [ ] Event history generates active/dormant/closed patterns
- [ ] Entity resolution produces ~190 UBIDs from ~300 records
- [ ] Auto-linked count > 100 (high-confidence matches)
- [ ] Review queue has 50+ pending pairs
- [ ] Activity classification: Active > Dormant > Closed distribution
- [ ] Risk scoring: mostly Low, some Medium, few High

---

## 👥 Team

**Team Code Crushers** — PANIAS Hackathon 2025

---

## 📄 License

This project is developed as a hackathon prototype for demonstration purposes. Not for production deployment without further security hardening.
