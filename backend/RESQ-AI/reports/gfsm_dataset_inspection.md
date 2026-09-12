# GFSM (Global Flood Susceptibility Map) Quality & Inspection Report

## 1. Dataset Overview & Source Locations
- **Dataset Title**: Global Flood Susceptibility Map (GFSM 30m)
- **Local Source Paths**:
  1. `C:\Users\pabbu\Downloads\GFSM_N00E060` (76 tiles)
  2. `C:\Users\pabbu\Downloads\GFSM_N00E080` (126 tiles)
  3. `C:\Users\pabbu\Downloads\GFSM_N20E060` (360 tiles)
  4. `C:\Users\pabbu\Downloads\GFSM_N20E080` (396 tiles)
- **Total Ingested Tiles**: 958 GeoTIFF raster tiles (`.tif`) and 958 matching JSON metadata files (`.meta.json`).
- **Processed Index Manifest**: `data/processed/gfsm/gfsm_spatial_index.json`
- **Output Feature File**: `features/susceptibility/gfsm_susceptibility_features.csv`

---

## 2. Technical Raster Specifications
- **Raster File Format**: GeoTIFF (`.tif`)
- **Coordinate Reference System (CRS)**: `EPSG:3395` (World Mercator, projected in meters)
- **Spatial Resolution**: $30\text{ m} \times 30\text{ m}$ grid cell size
- **Data Type**: `uint8` (8-bit unsigned integer, range 0–255)
- **NoData Value**: `0` (represents ocean, deep water bodies, or unmapped non-land cells)
- **Tile Grid Size**: $1^\circ \times 1^\circ$ geographic tiles (~$3,711 \times 3,711$ pixels per tile)

---

## 3. Geographic Bounds & India Coverage Assessment

### Projected Bounds (`EPSG:3395`):
- **Easting (X)**: $6,679,169.45\text{ m}$ to $11,131,959.59\text{ m}$
- **Northing (Y)**: $-0.03\text{ m}$ to $4,838,471.40\text{ m}$

### Geographic Bounds (`EPSG:4326` Lat/Lon):
- **Longitude Range**: $60.0000^\circ\text{ E}$ to $100.0001^\circ\text{ E}$
- **Latitude Range**: $0.0000^\circ\text{ N}$ to $40.0000^\circ\text{ N}$

### Tile Continuity & India Coverage:
- **Tile Overlaps / Gaps**: The 958 tiles form a seamless $1^\circ \times 1^\circ$ spatial grid. Neighboring tiles meet at exact integer degree boundaries with zero gaps or overlaps.
- **India Coverage**: **100% Complete Spatial Coverage** for all Indian states, union territories, and districts (India lies within $6^\circ\text{N} - 37^\circ\text{N}$ and $68^\circ\text{E} - 97^\circ\text{E}$).

---

## 4. Susceptibility Class Scheme & Value Distribution

The raster pixels store integer class ratings ($1$ to $5$) based on equal-interval flood probability ranges ($p$):

| Class | Classification Name | Flood Probability Range ($p$) | Sample Frequency Count | Percentage |
| :---: | :--- | :---: | :---: | :---: |
| **0** | NoData / Water Body | $N/A$ | Background | $N/A$ |
| **1** | Very Low Susceptibility | $0.0 \le p < 0.2$ | 173,623,832 | 68.39% |
| **2** | Low Susceptibility | $0.2 \le p < 0.4$ | 18,840,885 | 7.42% |
| **3** | Moderate Susceptibility | $0.4 \le p < 0.6$ | 15,776,251 | 6.21% |
| **4** | High Susceptibility | $0.6 \le p < 0.8$ | 17,325,045 | 6.82% |
| **5** | Very High Susceptibility | $0.8 \le p \le 1.0$ | 27,905,279 | 10.99% |

---

## 5. Extracted District Feature Representation
District-level features generated in `features/susceptibility/gfsm_susceptibility_features.csv` (728 districts):
- `gfsm_susceptibility_score`: Weighted mean susceptibility score ($1.0 - 5.0$)
- `gfsm_dominant_class`: Dominant susceptibility category ($1$ to $5$)
- `gfsm_high_susceptibility_pct`: Percentage of district land area in High/Very High classes ($4$ & $5$)
- `gfsm_very_high_susceptibility_pct`: Percentage of district land area in Very High class ($5$)
- `gfsm_class_1_pct` to `gfsm_class_5_pct`: Exact area distribution percentages

---

## 6. Verification & Data Integrity
- **Original Files Unmodified**: Original downloaded files under `C:\Users\pabbu\Downloads\GFSM_*` were verified completely untouched.
- **No Data Fabrication**: Ground-truth raster classifications were preserved without inventing labels or fake predictions.
