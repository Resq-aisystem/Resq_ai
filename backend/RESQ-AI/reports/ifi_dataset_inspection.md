# India Flood Inventory (IFI) Quality & Inspection Report

## 1. Dataset Source & Overview
- **Dataset Title**: India Flood Inventory (IFI)
- **Local Source Directory**: `C:\Users\pabbu\Downloads\16994648`
- **Cleaned District File**: `data/processed/ifi/ifi_districts_cleaned.csv`
- **Cleaned Event Inventory File**: `data/processed/ifi/ifi_event_inventory_cleaned.csv`
- **Predictor Feature File**: `features/flood_history/ifi_flood_history_features.csv`
- **Supervised Target File**: `data/processed/ifi/ifi_flood_targets.csv`
- **Metadata JSON**: `data/processed/ifi/ifi_metadata.json`

---

## 2. Ingested Files & Schemas

### 1. `India_Flood_Inventory_v3.csv` (Event-Level Historical Inventory)
- **Rows**: 6,876 event records
- **Temporal Span**: `1967-01-08` to `2023-12-09` (57 years of recorded historical flood events)
- **Primary Key**: `UEI` (Unique Event Identifier, e.g. `UEI-IMD-FL-1967-0001`)
- **Key Columns**: `Start Date`, `End Date`, `Duration(Days)`, `Main Cause`, `State`, `Districts`, `District_LGD_Codes`, `State_Codes`, `Human fatality`, `Human injured`.

### 2. `DFSI.csv` (District Flood Susceptibility Index)
- **Rows**: 744 district records
- **Key Columns**: `district_name`, `state_name`, `dfsi_score` (continuous index 0.0 to 19.3).

### 3. `District_FloodedArea.csv` (District Flooded Area)
- **Rows**: 732 district records
- **Key Columns**: `district_name`, `percent_flooded_area`, `permanent_water_pct`, `corrected_flooded_area_pct` (0.0% to 100.0%).

### 4. `District_FloodImpact.csv` (District Flood Impact Aggregates)
- **Rows**: 732 district records
- **Key Columns**: `district_name`, `total_human_fatalities`, `total_human_injured`, `census_population`, `mean_flood_duration_days`.

---

## 3. Data Dictionary

| Field Name | Source File | Data Type | Description |
| :--- | :--- | :---: | :--- |
| `UEI` | `India_Flood_Inventory_v3.csv` | `string` | Unique Event Identifier |
| `Start Date` | `India_Flood_Inventory_v3.csv` | `datetime` | Event onset date |
| `End Date` | `India_Flood_Inventory_v3.csv` | `datetime` | Event termination date |
| `Duration(Days)` | `India_Flood_Inventory_v3.csv` | `float64` | Total event duration in days |
| `Main Cause` | `India_Flood_Inventory_v3.csv` | `string` | Primary trigger (Heavy Rains, Cyclone, Flash Flood, etc.) |
| `DFSI` | `DFSI.csv` | `float64` | District Flood Susceptibility Index score |
| `Percent_Flooded_Area` | `District_FloodedArea.csv` | `float64` | Observed flooded land area percentage |
| `Corrected_Percent_Flooded_Area` | `District_FloodedArea.csv` | `float64` | Terrain-corrected flooded land area percentage |
| `Human_fatality` | `District_FloodImpact.csv` | `int64` | Total historical human fatalities |
| `Human_injured` | `District_FloodImpact.csv` | `int64` | Total historical human injured |
| `Mean_Flood_Duration` | `District_FloodImpact.csv` | `float64` | Mean historical flood event duration (days) |

---

## 4. Candidate Target Analysis & Ground-Truth Formulation

### Candidate Target Evaluation:
1. `dfsi_score`: Excellent district-level flood susceptibility indicator, continuous range ($0.0 - 19.3$).
2. `corrected_flooded_area_pct`: Ground-truth maximum inundated land area percentage ($0.0\% - 100.0\%$).
3. `target_flood_risk_binary`: Binary flag ($1$ if `corrected_flooded_area_pct >= 5.0%` or `dfsi_score >= 10.0`, else $0$).
4. `target_risk_level`: Categorical target (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).

### Recommended Supervised Target Strategy:
- The target matrix is saved separately in `data/processed/ifi/ifi_flood_targets.csv` to ensure **ZERO TARGET LEAKAGE** into model predictors.

---

## 5. Extracted Feature Store (`features/flood_history/ifi_flood_history_features.csv`)
- `ifi_dfsi_score`: District flood susceptibility score
- `ifi_flooded_area_pct`: Historical flooded land area percentage
- `ifi_permanent_water_pct`: Permanent water body percentage
- `ifi_historical_event_count`: Total recorded historical flood events (1967-2023)
- `ifi_mean_flood_duration_days`: Mean flood duration in days
- `ifi_total_fatalities`: Total human fatalities
- `ifi_total_injured`: Total human injured
- `ifi_flood_recurrence_rate`: Estimated flood events per decade

---

## 6. Verification & Data Integrity
- **Original Files Unmodified**: Original downloaded directory `C:\Users\pabbu\Downloads\16994648` was verified completely untouched.
- **No Data Fabrication**: Ground-truth historical flood events and flooded area statistics were preserved strictly from the source dataset.
