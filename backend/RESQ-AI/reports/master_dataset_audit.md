# RESQ-AI Master Dataset Feasibility, Temporal Alignment & Target Leakage Audit Report

## 1. Audit Overview & Objectives
This report evaluates the scientific feasibility, geographic joinability, temporal alignment, and target leakage risks across all 5 processed feature/target datasets in **RESQ-AI**.

---

## 2. Dataset Specs & Dimensions

| Dataset Name | Processed Path | Rows | Cols | Temporal Coverage | Geographic Extent |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **IMD Rainfall** | `C:\Users\pabbu\Desktop\RESQ-AI\features\rainfall\imd_rainfall_features.csv` | 17,457 | 23 | 2026-08-19 to 2026-09-11 (24 days) | 728 Districts (India) |
| **GFSM Susceptibility** | `C:\Users\pabbu\Desktop\RESQ-AI\features\susceptibility\gfsm_susceptibility_features.csv` | 728 | 11 | Static (Land Susceptibility) | 728 Districts (India) |
| **CAMELS-IND Hydrology** | `C:\Users\pabbu\Desktop\RESQ-AI\features\hydrology\camels_ind_hydrology_features.csv` | 728 | 18 | 1980–2020 (41-Yr Catchment Baseline) | 728 Districts (India) |
| **IFI Flood History** | `C:\Users\pabbu\Desktop\RESQ-AI\features\flood_history\ifi_flood_history_features.csv` | 728 | 10 | 1967–2023 (57-Yr Event Inventory) | 728 Districts (India) |
| **IFI Flood Targets** | `C:\Users\pabbu\Desktop\RESQ-AI\data\processed\ifi\ifi_flood_targets.csv` | 728 | 6 | Ground-Truth Historical Targets | 728 Districts (India) |
| **NASA GDIS History** | `C:\Users\pabbu\Desktop\RESQ-AI\features\disaster_history\gdis_disaster_history_features.csv` | 728 | 14 | 1960–2018 (59-Yr Multi-Hazard) | 728 Districts (India) |

---

## 3. Geographic Join Audit

- **RESQ-AI Target District Grid**: 728 Districts across 39 States / Union Territories.
- **GFSM Matching**: **728 / 728 (100.0%)**
- **CAMELS-IND Matching**: **728 / 728 (100.0%)**
- **IFI Features Matching**: **728 / 728 (100.0%)**
- **IFI Targets Matching**: **728 / 728 (100.0%)**
- **NASA GDIS Matching**: **728 / 728 (100.0%)**
- **Join Risk**: **ZERO** — All static feature matrices map 100% deterministically to the RESQ-AI district grid.

---

## 4. Temporal Alignment Audit

### Analysis of Timelines:
- **IMD Rainfall**: 2026-08-19 to 2026-09-11
- **CAMELS-IND**: 1980–2020
- **IFI**: 1967–2023
- **NASA GDIS**: 1960–2018
- **GFSM**: Static

### Explicit Answers to Questions A–E:
- **A. Common Time Periods**: No single daily window spans all five datasets simultaneously. IMD is 2026 daily; CAMELS, IFI, and GDIS are multi-decadal historical records (1960–2023).
- **B. IMD vs IFI Daily Alignment**: **NO**. Merging 2026 IMD daily rainfall with 1967-2023 historical flood event labels on a daily level is temporally invalid and would constitute time-travel data fabrication.
- **C. CAMELS vs IFI Alignment**: **YES**. CAMELS-IND long-term catchment hydrology (1980–2020) and IFI historical flood targets (1967–2023) share a overlapping 40-year historical baseline era.
- **D. GDIS Temporal Leakage**: GDIS 1960–2018 aggregates represent lifetime historical multi-hazard frequency prior to 2026. They are **SAFE** as static prior risk features for 2026 predictions, but must not be used to predict individual past events prior to 2018 without year-filtering.
- **E. District-Date Training Sample**: Daily district-date training requires matching daily weather with daily flood event logs during identical historical years.

---

## 5. Target Leakage Audit

### IFI Predictor Features Classification:
1. `ifi_dfsi_score`: **DIRECT LEAKAGE / UNUSABLE** (Derived from same historical DFSI calculation as `target_dfsi_score`).
2. `ifi_flooded_area_pct`: **DIRECT LEAKAGE / UNUSABLE** (Identical to `target_flooded_area_pct` ground truth).
3. `ifi_permanent_water_pct`: **SAFE** (Static surface water percentage).
4. `ifi_historical_event_count`: **POTENTIAL LEAKAGE** (Safe only as prior baseline for future window).
5. `ifi_mean_flood_duration_days`: **POTENTIAL LEAKAGE** (Post-event duration metric).
6. `ifi_total_fatalities`: **UNUSABLE** (Post-event casualty impact statistic).
7. `ifi_total_injured`: **UNUSABLE** (Post-event casualty impact statistic).
8. `ifi_flood_recurrence_rate`: **SAFE** (Decadal event recurrence frequency prior).

---

## 6. Master Dataset Architecture Evaluation

- **Option A (District-Level Static Historical Risk Model)**: Static predictors (`GFSM`, `CAMELS`, `GDIS`) predicting static `IFI` target. Valid, but lacks dynamic rainfall.
- **Option B (Historical District-Date Prediction Model)**: Requires multi-decade daily IMD rainfall grids (1980–2023).
- **Option C (RECOMMENDED: RESQ-AI Modular Multi-Layer Architecture)**:
  - **Layer 1**: Trained IMD Daily Rainfall Severity Model (`models/flood_risk/imd_baseline_model.pkl`) predicting daily rainfall intensity.
  - **Layer 2**: `GFSM` 30m terrain susceptibility + `CAMELS-IND` catchment hydrology & soil moisture.
  - **Layer 3**: `IFI` historical flood susceptibility & flooded area ground-truth targets + `NASA GDIS` historical multi-hazard frequency.
  - **Layer 4**: Decoupled Emergency Priority Scoring & Route Risk Intelligence Engines.

---

## 7. Final Model Readiness Decision

### **STATUS: NOT READY FOR SINGLE MONOLITHIC MATRIX MODEL / 100% READY FOR RESQ-AI INTEGRATED MODULAR PIPELINE**

- **Reason**: Joining 2026 IMD daily rows directly with 1967–2023 historical IFI event targets in a single monolithic CSV creates temporal leakage and data fabrication.
- **Recommendation**: Deploy the RESQ-AI Modular Multi-Layer Decision-Support Architecture.
