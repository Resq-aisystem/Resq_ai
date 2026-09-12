# RESQ-AI Model Card: IMD Rainfall Severity Classifier

**Platform**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Model Artifact**: `models/flood_risk/imd_baseline_model.pkl`  
**Model Type**: Supervised Multiclass Classification  

---

## 1. Model Details

- **Algorithm**: `sklearn.ensemble._forest.RandomForestClassifier`
- **Developer / Team**: RESQ-AI Engineering Team
- **Model Version**: `1.0.0`
- **Hyperparameters**:
  - `n_estimators`: `100`
  - `max_depth`: `10`
  - `class_weight`: `'balanced'`
  - `random_state`: `42`
- **Input Features (14 Verified Features)**:
  `['daily_normal_mm', 'cumulative_normal_mm', 'monthly_normal_mm', 'rolling_3d_rainfall_mm_lag1', 'rolling_7d_rainfall_mm_lag1', 'rolling_14d_rainfall_mm_lag1', 'rolling_30d_rainfall_mm_lag1', 'rolling_3d_max_mm_lag1', 'rolling_7d_max_mm_lag1', 'rolling_14d_max_mm_lag1', 'consecutive_rainy_days_lag1', 'rolling_7d_rainy_days_count_lag1', 'cumulative_actual_mm_lag1', 'monthly_actual_mm_lag1']`
- **Target Variable**: `rainfall_severity` (`LIGHT`, `MODERATE`, `HEAVY`, `EXTREME`)

---

## 2. Intended Use & Scope

- **Intended Use**: Classifies observed daily rainfall severity levels to serve as Layer 1 situational hazard intelligence within the RESQ-AI Production Risk Inference Engine.
- **Out-of-Scope / Non-Claims**:
  - **NOT** a 24–48 hour weather forecast model.
  - **NOT** a continuous rainfall amount (mm) regression model.
  - **NOT** a calibrated physical flood probability model.

---

## 3. Quantitative Evaluation Metrics

### Temporal Test Split Performance (Dates $\ge$ `2026-09-05`, 5,093 Test Rows)

| Evaluation Metric | Score Value | Interpretation |
| :--- | :---: | :--- |
| **Accuracy** | **68.05%** (0.680542) | Overall proportion of correct severity class predictions |
| **Weighted Precision** | **70.97%** (0.709655) | Class-weighted precision accounting for sample distribution |
| **Weighted Recall** | **68.05%** (0.680542) | Class-weighted recall matching accuracy |
| **Weighted F1 Score** | **68.87%** (0.688678) | Primary baseline classification metric under class imbalance |
| **Balanced Accuracy** | **45.11%** (0.451128) | Unweighted average recall across all four target classes |
| **Macro Precision** | **43.84%** (0.438438) | Equal-weighted precision across classes |
| **Macro Recall** | **45.11%** (0.451128) | Equal-weighted recall across classes |
| **Macro F1 Score** | **43.98%** (0.439806) | Equal-weighted F1 highlighting minority class performance |
| **Cohen's Kappa** | **0.3272** (0.327188) | Inter-rater agreement above chance classification |
| **Matthews Correlation Coefficient (MCC)** | **0.3345** (0.334451) | Balanced quality measure for multi-class classification |

### Per-Class Performance Breakdown

| Severity Class | Daily Actual Rainfall Range | Support (Rows) | Precision | Recall | F1 Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **LIGHT** | $< 2.5\text{ mm}$ | 3,437 | 0.81 | 0.69 | 0.75 |
| **MODERATE** | $2.5\text{ mm} \le \text{mm} < 64.5\text{ mm}$ | 1,640 | 0.50 | 0.66 | 0.57 |
| **HEAVY** | $64.5\text{ mm} \le \text{mm} < 115.6\text{ mm}$ | 16 | 0.00 | 0.00 | 0.00 |
| **EXTREME** | $\ge 115.6\text{ mm}$ | 0 | 0.00 | 0.00 | 0.00 |

---

## 4. Limitations & Ethical Considerations

1. **Class Imbalance & Minority Class Weakness**:
   - The temporal test set contained **0** EXTREME rainfall events and only **16** HEAVY rainfall events.
   - The model failed to predict any HEAVY events correctly (`F1 = 0.00`) due to extreme class imbalance in favor of LIGHT and MODERATE events.
2. **No Continuous Output**: The model outputs discrete severity categories, not continuous precipitation millimeters (`Rainfall amount regression accuracy: NOT AVAILABLE`).
3. **Decision Support Only**: Output probabilities reflect Random Forest class confidence, not real-world flood risk.
