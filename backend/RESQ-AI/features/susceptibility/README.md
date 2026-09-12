# RESQ-AI Susceptibility Feature Store

This directory contains terrain and land flood susceptibility feature layers extracted from the **Global Flood Susceptibility Map (GFSM 30m)** dataset.

## Primary Feature Dataset
- **File**: `features/susceptibility/gfsm_susceptibility_features.csv`
- **Rows**: 728 districts (matching IMD district geography)
- **Columns**:
  - `state`: Indian State / Union Territory name
  - `district`: District name
  - `gfsm_susceptibility_score`: Weighted mean susceptibility class score (1.0 to 5.0)
  - `gfsm_dominant_class`: Dominant susceptibility class (1=Very Low, 2=Low, 3=Moderate, 4=High, 5=Very High)
  - `gfsm_high_susceptibility_pct`: % district land area in High/Very High susceptibility (Classes 4 & 5)
  - `gfsm_very_high_susceptibility_pct`: % district land area in Very High susceptibility (Class 5)
  - `gfsm_class_1_pct` to `gfsm_class_5_pct`: Exact area distribution percentages across classes 1-5

## Connection to Final RESQ-AI Flood Risk Model
In the final RESQ-AI master feature store, these static terrain susceptibility features will be joined by district with dynamic weather inputs (IMD daily rainfall), hydrological attributes (CAMELS-IND catchment features), historical flood severity (IFI), and geocoded disaster events (GDIS) to produce explainable flood risk scores (0–100).
