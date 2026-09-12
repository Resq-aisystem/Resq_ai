# RESQ-AI Model & System Performance Complete Evaluation Report

**Project**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Evaluation Scope**: End-to-End System & Component Audit  
**Evaluation Date**: 2026-09-12  
**Final Status**: `RESQ-AI COMPLETE EVALUATION: PASS`  

---

## 1. Executive Summary

This report provides a rigorous, empirical evaluation of the **RESQ-AI** platform. Every platform component—from the supervised IMD rainfall baseline classifier to downstream deterministic risk, priority, routing, and action plan engines—is evaluated using empirical metrics, data quality audits, and leakage checks.

> [!IMPORTANT]
> **Scientific Evaluation Conclusion**:
> *"RESQ-AI currently has a validated ML rainfall-severity component with 68.05% temporal test accuracy and 68.87% weighted F1. The downstream Risk, Priority, Routing, and Action Plan components are deterministic/decision-support modules whose predictive accuracy cannot be established without independent benchmark datasets."*

---

## 2. Architecture & Component Classification

| Module / Component | Primary Source File | Operational Paradigm | Output Type |
| :--- | :--- | :--- | :--- |
| **IMD Rainfall Baseline Model** | `models/flood_risk/imd_baseline_model.pkl` | **A. Supervised ML Prediction** | Multiclass Severity Label (`LIGHT`, `MODERATE`, `HEAVY`, `EXTREME`) |
| **Production Risk Inference Engine** | `inference/risk_engine.py` | **B. Deterministic Scoring** | Bounded Risk Score `[0, 100]` & Level (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) |
| **Emergency Priority Engine** | `priority/emergency_priority/engine.py` | **B. Deterministic Scoring** | Bounded Priority Score `[0, 100]` & Ranking Level (`P1`, `P2`, `P3`, `P4`) |
| **Road Segment Risk Engine** | `route_risk/road_risk/road_risk_engine.py` | **B. Deterministic Scoring** | Bounded Route Segment Hazard Score `[0, 100]` |
| **OSRM Route Client & Modes** | `route_risk/route_scoring/osrm_client.py` | **C. Graph Routing Algorithm** | Candidate Geometries, Distances (km), Durations (min), Mode Selection |
| **Action Plan Engine & Fallback** | `action_plan/llm_client.py` | **D. LLM / Fallback Engine** | Validated Structured Action Plan Payload |
| **Feature Pipelines (5 Datasets)** | `features/` | **E. Preprocessing Pipeline** | Standardized Feature CSVs across 728 Districts |

---

## 3. Supervised ML Model Evaluation (IMD Baseline)

- **Model Artifact**: `models/flood_risk/imd_baseline_model.pkl` (`RandomForestClassifier`, `n_estimators=100`, `max_depth=10`, `class_weight='balanced'`, `random_state=42`)
- **Temporal Test Split**: `date >= 2026-09-05` (**5,093 test rows**)

### Legitimate ML Metrics
- **Accuracy**: **68.05%** (0.680542)
- **Weighted Precision**: **70.97%** (0.709655)
- **Weighted Recall**: **68.05%** (0.680542)
- **Weighted F1 Score**: **68.87%** (0.688678)
- **Balanced Accuracy**: **45.11%** (0.451128)
- **Macro Precision**: **43.84%** (0.438438)
- **Macro Recall**: **45.11%** (0.451128)
- **Macro F1 Score**: **43.98%** (0.439806)
- **Cohen's Kappa**: **0.3272**
- **Matthews Correlation Coefficient (MCC)**: **0.3345**

### Rainfall Regression Question
- **Status**: The IMD baseline model is a **classification** model predicting discrete severity categories (`LIGHT`, `MODERATE`, `HEAVY`, `EXTREME`). It does **NOT** predict continuous precipitation depth in millimeters.
- **Continuous Rainfall Regression Accuracy**: **NOT AVAILABLE** (No continuous regression model exists).

---

## 4. Downstream Engine Evaluations

### A. Production Risk Inference Engine
- **Predictive Accuracy**: **NOT ESTABLISHED** (Independent current ground-truth flood target is unavailable).
- **Quality Metrics**: 100% score-bound compliance `[0, 100]`, 100% district grid coverage (728/728 districts), 100% HIGH evidence quality rating, 100% deterministic repeatability.

### B. Emergency Priority Engine
- **Predictive Accuracy**: **NOT ESTABLISHED** (Operational ranking system rather than a supervised prediction model).
- **Quality Metrics**: 100% district coverage (728/728 districts), score range `[22.34, 74.44]`, level breakdown (`P1`: 9, `P2`: 173, `P3`: 454, `P4`: 92), 100% leakage exclusion compliance.

### C. Route Risk & Routing Engine
- **Route Optimization Accuracy**: **NOT ESTABLISHED** (No independent ground-truth emergency route benchmark dataset available).
- **Quality Metrics**: OSRM graph routing success rate = 100%, candidate parsing success = 100%, objective mode selection compliance (`FASTEST`, `SAFEST`, `BALANCED`) = 100%.

### D. Action Plan Generation Engine
- **LLM Response Accuracy**: **NOT MEASURED** (No authenticated LLM evaluation benchmark set available).
- **Quality Metrics**: Deterministic fallback success rate = 100%, schema contract validation rate = 100%, guardrail rejection mechanism = PASSED.

---

