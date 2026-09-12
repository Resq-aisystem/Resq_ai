# IMD Rainfall Severity Baseline Model Report

## 1. Model Objective
This baseline model predicts **Rainfall Severity** (`LIGHT`, `MODERATE`, `HEAVY`, `EXTREME`) for geographical districts using historical daily and antecedent rainfall features from IMD.

> **CRITICAL DISCLAIMER**:
> This is an **observed-rainfall severity baseline model**.
> It is **NOT** a 24–48 hour weather forecast model and is **NOT** the final RESQ-AI flood-risk model.

---

## 2. Dataset Provenance & Dimensions
- **Dataset File**: `C:\Users\pabbu\Desktop\RESQ-AI\features\rainfall\imd_rainfall_features.csv`
- **Total Dataset Rows**: 17457
- **Train Rows**: 12364 (Observations $\le$ 2026-09-04)
- **Test Rows**: 5093 (Observations $\ge$ 2026-09-05)

---

## 3. Target Definition & Selection Rationale
- **Target Name**: `rainfall_severity`
- **Classes**:
  - `LIGHT`: Daily actual rainfall $< 2.5$ mm
  - `MODERATE`: $2.5 \text{ mm} \le$ Daily actual rainfall $< 64.5$ mm
  - `HEAVY`: $64.5 \text{ mm} \le$ Daily actual rainfall $< 115.6$ mm
  - `EXTREME`: Daily actual rainfall $\ge 115.6$ mm
- **Why Selected**: Provides a meteorologically valid ground-truth classification of rainfall intensity based on IMD standard thresholds without inventing unverified flood targets.

---

## 4. Features & Leakage Prevention
To prevent zero-lag intra-day target leakage, `daily_actual_mm` and instantaneous flags (`is_rainy_day`, `is_heavy_rainy_day`, `rainfall_anomaly_mm`) were **excluded** from the predictor feature set $X$.

All rolling window features (`rolling_3d_rainfall_mm`, `rolling_7d_rainfall_mm`, etc.) were shifted by 1 day per district (`lag1`), ensuring that predictor variables contain strictly **antecedent historical data up to day $t-1$** alongside daily climatological normal values.

### Predictor Features Used:
daily_normal_mm, cumulative_normal_mm, monthly_normal_mm, rolling_3d_rainfall_mm_lag1, rolling_7d_rainfall_mm_lag1, rolling_14d_rainfall_mm_lag1, rolling_30d_rainfall_mm_lag1, rolling_3d_max_mm_lag1, rolling_7d_max_mm_lag1, rolling_14d_max_mm_lag1, consecutive_rainy_days_lag1, rolling_7d_rainy_days_count_lag1, cumulative_actual_mm_lag1, monthly_actual_mm_lag1

---

## 5. Model Configuration & Training
- **Algorithm**: `RandomForestClassifier` (scikit-learn)
- **Parameters**: `n_estimators=100`, `max_depth=10`, `random_state=42`, `class_weight='balanced'`
- **Model Binary Artifact**: `C:\Users\pabbu\Desktop\RESQ-AI\models\flood_risk\imd_baseline_model.pkl`

---

## 6. Actual Model Performance (Held-Out Test Set)

- **Accuracy**: **68.05%**
- **Macro Precision**: **43.84%**
- **Macro Recall**: **45.11%**
- **Macro F1 Score**: **43.98%**
- **Weighted Precision**: **70.97%**
- **Weighted Recall**: **68.05%**
- **Weighted F1 Score**: **68.87%**

### Sample Counts:
- **Test Samples**: 5093
- **Correct Predictions**: 3466
- **Incorrect Predictions**: 1627

---

## 7. Confusion Matrix (Test Set)

```
Labels: ['LIGHT', 'MODERATE', 'HEAVY', 'EXTREME']
[[2384 1048    5    0]
 [ 555 1082    3    0]
 [   1   15    0    0]
 [   0    0    0    0]]
```

---

## 8. Top Contributing Rainfall Features
- **cumulative_normal_mm**: 0.1303
- **daily_normal_mm**: 0.0948
- **monthly_normal_mm**: 0.0941
- **rolling_14d_max_mm_lag1**: 0.0789
- **monthly_actual_mm_lag1**: 0.0765

- **Feature Importance File**: `C:\Users\pabbu\Desktop\RESQ-AI\evaluation\metrics\imd_feature_importance.csv`
- **Feature Importance Plot**: `C:\Users\pabbu\Desktop\RESQ-AI\evaluation\plots\imd_feature_importance.png`

---

## 9. SHAP Explainability Status
- **SHAP Status**: `Not Available (ModuleNotFoundError: No module named 'shap')`

---

## 10. Limitations & Confirmations
1. **No Forecast Capability**: Model uses historical antecedent observations up to $t-1$; it does not predict future weather forecasts.
2. **No Flood Prediction**: Model measures rainfall intensity severity, not ground flood risk or catchment inundation.
3. **Single Dataset**: Built exclusively on IMD data. Will be combined with GFSM, CAMELS-IND, IFI, and GDIS in subsequent stages to form the complete RESQ-AI platform.
