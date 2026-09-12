# GFSM Metadata & Provenance Report

## 1. Dataset Origin & Credits
- **Dataset Name**: Global Flood Susceptibility Map (GFSM 30m)
- **Producer / Author**: Mirza Waleed (`waleedgeo@outlook.com`)
- **Publication / Generation UTC**: `2025-08-10T03:21:59Z`
- **Spatial Resolution**: 30 meters ($30\text{ m} \times 30\text{ m}$)
- **Coordinate System**: `EPSG:3395` (WGS 84 / World Mercator)

---

## 2. Classification Methodology & Encoding
- **Classification Scheme**: Equal-Interval Probability (`equal_interval_probability`)
- **Probability Edges**: `[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]`
- **Probability Decoding Formula**: $p \approx \text{pixel\_value} / 255$
- **NoData Rule**: Value `0` represents water/ocean bodies or unmapped non-land grid cells.
- **Cleaning Note**: Isolated-pixel majority clean-up applied on class map.

---

## 3. Integration into RESQ-AI Architecture
GFSM provides static, land-surface flood susceptibility metrics (slope, elevation, terrain depression, land cover characteristics).

It connects to the final RESQ-AI master dataset alongside:
- **IMD Rainfall**: Dynamic daily precipitation & antecedent wetness
- **CAMELS-IND**: Catchment hydrology, river runoff & soil moisture
- **India Flood Inventory (IFI)**: Historical flood events & inundated area ground truth
- **NASA GDIS**: Geocoded historical disaster events

> **PROVENANCE NOTICE**: GFSM represents static land-surface flood susceptibility. It is **NOT** a dynamic weather forecast and **NOT** a standalone flood prediction model.
