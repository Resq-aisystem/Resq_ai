# RESQ-AI Flood History Feature & Target Store

This directory contains historical flood occurrence, severity, and flooded area feature layers derived from the **India Flood Inventory (IFI)** dataset (1967–2023).

## Primary Feature Dataset
- **File**: `features/flood_history/ifi_flood_history_features.csv`
- **Rows**: 728 districts (matching IMD district geography)
- **Columns**:
  - `state`: Indian State / Union Territory name
  - `district`: District name
  - `ifi_dfsi_score`: District flood susceptibility index score
  - `ifi_flooded_area_pct`: Historical flooded land area percentage (0.0% to 100.0%)
  - `ifi_permanent_water_pct`: Permanent water body percentage
  - `ifi_historical_event_count`: Total recorded flood events (1967–2023)
  - `ifi_mean_flood_duration_days`: Mean flood event duration in days
  - `ifi_total_fatalities`: Total historical human fatalities
  - `ifi_total_injured`: Total historical human injured
  - `ifi_flood_recurrence_rate`: Flood events per decade

## Decoupled Target Dataset
- **File**: `data/processed/ifi/ifi_flood_targets.csv`
- **Purpose**: Stores ground-truth supervised targets (`target_flood_risk_binary`, `target_risk_level`, `target_flooded_area_pct`) separately from predictor features to ensure zero data leakage.
