# RESQ-AI Hydrology Feature Store

This directory contains catchment hydrological, soil moisture, and runoff feature layers derived from the **CAMELS-IND (Catchment Attributes and Meteorology for India)** dataset.

## Primary Feature Dataset
- **File**: `features/hydrology/camels_ind_hydrology_features.csv`
- **Rows**: 728 districts (matching IMD district geography)
- **Columns**:
  - `state`: Indian State / Union Territory name
  - `district`: District name
  - `camels_aridity_index`: Catchment aridity index ($PET / P$)
  - `camels_p_mean_mm_day`: Long-term mean daily precipitation ($mm/day$)
  - `camels_q_mean_mm_day`: Long-term mean daily runoff/streamflow ($mm/day$)
  - `camels_runoff_ratio`: Catchment runoff ratio ($Q / P$)
  - `camels_soil_moisture_mean_kg_m2`: Catchment mean root-zone soil moisture ($kg/m^2$)
  - `camels_soil_moisture_lvl1_top`: Topsoil moisture ($kg/m^2$)
  - `camels_soil_moisture_lvl4_deep`: Deep soil moisture ($kg/m^2$)
  - `camels_soil_conductivity_top`: Topsoil hydraulic conductivity ($mm/hr$)
  - `camels_soil_awc_top`: Soil available water capacity ($mm$)
  - `camels_high_precip_freq_days`: Frequency of high precipitation events ($days/year$)
  - `camels_low_precip_freq_days`: Frequency of dry/low precipitation events ($days/year$)
  - `camels_elevation_mean_m`: Catchment mean elevation ($m$)
  - `camels_slope_mean_deg`: Catchment mean slope ($^\circ$)
  - `camels_forest_cover_pct`: Percentage forest cover (%)
  - `camels_dam_count`: Count of dams in catchment
  - `camels_dam_storage_capacity_mcm`: Total dam reservoir storage capacity ($MCM$)

## Connection to Final RESQ-AI Master Dataset & Flood Risk Model
In the final RESQ-AI master feature store, these hydrological and catchment attributes will be merged with:
1. **IMD Rainfall**: Dynamic daily precipitation and rolling antecedent rainfall.
2. **GFSM Susceptibility**: Static 30m flood susceptibility metrics.
3. **India Flood Inventory (IFI)**: Ground-truth historical flood events and inundated area damage labels.
4. **NASA GDIS**: Geocoded historical disaster events.
