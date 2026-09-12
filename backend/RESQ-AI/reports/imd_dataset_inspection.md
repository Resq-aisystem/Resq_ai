# IMD District-Wise Daily Rainfall Dataset Quality & Inspection Report

## 1. Dataset Source & Location
- **Original Source File**: `C:\Users\pabbu\Downloads\rainfall_districtwise_daily_imd.csv.csv`
- **Cleaned Target File**: `data/processed/imd/imd_rainfall_cleaned.csv`
- **Feature Target File**: `features/rainfall/imd_rainfall_features.csv`
- **Summary JSON**: `data/interim/imd_dataset_summary.json`

---

## 2. Original Dimensions
- **Total Rows**: 17,457
- **Total Columns**: 22

---

## 3. Original Columns
1. `State` (object)
2. `District` (object)
3. `Date` (object)
4. `Daily Actual` (float64)
5. `Daily Normal` (float64)
6. `Daily Departure Per` (object)
7. `Daily Category` (object)
8. `Week Date` (object)
9. `Weekly \nActual` (float64)
10. `Weekly Normal` (float64)
11. `Weekly Departure Per` (object)
12. `Weekly Category` (object)
13. `Cumulative Date` (object)
14. `Cumulative Actual` (float64)
15. `Cumulative Normal` (float64)
16. `Cumulative Departue Per` (object)
17. `Cumulative \nCategory` (object)
18. `Monthly Date` (object)
19. `Monthly Acutual` (float64)
20. `Monthly Normal` (float64)
21. `Monthly \nDeparture Per` (object)
22. `Monthly Category` (object)

---

## 4. Initial Missing-Value Analysis

| Raw Column Name | Null Count | Null Percentage | Rationale / Underlying Status |
| :--- | :---: | :---: | :--- |
| `State` | 0 | 0.00% | Fully populated |
| `District` | 0 | 0.00% | Fully populated |
| `Date` | 0 | 0.00% | Fully populated |
| `Daily Actual` | 0 | 0.00% | Fully populated |
| `Daily Normal` | 0 | 0.00% | Fully populated |
| `Daily Departure Per` | 219 | 1.25% | Category is `ND` (No Data available for departure calc) |
| `Daily Category` | 0 | 0.00% | Fully populated (`NR`, `LD`, `D`, `N`, `E`, `LE`, `ND`) |
| `Week Date` | 0 | 0.00% | Fully populated |
| `Weekly \nActual` | 0 | 0.00% | Fully populated |
| `Weekly Normal` | 0 | 0.00% | Fully populated |
| `Weekly Departure Per` | 163 | 0.93% | Departure undefined or missing |
| `Weekly Category` | 0 | 0.00% | Fully populated |
| `Cumulative Date` | 0 | 0.00% | Fully populated |
| `Cumulative Actual` | 0 | 0.00% | Fully populated |
| `Cumulative Normal` | 0 | 0.00% | Fully populated |
| `Cumulative Departue Per` | 120 | 0.69% | Departure undefined or missing |
| `Cumulative \nCategory` | 0 | 0.00% | Fully populated |
| `Monthly Date` | 0 | 0.00% | Fully populated |
| `Monthly Acutual` | 0 | 0.00% | Fully populated |
| `Monthly Normal` | 0 | 0.00% | Fully populated |
| `Monthly \nDeparture Per` | 125 | 0.72% | Departure undefined or missing |
| `Monthly Category` | 0 | 0.00% | Fully populated |

---

## 5. Duplicate Analysis
- **Full Row Duplicates**: 0
- **Duplicate Date-District Combinations**: 0

---

## 6. Date & Geographic Coverage
- **Temporal Range**: `2026-08-19` to `2026-09-11`
- **Total Unique Observation Days**: 24 days
- **Unique States / UTs**: 39
- **Unique Districts**: 728
- **Date Continuity**: 727 districts contain complete 24-day observations; 1 district (`NAGAPATTINAM`, Tamil Nadu) contains 9 recorded daily observations.

---

## 7. Numerical Rainfall Distribution Summary

| Column Name | Min (mm) | Max (mm) | Mean (mm) | Median (mm) | Std Dev (mm) | Zero Records (%) | Negative Values |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Daily Actual`** | 0.0 | 145.7 | 6.03 | 1.0 | 11.92 | 6,049 (34.65%) | 0 |
| **`Daily Normal`** | 0.0 | 94.5 | 7.68 | 6.8 | 4.72 | 29 (0.17%) | 0 |
| **`Weekly Actual`** | 0.0 | 407.6 | 36.01 | 16.9 | 48.02 | 2,289 (13.11%) | 0 |
| **`Weekly Normal`** | 0.0 | 255.6 | 44.72 | 42.4 | 34.08 | 7 (0.04%) | 0 |
| **`Cumulative Actual`** | 0.0 | 2,980.3 | 648.57 | 538.9 | 477.26 | 120 (0.69%) | 0 |
| **`Cumulative Normal`** | 6.3 | 4,040.6 | 768.38 | 681.3 | 515.58 | 0 (0.00%) | 0 |
| **`Monthly Actual`** | 0.0 | 928.3 | 122.35 | 76.9 | 134.28 | 1,014 (5.81%) | 0 |
| **`Monthly Normal`** | 0.0 | 976.3 | 142.39 | 96.8 | 130.69 | 3 (0.02%) | 0 |

---

## 8. Invalid & Suspicious Values
- **Negative Rainfall Values**: 0 found across all columns.
- **Impossible / Out-of-Bounds Values**: 0 found. Peak daily actual rainfall recorded was 145.7 mm (Niwari district, MP on 2026-08-27), which represents plausible extreme heavy monsoon rainfall.
- **Non-numeric Strings in Numeric Columns**: 0 found.

---

## 9. Cleaning Actions Taken
1. **Raw File Safety Preserved**: Original CSV `C:\Users\pabbu\Downloads\rainfall_districtwise_daily_imd.csv.csv` was verified untouched (file size and timestamp unmodified).
2. **Column Standardization**: Raw column names sanitized into clean pythonic snake_case identifiers (e.g. `Weekly \nActual` → `weekly_actual_mm`, `Monthly Acutual` → `monthly_actual_mm`).
3. **String Sanitization**: Removed carriage returns (`\r`), newlines (`\n`), and trailing whitespace from location strings and category values.
4. **Date Normalization**: Standardized `Date` column into ISO `YYYY-MM-DD` string format.
5. **Percentage String Parsing**: Stripped `%` symbols and converted departure percentages to `float64` values while preserving `NaN` for `ND` (No Data) categories without inventing values.
6. **Zero Rows Removed**: All 17,457 valid observation rows retained.

---

## 10. Final Dataset Metrics
- **Rows Removed**: 0
- **Rows Retained**: 17,457 (100.0%)
- **Final Cleaned Dimensions**: 17,457 rows × 22 columns
- **Final Feature Matrix Dimensions**: 17,457 rows × 23 feature columns

---

## 11. Final Data Quality Assessment
The IMD District-wise Daily Rainfall Dataset is of **EXCELLENT DATA QUALITY**. Data integrity is verified, geographic & temporal fields are 100% complete, no corrupt records exist, and rainfall distributions follow expected meteorological monsoon patterns.
