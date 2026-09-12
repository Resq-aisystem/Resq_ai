# RESQ-AI — Gemini Integration & Frontend UI Transformation Plan

**Generated Date**: 2026-09-12  
**Project**: RESQ-AI Emergency Flood Response System  

---

## 1. Current Architecture Overview

```
+------------------------+           +--------------------------+           +--------------------------+
|  Angular 19 Frontend   |  HTTP     |  FastAPI Backend Gateway |  In-Proc  |  Python RESQ-AI System   |
|  (Port 4200)           | --------> |  (Port 8000)             | --------> |  (backend/RESQ-AI)       |
|  proxy.conf.json       |  /api/v1  |  routers/ai.py           |  Python   |  decision_contract.py    |
+------------------------+           +--------------------------+           +--------------------------+
```

The existing architecture provides verified numerical decision intelligence (`risk_score`, `priority_score`, `routes`, `scenarios`, `action_plan`, `provenance`). RESQ-AI is the sole numerical source of truth.

---

## 2. Gemini Integration Architecture

```
+------------------+         +------------------+         +------------------+         +------------------+
| Angular 19 UI    |  HTTP   | FastAPI Backend  |  SDK    | Gemini Service   |  HTTPS  | Google Gemini    |
| (Port 4200)      | ------> | (Port 8000)      | ------> | (gemini_service) | ------> | API              |
+------------------+         +------------------+         +------------------+         +------------------+
                                      |
                                      v (Provides Grounded Context Only)
                             +------------------+
                             | Python RESQ-AI   |
                             +------------------+
```

### Architectural Guarantees
1. **Source of Truth**: RESQ-AI retains 100% authority over numerical predictions, risk levels, priority ranks, route metrics, and scenario deltas.
2. **Explanation Layer**: Gemini acts purely as a natural-language synthesizer and coordinator briefing generator.
3. **Strict Grounding**: Gemini is fed only structured JSON payloads from RESQ-AI. It is forbidden from inventing weather observations, water levels, populations, or casualties.
4. **Backend Isolation**: `GEMINI_API_KEY` is loaded strictly on the FastAPI backend from `.env`. The frontend never sees or receives the API key.
5. **Deterministic Fallback**: If Gemini is offline or unconfigured, the system seamlessly displays the verified deterministic RESQ-AI action plan without breaking UI or throwing unhandled errors.

---

## 3. Frontend Architecture & Transformation Strategy

- **Design System**: Emergency Operations Command Center theme (Dark glassmorphism, `#0b1120` canvas, `#0d1527` panels, `#38bdf8` cyan highlights, `#ef4444` critical alerts, `#22c55e` safe indicators).
- **State Management**: Angular Signals (`signal`, `computed`) in `DisasterStateService`.
- **Component Breakdown**:
  - `CommandCenterHeaderComponent`: Status indicators for Backend, RESQ-AI, and Gemini.
  - `KpiCardsComponent`: Key operational metrics.
  - `InteractiveMapComponent`: Leaflet map visualization of risk locations, shelters, and evacuation routes.
  - `PriorityQueueComponent`: Explainable P1-P4 evacuation ranking.
  - `RouteIntelligenceComponent`: FASTEST, SAFEST, BALANCED route comparison.
  - `WhatIfScenarioComponent`: Interactive rainfall surge simulation controls.
  - `GeminiBriefingPanelComponent` **[NEW]**: Grounded Gemini Emergency Coordinator Briefing view.
  - `AiActionPlanComponent`: Grounded deterministic directives & operational steps.
  - `ProvenancePanelComponent`: Audit trail & scientific dataset coverage.

---

## 4. Summary of Files to Modify & Create

### Files to Create
1. `backend/services/__init__.py` — Package init.
2. `backend/services/gemini_service.py` — Backend Gemini API client using `google-generativeai` SDK with grounded prompt engineering.
3. `frontend/src/app/core/models/gemini-briefing.model.ts` — TypeScript models for Gemini briefing response & health.
4. `frontend/src/app/features/gemini-briefing/gemini-briefing-panel.component.ts` — Dedicated Angular component for Gemini briefing display.
5. `reports/RESQ_AI_GEMINI_INTEGRATION.md` — Final integration report.

### Files to Modify
1. `backend/config.py` — Add `GEMINI_API_KEY` and `GEMINI_MODEL` settings.
2. `backend/.env` — Store actual `GEMINI_API_KEY` (git-ignored).
3. `backend/.env.example` — Include template placeholder.
4. `backend/routers/ai.py` — Add `/gemini/briefing` and `/gemini/health` endpoints.
5. `frontend/src/app/core/services/ai-intelligence.service.ts` — Add `getGeminiBriefing()` & `getGeminiHealth()`.
6. `frontend/src/app/core/services/disaster-state.service.ts` — Add `geminiBriefing` and `geminiHealth` signals.
7. `frontend/src/app/features/action-plan/ai-action-plan.component.ts` — Render Gemini briefing tab alongside deterministic plan.
8. `frontend/src/app/features/header/command-center-header.component.ts` — Show Gemini connection status.
9. `test_integration.py` — Test Gemini health and briefing endpoints.

---

## 5. Security & Key Management

- `GEMINI_API_KEY` stored exclusively in `backend/.env`.
- `.env` added to `.gitignore`.
- `.env.example` committed with dummy placeholder string `YOUR_GEMINI_API_KEY_HERE`.
- Frontend API service calls backend proxy endpoint `POST /api/v1/ai/gemini/briefing`; no third-party API calls are made directly from browser.

---

## 6. Testing Strategy

1. **Unit Testing**: Test `GeminiService` fallback mechanism when API key is missing or network fails.
2. **Backend API Testing**: Verify `GET /api/v1/ai/gemini/health` and `POST /api/v1/ai/gemini/briefing`.
3. **Data Integrity Testing**: Verify Python Risk Score == Backend Risk Score == Frontend Risk Score.
4. **Angular Build**: Execute `ng build` to ensure zero compilation or type errors.
5. **End-to-End Test Suite**: Run `test_integration.py` against running FastAPI backend & Angular proxy server.
