# RESQ-AI Target AI System Architecture Specification (v2.0)

**Platform**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Architecture Standard**: PRD-Aligned End-to-End Decision Intelligence  
**Document Version**: 2.0.0  

---

## 1. High-Level Data Flow Diagram

```
[OpenWeatherMap API / Fallback Forecast] ──> forecast/
                                                  │
                                                  ▼
[IMD Daily Rainfall Features] ───────> flood_prediction/ <─── [GFSM Susceptibility & CAMELS Hydrology]
                                                  │
                                                  ▼
[Layer 1-3 Risk Engine] ─────────────> inference/ (Risk Score & Level)
                                                  │
                                                  ├────────────────────────┐
                                                  ▼                        ▼
[Spatial Flood Zone Engine] ───────> flood_zones/             facility/ (Facility Exposure & Impact)
                                         │                                 │
                                         ▼                                 ▼
[OSRM Routing Client] ─────────────> route_risk/              priority/ (PRD Facility Priority V1)
                                         │                                 │
                                         └────────────────┬────────────────┘
                                                          ▼
                                              action_plan/ (Grounded Action Plan)
                                                          │
                                                          ▼
                                              scenario/ (What-If Scenario Engine)
                                                          │
                                                          ▼
                                        provenance/ & inference/decision_contract.py
                                                          │
                                                          ▼
                                     Unified Master Decision Intelligence Payload
```

---

## 2. Package & Layer Architecture Specifications

### 1. Forecast Layer (`forecast/`)
- Ingests 6-hour forecast series (hourly precipitation mm, temperature, humidity, wind speed).
- Client: `fetch_6hour_forecast` (OpenWeatherMap API via `OPENWEATHERMAP_API_KEY` or deterministic mock fallback).

### 2. Predictive Flood Layer (`flood_prediction/`)
- Predictor: `predict_6hour_flood_risk`
- Combines 6-hour forecast precipitation, observed IMD rainfall severity baseline predictions, GFSM terrain flood susceptibility, and CAMELS hydrology features into a forward-looking 6-hour flood risk score `[0, 100]`.

### 3. Depth & Zone Layer (`flood_depth/` & `flood_zones/`)
- Depth Engine: `estimate_flood_depth` (returns `STATUS = "INSUFFICIENT_DATA"` when high-res DEM raster is unconfigured).
- Flood Zones: `generate_city_flood_zones` (generates 100m grid spatial polygons and intersects with facilities and route waypoints).

### 4. Facility Exposure & Priority Layer (`facility/` & `priority/`)
- Impact Engine: `evaluate_facility_impacts` (evaluates hospitals, shelters, emergency centers, schools).
- Facility Priority: `get_facility_evacuation_priorities` (`PRD_FACILITY_PRIORITY_V1` incorporating ICU/patient metrics and spatial flood zone exposure).

### 5. Rescue Routing Layer (`route_risk/`)
- Road Risk Engine: `calculate_route_risk` (intersects waypoints with spatial flood zone polygons to compute exposed route distance in km and exposure %).
- Modes: `FASTEST`, `SAFEST`, `BALANCED`.

### 6. Action Plan & Scenario Layer (`action_plan/` & `scenario/`)
- Grounded Context Builder: `build_grounded_context`
- LLM Client & Fallback: `generate_llm_action_plan` (OpenAI / Gemini API or zero-dependency deterministic fallback).
- What-If Scenario Engine: `run_scenario_analysis` (evaluates rainfall surge multipliers and road failure scenarios).

### 7. Provenance & Master Contract Layer (`provenance/` & `inference/decision_contract.py`)
- Provenance Tracker: `create_provenance_record` (attaches dataset, model, feature versions, and calculation timestamps).
- Decision Contract: `get_city_decision_intelligence` (unified API payload).
