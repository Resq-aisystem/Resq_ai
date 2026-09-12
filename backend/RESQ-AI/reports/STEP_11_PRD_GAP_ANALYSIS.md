# RESQ-AI STEP 11 — PRD Gap Analysis Report

**Project**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Document Purpose**: Identifies architectural, data, and functional gaps between existing working system components and Product Requirements Document (PRD) targets, specifying exact required modifications.

---

## 1. Requirement-by-Requirement PRD Gap Matrix

| PRD Requirement | Existing System Implementation | Identified Gap | Required Modification | Affected / New Files | Data Availability | Validation Method |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Single-City MVP Scope** | 728-district national grid mode | No configurable single-city administrative scope | Add `CITY_MODE` in configuration while retaining 728-district grid | `config/settings.py` (MODIFIED), `config/city_config.yaml` (NEW) | Available via district bounding boxes | Unit & config tests |
| **2. 6-Hour Forecast Warnings** | Observed historical IMD rainfall features | No 6-hour weather forecast ingestion or normalization | Create modular `forecast/` package with OpenWeatherMap client & mock fallback | `forecast/__init__.py`, `forecast_client.py`, `forecast_schema.py` (NEW) | OpenWeatherMap API / Fallback mock | API & fallback integration tests |
| **3. 6-Hour Flood Prediction** | IMD Rainfall Severity classifier (`RandomForestClassifier`) | Baseline model is daily rainfall severity, not 6h flood forecast | Create `flood_prediction/` layer combining forecast signals with IMD model | `flood_prediction/__init__.py`, `predictor.py`, `schemas.py` (NEW) | Forecast + IMD + GFSM + CAMELS | Feature & predictor contract tests |
| **4. Flood Depth Estimation** | Categorical risk levels (`LOW` to `CRITICAL`) | No high-res hydro-dynamic depth model in dataset | Create `flood_depth/` interface returning `STATUS = "INSUFFICIENT_DATA"` if unconfigured | `flood_depth/__init__.py`, `depth_engine.py`, `depth_schema.py` (NEW) | Unconfigured high-res DEM | Data status & schema validation |
| **5. Flood Zone Generation** | District-level polygon boundaries | No spatial 100m grid flood zone polygons | Create `flood_zones/` spatial polygon generator & spatial intersection engine | `flood_zones/__init__.py`, `zone_schema.py`, `spatial_intersection.py` (NEW) | District/Grid geometry | Spatial intersection tests |
| **6. Facility Impact Assessment** | District-level risk & priority scoring | No facility-level impact scoring (hospitals, schools) | Create `facility/` package to evaluate facility exposure, risk, and impact | `facility/__init__.py`, `facility_schema.py`, `impact_engine.py` (NEW) | Facility schema / PostGIS integration | Facility impact tests |
| **7. Vulnerability-Aware Ranking** | District-level historical recurrence & GFSM priors | No facility vulnerability or population metrics (elderly, patients) | Extend priority engine with facility-level priority scoring (`PRD_FACILITY_PRIORITY_V1`) | `priority/emergency_priority/facility_priority.py` (NEW) | Facility vulnerability payload | Facility priority tests |
| **8. Flood-Aware Rescue Routing** | OSRM route calculation + district risk scoring | Route risk did not intersect with spatial flood zones | Upgrade `road_risk_engine.py` to calculate flood zone segment exposure | `route_risk/road_risk/road_risk_engine.py` (MODIFIED) | OSRM + Flood Zones | Flood-aware route tests |
| **9. 3 Route Alternatives** | `FASTEST`, `SAFEST`, `BALANCED` route mode ranking | Implemented; needs tradeoff breakdown formatting | Enhance route service to display travel time vs hazard risk tradeoff summaries | `route_risk/route_scoring/route_service.py` (MODIFIED) | OSRM API | Mode ranking tests |
| **10. 30-Minute Update Engine** | Manual batch execution scripts | No scheduler or update status tracking layer | Create `update/` orchestration layer with `update_interval_minutes = 30` | `update/__init__.py`, `scheduler.py`, `update_status.py` (NEW) | System timer | Update scheduler tests |
| **11. What-If Scenario Planning** | Static evaluation per date | No scenario analysis (rainfall multiplier, road closure) | Create `scenario/` package for baseline vs scenario comparisons | `scenario/__init__.py`, `scenario_engine.py`, `scenario_schema.py` (NEW) | Configurable parameters | Scenario comparison tests |
| **12. Provenance & Confidence** | Evidence quality rating (`HIGH`, `MEDIUM`, `LOW`) | No dataset/model/feature provenance tracking | Create `provenance/` package tracking dataset source, model version, timestamps | `provenance/__init__.py`, `tracker.py`, `provenance_schema.py` (NEW) | System metadata | Provenance tracking tests |
| **13. Grounded Action Plan** | Grounded Action Plan Engine (`action_plan/`) | Exists; needs 6-hour forecast, facility, & scenario context | Upgrade `GroundedContext` to consume forecast, facility impact, & scenarios | `action_plan/grounded_context.py` (MODIFIED), `action_plan_engine.py` (MODIFIED) | Engine outputs | Action plan integration tests |
| **14. Master Decision Contract** | Individual module contracts | No single top-level decision payload API | Create `inference/decision_contract.py` assembling full platform intelligence | `inference/decision_contract.py` (NEW) | All modules | Master contract tests |

---

## 2. Architecture & Data Principles

1. **Zero System Disruption**: Existing models (`imd_baseline_model.pkl`), Risk Engine (`inference/risk_engine.py`), Emergency Priority Engine (`priority/`), Route Risk Engine (`route_risk/`), and Action Plan Engine (`action_plan/`) are preserved and extended with 100% backward compatibility.
2. **No Data Fabrication**: Where PRD requires features without underlying datasets (e.g., continuous 100m flood depth or continuous rainfall regression), the system exposes clean interfaces, validates data schemas, and returns explicit data status fields (`INSUFFICIENT_DATA` or `UNAUTHENTICATED`).
3. **Determinism as Source of Truth**: Deterministic scoring and physical graph routing remain the source of truth for all numerical risk, priority, and route scores.
