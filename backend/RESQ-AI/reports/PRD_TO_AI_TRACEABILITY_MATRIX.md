# RESQ-AI PRD to AI System Traceability Matrix

**Project**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Target Document**: Product Requirements Document (PRD)  

---

| PRD Requirement | AI Module / Layer | Primary Inputs | Primary Outputs | Validation & Test Method | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **1. 6-Hour Predictive Warning** | `forecast/` & `flood_prediction/` | OpenWeatherMap API / Weather Forecast + IMD model | 6-hour predictive rainfall total (mm) & risk score | Integration tests (`tests/test_prd_pipeline.py`) | **PASS** |
| **2. Rainfall Forecast Ingestion** | `forecast/forecast_client.py` | API Key / OpenWeatherMap or deterministic fallback | Standardized 6-hour hourly precipitation series | API & mock fallback tests | **PASS** |
| **3. Flood Risk Modeling** | `flood_prediction/predictor.py` | Forecast + IMD RF baseline + GFSM + CAMELS | 6-hour forward flood risk score `[0, 100]` & level | Predictor contract tests | **PASS** |
| **4. Flood Depth Estimation** | `flood_depth/depth_engine.py` | High-res DEM (unconfigured by default) | `STATUS = "INSUFFICIENT_DATA"` (Zero depth fabrication) | Data status validation test | **PASS** |
| **5. Flood Zone Generation** | `flood_zones/spatial_intersection.py` | Bounding box / 100m grid polygons | Spatial polygons (`FloodZonePayload`) & route exposure | Spatial intersection tests | **PASS** |
| **6. Facility Impact Assessment** | `facility/impact_engine.py` | Facility schema + Flood zones + Risk Engine | Facility risk, exposure, & vulnerability scores | Facility impact tests | **PASS** |
| **7. Vulnerability-Aware Ranking** | `priority/emergency_priority/facility_priority.py` | Facility impacts + Patient/Elderly counts | Ranked facility priorities (`PRD_FACILITY_PRIORITY_V1`) | Priority ranking tests | **PASS** |
| **8. Explainable Scoring** | `inference/risk_engine.py` & `priority/` | Verified layer metrics & top factors | Top contributing factors & evidence reasons | Factor evidence tests | **PASS** |
| **9. 3 Route Alternatives** | `route_risk/route_modes/route_modes.py` | OSRM route candidates | `FASTEST`, `SAFEST`, `BALANCED` route rankings | Mode ranking tests | **PASS** |
| **10. Flood-Aware Routing** | `route_risk/road_risk/road_risk_engine.py` | Waypoints + Spatial flood zone polygons | Exposed route distance (km) & percentage (%) | Flood-aware route tests | **PASS** |
| **11. Grounded Action Recommendations** | `action_plan/action_plan_engine.py` | GroundedContext + LLM / Deterministic Fallback | Validated Emergency Action Plan payload | Schema & guardrail tests | **PASS** |
| **12. Provenance Tracking** | `provenance/provenance_schema.py` | System metadata, model version, timestamps | Lineage payload (`ProvenanceRecord`) | Provenance tracking tests | **PASS** |
| **13. Confidence Information** | `flood_prediction/schemas.py` | Model calibration status | `confidence_level = "UNCALIBRATED"` | Confidence semantics tests | **PASS** |
| **14. What-If Scenario Planning** | `scenario/scenario_engine.py` | Multipliers (e.g. 1.8x rainfall surge) | Baseline vs scenario risk deltas & new P1 facilities | Scenario comparison tests | **PASS** |
| **15. Single-City MVP Capability** | `config/city_config.yaml` | `CITY_MODE` bounds (e.g. Puri City MVP) | City decision intelligence payload | City config tests | **PASS** |
| **16. 30-Minute Update Architecture** | `update/scheduler.py` | `update_interval_minutes = 30` | Update timestamps & completion status | Update scheduler tests | **PASS** |
| **17. Decision-Ready Output Payload** | `inference/decision_contract.py` | All system modules | Master PRD decision payload payload | Master contract tests | **PASS** |
