# India Flood Inventory Metadata & Provenance Report

## 1. Dataset Origin & Citation
- **Dataset Title**: India Flood Inventory (IFI)
- **Local Source Directory**: `C:\Users\pabbu\Downloads\16994648`
- **Primary Data Sources**: India Meteorological Department (IMD) disaster reports, Central Water Commission (CWC), state disaster management authorities, and published flood inventories.
- **Temporal Span**: 1967-01-08 to 2023-12-09 (57 years).

---

## 2. Key Metadata & Data Dictionary
- **`UEI`**: Unique Event Identifier (e.g. `UEI-IMD-FL-1967-0001`).
- **`DFSI`**: District Flood Susceptibility Index score.
- **`Corrected_Percent_Flooded_Area`**: Terrain-corrected maximum observed flooded area percentage (0-100%).
- **`Mean_Flood_Duration`**: Average duration of historical flood inundation events in days.

---

## 3. Integration into RESQ-AI Architecture
IFI serves a dual role in RESQ-AI:
1. **Target Provider**: Supplies verified ground-truth historical flood targets (`target_flood_risk_binary`, `target_risk_level`, `target_flooded_area_pct`) in `data/processed/ifi/ifi_flood_targets.csv`.
2. **Historical Feature Provider**: Supplies historical flood occurrence features (`ifi_dfsi_score`, `ifi_flooded_area_pct`, `ifi_historical_event_count`) in `features/flood_history/ifi_flood_history_features.csv`.

> **PROVENANCE NOTICE**: Target variables are stored in a dedicated, decoupled directory (`data/processed/ifi/ifi_flood_targets.csv`) to prevent accidental feature leakage into model training predictors.
