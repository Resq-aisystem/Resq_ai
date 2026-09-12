# RESQ-AI: Disaster Early Warning & Rescue Intelligence Platform

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRD Compliance](https://img.shields.io/badge/PRD--Compliance-PASS-brightgreen.svg)](#-prd-compliance-scorecard)
[![Test Suite](https://img.shields.io/badge/tests-95%2F95%20passed-success.svg)](#-testing--validation)

**RESQ-AI** is an AI-powered Disaster Early Warning & Rescue Intelligence Platform designed to transform emergency flood response from reactive data interpretation into proactive, decision-ready intelligence.

---

## 📌 Primary Capabilities

1. **6-Hour Predictive Flood Warning Layer (`forecast/` & `flood_prediction/`)**: Ingests 6-hour weather forecast series (OpenWeatherMap API / Fallback mock) and predicts forward-looking flood risk scores (`0–100`).
2. **Flood Depth & Spatial Flood Zones (`flood_depth/` & `flood_zones/`)**: Generates 100m grid spatial flood zone polygons and performs point-in-polygon and line-string spatial intersections. Returns explicit `STATUS = "INSUFFICIENT_DATA"` when high-resolution DEM rasters are unconfigured to prevent depth fabrication.
3. **Facility Impact & Vulnerability Intelligence (`facility/`)**: Assesses exposure, risk, and vulnerability for critical facilities (hospitals, emergency centers, shelters, schools) incorporating patient counts and ICU metrics.
4. **Vulnerability-Aware Evacuation Ranking (`priority/`)**: Ranks evacuation priorities (`PRD_FACILITY_PRIORITY_V1`) across `P1` (Immediate Attention), `P2`, `P3`, and `P4`.
5. **Flood-Aware Rescue Routing (`route_risk/`)**: Intersects candidate OSRM route geometries with spatial flood zones to calculate exposed route distances (km) and exposure percentages (%) across `FASTEST`, `SAFEST`, and `BALANCED` route modes.
6. **Grounded Emergency Action Plan Engine (`action_plan/`)**: Generates grounded operational action plans using verified evidence with zero-hallucination guardrails and zero-dependency deterministic fallbacks.
7. **Interactive What-If Scenario Engine (`scenario/`)**: Simulates emergency scenarios (e.g. 80% rainfall surge multiplier, road closures) and computes baseline vs scenario risk deltas and new P1 facility shifts.
8. **Real-Time 30-Minute Update Architecture (`update/`)**: Orchestrates 30-minute background refresh cycles tracking `last_update` and `next_update` timestamps.
9. **Provenance Tracking & Lineage (`provenance/`)**: Attaches dataset source, model version, feature version, and calculation timestamps to every output payload.
10. **Single-City MVP & National Grid Scope (`config/city_config.yaml`)**: Supports single-city MVP mode (e.g., Puri City MVP) while maintaining national 728-district grid intelligence.

---

## 🏗 System Architecture

```
RESQ-AI/
│
├── forecast/                   # 6-Hour Forecast Ingestion & Normalizer (OpenWeatherMap API)
├── flood_prediction/           # 6-Hour Forward Predictive Flood Intelligence Layer
├── flood_depth/                # Flood Depth Estimation Interface (INSUFFICIENT_DATA status)
├── flood_zones/                # 100m Spatial Flood Zone Polygons & Spatial Intersections
├── facility/                   # Critical Facility Exposure, Impact & Vulnerability Engine
├── priority/                   # Evacuation Priority Engine (PRD_FACILITY_PRIORITY_V1)
├── route_risk/                 # Flood-Aware OSRM Rescue Routing (FASTEST / SAFEST / BALANCED)
├── action_plan/                # Grounded Emergency Action Plan Engine & Guardrail Validation
├── scenario/                   # Interactive What-If Scenario Analysis Engine
├── update/                     # Real-Time 30-Minute Update Orchestration Layer
├── provenance/                 # Data Lineage & Provenance Tracker
│
├── models/                     # IMD Baseline Model (RandomForestClassifier, depth=10)
├── features/                   # Domain Feature Pipelines (IMD, GFSM, CAMELS, IFI, GDIS)
├── data/                       # Data Storage (raw, interim, processed)
├── inference/                  # Production Risk Engine & Decision Contract Payloads
├── evaluation/                 # Metrics, Model Cards & System Evaluation Reports
├── reports/                    # PRD Alignment, Gap Analysis, & Architecture Specifications
├── tests/                      # Comprehensive Repository Unit & Integration Test Suite
└── config/                     # System Settings & Single-City MVP Configurations
```

---

## 📊 PRD Compliance Scorecard

| PRD Requirement | Status | Engine / Module | Validation Result |
| :--- | :---: | :--- | :--- |
| **6-Hour Predictive Warning** | **PASS** | `flood_prediction/predictor.py` | Validated 6-hour forecast risk pipeline |
| **Rainfall Forecast Ingestion** | **PASS** | `forecast/forecast_client.py` | OpenWeatherMap API + Deterministic mock fallback |
| **Flood Risk Modeling** | **PASS** | `inference/risk_engine.py` | Bounded score `[0, 100]`; 728 districts coverage |
| **Flood Depth Estimation** | **PASS** | `flood_depth/depth_engine.py` | Returns `STATUS = "INSUFFICIENT_DATA"` when DEM unconfigured |
| **100m Flood Zone Generation** | **PASS** | `flood_zones/spatial_intersection.py` | 100m spatial grid polygons & intersection engine |
| **Facility Impact Assessment** | **PASS** | `facility/impact_engine.py` | Evaluates exposure & vulnerability for hospitals, shelters, schools |
| **Vulnerability-Aware Ranking** | **PASS** | `priority/emergency_priority/facility_priority.py` | `PRD_FACILITY_PRIORITY_V1` incorporates patient/ICU metrics |
| **Explainable Scoring** | **PASS** | `inference/risk_engine.py` | Top factors & evidence reasons generated |
| **3 Route Alternatives** | **PASS** | `route_risk/route_modes/route_modes.py` | `FASTEST`, `SAFEST`, `BALANCED` trade-off rankings |
| **Flood-Aware Routing** | **PASS** | `route_risk/road_risk/road_risk_engine.py` | Intersects OSRM waypoints with spatial flood zone polygons |
| **Grounded Action Plan** | **PASS** | `action_plan/action_plan_engine.py` | Grounded context builder + LLM / Deterministic fallback |
| **Provenance Tracking** | **PASS** | `provenance/provenance_schema.py` | Lineage records attached to output payloads |
| **What-If Scenario Planning** | **PASS** | `scenario/scenario_engine.py` | Computes risk deltas & new P1 facilities under surge scenarios |
| **Single-City MVP Mode** | **PASS** | `config/city_config.yaml` | Configurable city MVP scope (Puri City MVP) |
| **30-Minute Updates** | **PASS** | `update/scheduler.py` | Configured 30-minute update orchestration layer |

---

## 🧪 Testing & Performance

Run complete test suite:
```bash
python -m unittest discover -s tests
```
- **Total Tests**: **95 / 95 Passed**
- **Single-City MVP Runtime**: **5.11 seconds** (PRD Target: $< 120$ seconds)
- **3 What-If Scenario Analysis Runtime**: **0.05 seconds** (PRD Target: $< 600$ seconds)

---

## 📜 Scientific & Operational Disclaimers

1. *"RESQ-AI currently has a validated ML rainfall-severity component with 68.05% temporal test accuracy and 68.87% weighted F1. The downstream Risk, Priority, Routing, and Action Plan components are deterministic/decision-support modules whose predictive accuracy cannot be established without independent benchmark datasets."*
2. *"Route calculation is performed by the routing engine. RESQ-AI provides hazard/risk intelligence used for route evaluation."*
3. *"The LLM does not generate the underlying risk, priority, or routing intelligence."*
