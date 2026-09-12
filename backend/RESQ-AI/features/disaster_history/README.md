# RESQ-AI Disaster History Feature Store

This directory contains historical disaster occurrence and multi-hazard frequency feature layers derived from the **NASA GDIS (Geocoded Disasters Dataset 1960–2018)**.

## Primary Feature Dataset
- **File**: `features/disaster_history/gdis_disaster_history_features.csv`
- **Rows**: 728 districts (matching IMD district geography)
- **Columns**:
  - `state`: Indian State / Union Territory name
  - `district`: District name
  - `gdis_historical_disaster_count`: Total historical disaster events recorded (1960–2018)
  - `gdis_flood_event_count`: Total recorded flood events
  - `gdis_storm_event_count`: Total recorded storm events
  - `gdis_drought_event_count`: Total recorded drought events
  - `gdis_extreme_temp_event_count`: Total recorded extreme temperature events
  - `gdis_earthquake_event_count`: Total recorded earthquake events
  - `gdis_landslide_event_count`: Total recorded landslide events
  - `gdis_unique_disaster_types_count`: Count of unique disaster types experienced
  - `gdis_year_first_record`: Earliest recorded disaster year
  - `gdis_year_last_record`: Latest recorded disaster year
  - `gdis_recent_10yr_event_count`: Disaster event count in recent 10-year window (2009–2018)
  - `gdis_disaster_frequency_per_decade`: Disaster events per decade

## Connection to Final RESQ-AI Master Feature Store
In the final RESQ-AI master feature store, these historical multi-hazard frequency features will be merged by district with:
1. **IMD Rainfall**: Dynamic daily precipitation and rolling antecedent rainfall.
2. **GFSM Susceptibility**: Static 30m flood susceptibility metrics.
3. **CAMELS-IND Hydrology**: Catchment hydrology, soil moisture, and runoff metrics.
4. **India Flood Inventory (IFI)**: Ground-truth historical flood events and inundated area damage labels.