## 5. Dataset Quality & Target Leakage Audit

### Dataset Quality Summary
1. **IMD Rainfall**: Daily observed data (2026-08-19 to 2026-09-11), 728 districts covered, 0 missing values.
2. **GFSM Susceptibility**: 30m resolution terrain flood susceptibility ratings (728 districts), 0 missing values.
3. **CAMELS-IND Hydrology**: Catchment runoff ratios and soil moisture (728 districts), 0 missing values.
4. **IFI Flood History**: Decoupled historical flood recurrence rates (728 districts), 0 missing values.
5. **NASA GDIS Disaster History**: Multi-hazard disaster counts (1960–2018), 728 districts covered, 0 missing values.

### Target Leakage Audit Table

| Variable Name | Variable Category | Risk Engine | Priority Engine | Route Engine | Leakage Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `daily_actual_mm` | Observed Weather Feature | Used | Used | Used | **SAFE** |
| `gfsm_susceptibility_score` | Physical Terrain Feature | Used | Used | Used | **SAFE** |
| `camels_runoff_ratio` | Hydrological Feature | Used | Used | Used | **SAFE** |
| `ifi_flood_recurrence_rate` | Historical Prior | Used | Used | Used | **SAFE** |
| `gdis_historical_disaster_count` | Historical Prior | Used | Used | Used | **SAFE** |
| `ifi_dfsi_score` | Target-Derived Metric | **EXCLUDED** | **EXCLUDED** | **EXCLUDED** | **SAFE (EXCLUDED)** |
| `target_flooded_area_pct` | Target Variable | **EXCLUDED** | **EXCLUDED** | **EXCLUDED** | **SAFE (EXCLUDED)** |
| `target_risk_level` | Target Variable | **EXCLUDED** | **EXCLUDED** | **EXCLUDED** | **SAFE (EXCLUDED)** |
| `target_flood_risk_binary` | Target Variable | **EXCLUDED** | **EXCLUDED** | **EXCLUDED** | **SAFE (EXCLUDED)** |
| `total_fatalities` / `injured` | Post-Event Impact | **EXCLUDED** | **EXCLUDED** | **EXCLUDED** | **SAFE (EXCLUDED)** |

---

## 6. What Can & Cannot Legitimately Be Called "Accuracy"

### What CAN Legitimately Be Called Accuracy:
- **68.05% Accuracy** for IMD Rainfall Severity Classification on held-out temporal test set (`dates >= 2026-09-05`).
- **68.87% Weighted F1 Score** for IMD Rainfall Severity Classification.
- **43.98% Macro F1 Score** for IMD Rainfall Severity Classification.

### What CANNOT Legitimately Be Called Accuracy:
- **"X% Flood Prediction Accuracy"**: No ground-truth flood prediction model was trained or evaluated.
- **"X% Route Optimization Accuracy"**: Routing is an algorithmic graph search; no ground-truth optimal rescue route dataset exists.
- **"X% Priority Ranking Accuracy"**: Priority is an operational decision-support heuristic ranking.
- **"X% Action Plan LLM Accuracy"**: LLM operates in zero-credential deterministic fallback mode.
- **"Continuous Rainfall Depth (mm) Accuracy"**: Model is a classification model, not a regression model.

---

## 7. Hackathon Presentation Metrics Table

| Platform Component | Metric Name | Metric Result | Scientific & Operational Interpretation |
| :--- | :--- | :---: | :--- |
| **IMD Rainfall Severity Model** | Classification Accuracy | **68.05%** | Valid temporal test accuracy for 4-class severity classification |
| **IMD Rainfall Severity Model** | Weighted F1 Score | **68.87%** | Class-weighted performance metric under sample distribution |
| **IMD Rainfall Severity Model** | Macro F1 Score | **43.98%** | Equal-weighted F1 score reflecting minority class challenge |
| **IMD Rainfall Severity Model** | Continuous Rainfall MAE/RMSE | **N/A** | Model predicts severity classes (`LIGHT`/`MODERATE`/`HEAVY`/`EXTREME`), not mm |
| **Production Risk Inference Engine** | Predictive Accuracy | **N/A** | Decision-support score; independent ground-truth flood target unavailable |
| **Production Risk Inference Engine** | District Grid Coverage | **100% (728/728)** | Complete geographic coverage across all Indian districts |
| **Emergency Priority Engine** | Ranking Accuracy | **N/A** | Operational ranking system (`P1`–`P4`); not a supervised prediction model |
| **Emergency Priority Engine** | Target Leakage Audit | **PASSED** | 100% exclusion of target-derived & casualty variables |
| **Route Risk Engine** | Optimization Accuracy | **N/A** | OSRM graph search; ground-truth emergency route benchmark unavailable |
| **Route Risk Engine** | Routing Success Rate | **100%** | Successful route graph parsing across `FASTEST`, `SAFEST`, `BALANCED` modes |
| **Action Plan Generator** | LLM Accuracy | **N/A** | Unauthenticated LLM evaluation set unavailable; deterministic fallback used |
| **Action Plan Generator** | Schema Contract Validation | **100%** | Complete compliance with output schema & guardrail rules |
| **Complete System Test Suite** | Repository Unit Tests | **84 / 84 Passed** | 100% pass rate across all system unit & integration tests |

---

### FINAL STATUS

**RESQ-AI COMPLETE EVALUATION: PASS**
