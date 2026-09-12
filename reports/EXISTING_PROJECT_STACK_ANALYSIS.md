# RESQ-AI — Existing Project Stack Analysis Report

**Generated Date**: 2026-09-12  
**Project**: RESQ-AI Emergency Flood Response System  

---

## 1. Detected Frontend Stack

- **Framework**: Angular 19.2 (`@angular/core`: `^19.2.0`, `@angular/cli`: `^19.2.27`)
- **Language**: TypeScript 5.7.2
- **Package Manager**: `npm`
- **Build System**: Angular CLI (`ng build` / `@angular-devkit/build-angular`)
- **Routing**: Angular Router (`@angular/router`, `src/app/app.routes.ts`)
- **HTTP Client**: Angular `HttpClient` (`src/app/core/services/api.service.ts`)
- **Map Library**: Leaflet 1.9.4 (`leaflet`, `@types/leaflet`) used in Map feature component
- **UI Component Library / Icons**: Angular Material 19.2 (`@angular/material`, `@angular/cdk`), Lucide icons (`lucide-angular`)
- **State Management**: Angular Signals (`signal`, `computed` in `src/app/core/services/disaster-state.service.ts`)
- **Styling**: SCSS (`styles.scss` with CSS variables, modern dark glassmorphism theme)
- **Environment Configuration**: `src/environments/environment.ts` (`apiUrl: '/api/v1'`, `healthUrl: '/health'`)
- **Dev Server Port**: 4200
- **Dev Proxy**: `proxy.conf.json` forwarding `/api` and `/health` to `http://127.0.0.1:8000`

---

## 2. Detected Backend Stack

- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.12+ (Uvicorn 0.24.0)
- **Package Manager**: `pip` (`backend/requirements.txt`)
- **Application Entry Point**: `backend/main.py` (`app = FastAPI(...)`)
- **Controllers / Routers**: `backend/routers/alerts.py`, `backend/routers/locations.py`
- **Database**: SQLite (`flood_response.db` in workspace root) via SQLAlchemy 2.0.23 ORM (`backend/database.py`, `backend/models.py`)
- **Data Validation & DTOs**: Pydantic 2.5.0 (`backend/schemas.py`)
- **Configuration & Settings**: Pydantic Settings 2.1.0 (`backend/config.py`)
- **Security & Authentication**: CORS Middleware in `main.py` (`ALLOWED_ORIGINS` in `config.py`). Placeholder secret key configuration exists for JWT authentication.
- **CORS Configuration**: Allowed origins `http://localhost:3000`, `http://localhost:8000`, `http://localhost:4200`, `http://127.0.0.1:4200`
- **API Architecture**: REST API (`/api/v1/alerts`, `/api/v1/locations`, `/health`)
- **Default Port**: 8000 (`http://127.0.0.1:8000`)

---

## 3. Detected AI Stack

- **Location**: `backend/RESQ-AI` (Python AI intelligence directory embedded directly in backend)
- **Dependencies**: `numpy`, `pandas`, `rasterio`, `tifffile`, `scikit-learn`, `xgboost`, `lightgbm`, `shap`, `pydantic`, `PyYAML`, `python-dotenv`, `pytest`
- **Master Intelligence Entry Point**: `backend/RESQ-AI/inference/decision_contract.py` (`get_city_decision_intelligence()`)
- **Engine Breakdown**:
  - **Risk Engine**: `flood_prediction/predictor.py` & `inference/risk_engine.py` (6-hour predictive flood risk)
  - **Priority Engine**: `priority/emergency_priority/facility_priority.py` (P1-P4 evacuation ranking)
  - **Route Risk Engine**: `route_risk/route_scoring/route_service.py` (FASTEST, SAFEST, BALANCED routes)
  - **Scenario Engine**: `scenario/scenario_engine.py` (What-if rainfall surge & flood depth simulation)
  - **Action Plan Engine**: `action_plan/action_plan_engine.py` (Deterministic rule-based action plan generator with zero-dependency fallback)
  - **Depth Engine**: `flood_depth/depth_engine.py`
  - **Spatial Zones Engine**: `flood_zones/spatial_intersection.py`
  - **Facility Exposure Engine**: `facility/impact_engine.py`
  - **Provenance Engine**: `provenance/provenance_schema.py` (Audit records for IMD, GFSM, CAMELS-IND, IFI, NASA GDIS)
- **Tests**: 15 unit and pipeline integration tests in `backend/RESQ-AI/tests/`

---

## 4. Current Ports & Communication Flow

```
+------------------------+           +--------------------------+           +--------------------------+
|  Angular Frontend      |  HTTP     |  FastAPI Backend Gateway |  In-Proc  |  Python RESQ-AI System   |
|  (Port 4200)           | --------> |  (Port 8000)             | --------> |  (backend/RESQ-AI)       |
|  proxy.conf.json       |  /api/v1  |  /api/v1/ai/...          |  Python   |  decision_contract.py    |
+------------------------+           +--------------------------+           +--------------------------+
```

1. Frontend runs on port `4200` via Angular Dev Server.
2. Angular CLI proxies `/api` and `/health` requests to `http://127.0.0.1:8000`.
3. Backend runs on port `8000` via Uvicorn.
4. Backend handles `/api/v1/alerts`, `/api/v1/locations`, `/health`, and will host `/api/v1/ai/...` (or `/api/ai/...`).
5. Because the Backend is already built with FastAPI (Python), it can directly import and call Python RESQ-AI intelligence functions without needing a separate inter-process HTTP network jump.

---

## 5. Integration Risks & Mitigation Strategies

1. **Python Import Paths**: `backend/RESQ-AI` contains subpackages (`forecast`, `flood_prediction`, `priority`, etc.). We must ensure `sys.path` or package root resolution allows importing these modules cleanly within FastAPI.
2. **LLM Dependency Removal**: `action_plan/config/action_plan.yaml` references OpenAI. Per Phase 14, LLM integration must be disabled and routed exclusively to the deterministic fallback engine `generate_deterministic_fallback_plan()`.
3. **Data Schema Harmonization**: The RESQ-AI decision contract returns rich structured payloads (`risk`, `priority`, `routes`, `scenarios`, `action_plan`, `provenance`). The FastAPI backend must expose endpoints returning these exact data contracts to the Angular frontend.
4. **Angular Frontend State Integration**: The Angular frontend's `DisasterStateService` must fetch real AI results from `/api/v1/ai/decision` (or individual AI endpoints) and bind them to the signals powering the UI.

---

## 6. Recommended Integration Architecture

- **Backend AI Gateway Router**: Add `backend/routers/ai.py` into FastAPI backend, registered under `/api/v1/ai` (and aliased under `/api/ai` for full endpoint compatibility).
- **Exposed Endpoints**:
  - `GET /api/v1/ai/health` (AI Service status)
  - `POST /api/v1/ai/risk` (Risk Engine assessment)
  - `POST /api/v1/ai/priority` (Emergency Priority ranking)
  - `POST /api/v1/ai/routes` (Route Risk intelligence)
  - `POST /api/v1/ai/scenario` (What-If Scenario simulation)
  - `POST /api/v1/ai/decision` (Complete Master Decision Intelligence payload)
- **Frontend AI Service**: Extend `frontend/src/app/core/services/` with `ai-intelligence.service.ts` connecting `DisasterStateService` to the backend AI endpoints.
- **Frontend UI Updates**: Update Dashboard, Action Plan, Route Intelligence, What-If, Priority Queue, and Provenance components to display live deterministic RESQ-AI intelligence.
