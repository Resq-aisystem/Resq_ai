# RESQ-AI IMD Baseline Model Reproduction Test Report

**Project**: RESQ-AI — Disaster Early Warning & Rescue Intelligence Platform  
**Model Artifact**: `models/flood_risk/imd_baseline_model.pkl`  
**Test Date**: 2026-09-12  
**Result**: `IMD MODEL REPRODUCTION TEST: PASS`  

---

## 1. Model Artifact Inspection & Integrity

Empirical inspection of the binary model artifact confirmed the following parameters:

- **Model Class**: `sklearn.ensemble._forest.RandomForestClassifier`
- **Estimators (`n_estimators`)**: `100`
- **Max Depth (`max_depth`)**: `10`
- **Class Weight (`class_weight`)**: `'balanced'`
- **Random State (`random_state`)**: `42`
- **Input Features Count (`n_features_in_`)**: `14`
- **Feature Names**: `['daily_normal_mm', 'cumulative_normal_mm', 'monthly_normal_mm', 'rolling_3d_rainfall_mm_lag1', 'rolling_7d_rainfall_mm_lag1', 'rolling_14d_rainfall_mm_lag1', 'rolling_30d_rainfall_mm_lag1', 'rolling_3d_max_mm_lag1', 'rolling_7d_max_mm_lag1', 'rolling_14d_max_mm_lag1', 'consecutive_rainy_days_lag1', 'rolling_7d_rainy_days_count_lag1', 'cumulative_actual_mm_lag1', 'monthly_actual_mm_lag1']`
- **Class Labels (`classes_`)**: `['EXTREME', 'HEAVY', 'LIGHT', 'MODERATE']`
- **Artifact Integrity**: **PASS** (Loads without error, input schema matches training dataset).

---

## 2. Dataset & Temporal Test Split Reproduction

The original temporal split was reproduced without data shuffling or random splits:

- **Feature Source**: `features/rainfall/imd_rainfall_features.csv`
- **Training Period**: `date <= 2026-09-04`
- **Temporal Test Period**: `date >= 2026-09-05`
- **Test Sample Count**: **5,093 rows**

---

## 3. Metrics Reproduction Comparison

| Evaluation Metric | Original Baseline Metric | Newly Reproduced Metric | Difference | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | 68.05% | **68.05%** (0.680542) | 0.00% | **EXACT MATCH** |
| **Weighted Precision** | 70.97% | **70.97%** (0.709655) | 0.00% | **EXACT MATCH** |
| **Weighted Recall** | 68.05% | **68.05%** (0.680542) | 0.00% | **EXACT MATCH** |
| **Weighted F1 Score** | 68.87% | **68.87%** (0.688678) | 0.00% | **EXACT MATCH** |
| **Macro Precision** | 43.84% | **43.84%** (0.438438) | 0.00% | **EXACT MATCH** |
| **Macro Recall** | 45.11% | **45.11%** (0.451128) | 0.00% | **EXACT MATCH** |
| **Macro F1 Score** | 43.98% | **43.98%** (0.439806) | 0.00% | **EXACT MATCH** |

---

## 4. Confusion Matrix & Classification Report

### Confusion Matrix (Class Order: `LIGHT`, `MODERATE`, `HEAVY`, `EXTREME`)

```
[[2384, 1048,    5,    0],   # Actual LIGHT
 [ 555, 1082,    3,    0],   # Actual MODERATE
 [   1,   15,    0,    0],   # Actual HEAVY
 [   0,    0,    0,    0]]   # Actual EXTREME
```

### Classification Report

```
              precision    recall  f1-score   support

       LIGHT       0.81      0.69      0.75      3437
    MODERATE       0.50      0.66      0.57      1640
       HEAVY       0.00      0.00      0.00        16
     EXTREME       0.00      0.00      0.00         0

    accuracy                           0.68      5093
   macro avg       0.33      0.34      0.33      5093
weighted avg       0.71      0.68      0.69      5093
```

---

## 5. Model Inference & Probability Sanity Check

`predict_proba()` was verified on real test set samples. Probabilities sum strictly to `1.0000` across the 4 class labels:

1. **Sample 1** (Date: `2026-09-07`, State: `CHHATISGARH`, District: `RAIPUR`):
   - **Actual**: `LIGHT` | **Predicted**: `MODERATE`
   - **Probabilities**: `LIGHT`: 45.56%, `MODERATE`: 48.12%, `HEAVY`: 4.38%, `EXTREME`: 1.94% (Sum = 1.0000)
2. **Sample 2** (Date: `2026-09-08`, State: `PUNJAB`, District: `MOGA`):
   - **Actual**: `LIGHT` | **Predicted**: `LIGHT`
   - **Probabilities**: `LIGHT`: 86.45%, `MODERATE`: 13.55%, `HEAVY`: 0.00%, `EXTREME`: 0.00% (Sum = 1.0000)
3. **Sample 3** (Date: `2026-09-06`, State: `CHHATISGARH`, District: `BEMETARA`):
   - **Actual**: `LIGHT` | **Predicted**: `MODERATE`
   - **Probabilities**: `LIGHT`: 47.13%, `MODERATE`: 49.64%, `HEAVY`: 2.24%, `EXTREME`: 0.99% (Sum = 1.0000)

> [!NOTE]
> **Probability Interpretation Warning**: Random Forest class probabilities represent internal classification confidence for observed rainfall severity. They do **NOT** represent physical flood probabilities.

---

## 6. Critical Interpretation & Limitations

> [!IMPORTANT]
> - *"This test validates reproducibility of the existing IMD rainfall severity model."*
> - *"This test does NOT prove 24–48 hour flood prediction."*
> - *"This test does NOT prove future disaster prediction."*

### Class Imbalance Analysis:
- **EXTREME Severity**: Contained `0` test samples in the temporal test set.
- **HEAVY Severity**: Contained only `16` test samples (`0` correctly predicted due to strong class dominance of LIGHT and MODERATE).
- **Metric Significance**: Overall accuracy alone (68.05%) is heavily influenced by majority class performance; macro F1 (43.98%) reflects true multi-class performance under imbalance.

---

## 7. Test Suite Validation Results

- **IMD Model Tests (`tests/test_imd_model.py`)**: **PASS** (2/2 tests passed)
- **Complete Repository Tests (`python -m unittest discover -s tests`)**: **PASS** (80/80 tests passed)

---

### FINAL STATUS

**IMD MODEL REPRODUCTION TEST: PASS**
