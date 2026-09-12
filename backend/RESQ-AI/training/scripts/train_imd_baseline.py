"""
IMD Rainfall Severity Baseline Model Training Script for RESQ-AI.

Trains a Random Forest baseline classifier on historical IMD rainfall features.
Strictly prevents target leakage using lagged antecedent features.
Saves model binary, evaluation metrics, confusion matrix plots, feature importance,
SHAP explanations (if library available), and comprehensive markdown report.
"""

import json
import os
from pathlib import Path
import pickle
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FEATURE_PATH = BASE_DIR / "features" / "rainfall" / "imd_rainfall_features.csv"

MODEL_SAVE_PATH = BASE_DIR / "models" / "flood_risk" / "imd_baseline_model.pkl"
METRICS_JSON_PATH = BASE_DIR / "evaluation" / "metrics" / "imd_baseline_metrics.json"
CM_JSON_PATH = BASE_DIR / "evaluation" / "metrics" / "imd_confusion_matrix.json"
CM_PLOT_PATH = BASE_DIR / "evaluation" / "plots" / "imd_confusion_matrix.png"
FI_CSV_PATH = BASE_DIR / "evaluation" / "metrics" / "imd_feature_importance.csv"
FI_PLOT_PATH = BASE_DIR / "evaluation" / "plots" / "imd_feature_importance.png"
SHAP_DIR = BASE_DIR / "explainability" / "shap"
REPORT_MD_PATH = BASE_DIR / "evaluation" / "reports" / "imd_baseline_report.md"


def get_severity(mm):
    """IMD Standard Rainfall Intensity Threshold Classification."""
    if mm < 2.5:
        return 'LIGHT'
    elif mm < 64.5:
        return 'MODERATE'
    elif mm < 115.6:
        return 'HEAVY'
    else:
        return 'EXTREME'


def train_baseline():
    print(f"[IMD Baseline] Loading feature dataset from: {FEATURE_PATH}")
    df = pd.read_csv(FEATURE_PATH)
    print(f"[IMD Baseline] Initial shape: {df.shape}")

    # 1. Target Definition
    df['rainfall_severity'] = df['daily_actual_mm'].apply(get_severity)
    class_order = ['LIGHT', 'MODERATE', 'HEAVY', 'EXTREME']

    # Sort deterministically
    df = df.sort_values(by=['state', 'district', 'date']).reset_index(drop=True)

    # 2. Prevent Target Leakage: Use antecedent (lag1) features for rolling predictors
    grouped = df.groupby(['state', 'district'])

    feature_cols = [
        'daily_normal_mm',
        'cumulative_normal_mm',
        'monthly_normal_mm',
        'rolling_3d_rainfall_mm_lag1',
        'rolling_7d_rainfall_mm_lag1',
        'rolling_14d_rainfall_mm_lag1',
        'rolling_30d_rainfall_mm_lag1',
        'rolling_3d_max_mm_lag1',
        'rolling_7d_max_mm_lag1',
        'rolling_14d_max_mm_lag1',
        'consecutive_rainy_days_lag1',
        'rolling_7d_rainy_days_count_lag1',
        'cumulative_actual_mm_lag1',
        'monthly_actual_mm_lag1'
    ]

    df_lagged = df.copy()
    lag_sources = [
        'rolling_3d_rainfall_mm', 'rolling_7d_rainfall_mm', 'rolling_14d_rainfall_mm', 'rolling_30d_rainfall_mm',
        'rolling_3d_max_mm', 'rolling_7d_max_mm', 'rolling_14d_max_mm',
        'consecutive_rainy_days', 'rolling_7d_rainy_days_count',
        'cumulative_actual_mm', 'monthly_actual_mm'
    ]
    for col in lag_sources:
        df_lagged[f'{col}_lag1'] = grouped[col].shift(1)

    df_lagged = df_lagged.fillna(0)

    # 3. Time-Aware Split (Train <= 2026-09-04, Test >= 2026-09-05)
    train_df = df_lagged[df_lagged['date'] <= '2026-09-04']
    test_df = df_lagged[df_lagged['date'] >= '2026-09-05']

    X_train = train_df[feature_cols]
    y_train = train_df['rainfall_severity']

    X_test = test_df[feature_cols]
    y_test = test_df['rainfall_severity']

    print(f"[IMD Baseline] Train samples: {len(X_train)} (dates <= 2026-09-04)")
    print(f"[IMD Baseline] Test samples: {len(X_test)} (dates >= 2026-09-05)")

    # 4. Train Model
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    rf.fit(X_train, y_train)

    # Save Model Artifact
    MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_SAVE_PATH, 'wb') as f:
        pickle.dump(rf, f)
    print(f"[IMD Baseline] Saved model binary to: {MODEL_SAVE_PATH}")

    # 5. Evaluate Model on Test Set
    y_pred = rf.predict(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)

    cm = confusion_matrix(y_test, y_pred, labels=class_order)
    correct_count = int(np.trace(cm))
    incorrect_count = int(len(y_test) - correct_count)

    print(f"[IMD Baseline] Accuracy: {acc * 100:.2f}%")
    print(f"[IMD Baseline] Macro F1: {f1_m * 100:.2f}%")
    print(f"[IMD Baseline] Weighted F1: {f1_w * 100:.2f}%")

    # Save Confusion Matrix JSON & Plot
    CM_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    cm_dict = {
        "labels": class_order,
        "matrix": cm.tolist()
    }
    with open(CM_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(cm_dict, f, indent=2)

    CM_PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap='Blues')
    plt.colorbar(im)
    ax.set_xticks(np.arange(len(class_order)))
    ax.set_yticks(np.arange(len(class_order)))
    ax.set_xticklabels(class_order)
    ax.set_yticklabels(class_order)
    plt.xlabel('Predicted Severity')
    plt.ylabel('Actual Severity')
    plt.title('IMD Baseline Confusion Matrix (Test Set)')
    for i in range(len(class_order)):
        for j in range(len(class_order)):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', color='red' if cm[i, j] > cm.max()/2 else 'black')
    plt.tight_layout()
    plt.savefig(CM_PLOT_PATH, dpi=150)
    plt.close()

    # 6. Feature Importances
    importances = rf.feature_importances_
    fi_df = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False).reset_index(drop=True)

    FI_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fi_df.to_csv(FI_CSV_PATH, index=False)

    FI_PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 6))
    plt.barh(fi_df['Feature'][::-1], fi_df['Importance'][::-1], color='navy')
    plt.xlabel('Random Forest Feature Importance')
    plt.title('IMD Rainfall Severity Top Features')
    plt.tight_layout()
    plt.savefig(FI_PLOT_PATH, dpi=150)
    plt.close()

    # 7. SHAP Check
    SHAP_DIR.mkdir(parents=True, exist_ok=True)
    shap_status = "Not Available (ModuleNotFoundError: 'shap' package not installed in environment)"
    try:
        import shap
        explainer = shap.TreeExplainer(rf)
        shap_vals = explainer.shap_values(X_test.iloc[:500])
        shap_plot_path = SHAP_DIR / "imd_shap_summary.png"
        plt.figure(figsize=(8, 6))
        shap.summary_plot(shap_vals, X_test.iloc[:500], plot_type="bar", show=False)
        plt.tight_layout()
        plt.savefig(shap_plot_path, dpi=150)
        plt.close()
        shap_status = "Available (SHAP summary plot saved)"
    except Exception as e:
        shap_status = f"Not Available ({type(e).__name__}: {str(e)})"

    # 8. Save Metrics JSON
    class_dist_train = y_train.value_counts().to_dict()
    class_dist_test = y_test.value_counts().to_dict()

    metrics_payload = {
        "model_name": "IMD Rainfall Severity Baseline Model",
        "model_type": "IMD_RAINFALL_SEVERITY_BASELINE",
        "dataset_path": str(FEATURE_PATH),
        "target_name": "rainfall_severity",
        "train_size": len(X_train),
        "test_size": len(X_test),
        "split_method": "Temporal split (Train <= 2026-09-04, Test >= 2026-09-05)",
        "feature_names": feature_cols,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision_macro": round(float(prec_m), 4),
            "recall_macro": round(float(rec_m), 4),
            "f1_macro": round(float(f1_m), 4),
            "precision_weighted": round(float(prec_w), 4),
            "recall_weighted": round(float(rec_w), 4),
            "f1_weighted": round(float(f1_w), 4),
            "correct_predictions": correct_count,
            "incorrect_predictions": incorrect_count
        },
        "class_distribution_train": class_dist_train,
        "class_distribution_test": class_dist_test,
        "confusion_matrix": cm_dict,
        "shap_status": shap_status
    }

    with open(METRICS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(metrics_payload, f, indent=2)

    # 9. Generate Report Markdown
    top_fi_str = "\n".join([f"- **{row['Feature']}**: {row['Importance']:.4f}" for _, row in fi_df.head(5).iterrows()])

    report_content = f"""# IMD Rainfall Severity Baseline Model Report

## 1. Model Objective
This baseline model predicts **Rainfall Severity** (`LIGHT`, `MODERATE`, `HEAVY`, `EXTREME`) for geographical districts using historical daily and antecedent rainfall features from IMD.

> **CRITICAL DISCLAIMER**:
> This is an **observed-rainfall severity baseline model**.
> It is **NOT** a 24–48 hour weather forecast model and is **NOT** the final RESQ-AI flood-risk model.

---

## 2. Dataset Provenance & Dimensions
- **Dataset File**: `{FEATURE_PATH}`
- **Total Dataset Rows**: {len(df)}
- **Train Rows**: {len(X_train)} (Observations $\\le$ 2026-09-04)
- **Test Rows**: {len(X_test)} (Observations $\\ge$ 2026-09-05)

---

## 3. Target Definition & Selection Rationale
- **Target Name**: `rainfall_severity`
- **Classes**:
  - `LIGHT`: Daily actual rainfall $< 2.5$ mm
  - `MODERATE`: $2.5 \\text{{ mm}} \\le$ Daily actual rainfall $< 64.5$ mm
  - `HEAVY`: $64.5 \\text{{ mm}} \\le$ Daily actual rainfall $< 115.6$ mm
  - `EXTREME`: Daily actual rainfall $\\ge 115.6$ mm
- **Why Selected**: Provides a meteorologically valid ground-truth classification of rainfall intensity based on IMD standard thresholds without inventing unverified flood targets.

---

## 4. Features & Leakage Prevention
To prevent zero-lag intra-day target leakage, `daily_actual_mm` and instantaneous flags (`is_rainy_day`, `is_heavy_rainy_day`, `rainfall_anomaly_mm`) were **excluded** from the predictor feature set $X$.

All rolling window features (`rolling_3d_rainfall_mm`, `rolling_7d_rainfall_mm`, etc.) were shifted by 1 day per district (`lag1`), ensuring that predictor variables contain strictly **antecedent historical data up to day $t-1$** alongside daily climatological normal values.

### Predictor Features Used:
{", ".join(feature_cols)}

---

## 5. Model Configuration & Training
- **Algorithm**: `RandomForestClassifier` (scikit-learn)
- **Parameters**: `n_estimators=100`, `max_depth=10`, `random_state=42`, `class_weight='balanced'`
- **Model Binary Artifact**: `{MODEL_SAVE_PATH}`

---

## 6. Actual Model Performance (Held-Out Test Set)

- **Accuracy**: **{acc * 100:.2f}%**
- **Macro Precision**: **{prec_m * 100:.2f}%**
- **Macro Recall**: **{rec_m * 100:.2f}%**
- **Macro F1 Score**: **{f1_m * 100:.2f}%**
- **Weighted Precision**: **{prec_w * 100:.2f}%**
- **Weighted Recall**: **{rec_w * 100:.2f}%**
- **Weighted F1 Score**: **{f1_w * 100:.2f}%**

### Sample Counts:
- **Test Samples**: {len(X_test)}
- **Correct Predictions**: {correct_count}
- **Incorrect Predictions**: {incorrect_count}

---

## 7. Confusion Matrix (Test Set)

```
Labels: {class_order}
{cm}
```

---

## 8. Top Contributing Rainfall Features
{top_fi_str}

- **Feature Importance File**: `{FI_CSV_PATH}`
- **Feature Importance Plot**: `{FI_PLOT_PATH}`

---

## 9. SHAP Explainability Status
- **SHAP Status**: `{shap_status}`

---

## 10. Limitations & Confirmations
1. **No Forecast Capability**: Model uses historical antecedent observations up to $t-1$; it does not predict future weather forecasts.
2. **No Flood Prediction**: Model measures rainfall intensity severity, not ground flood risk or catchment inundation.
3. **Single Dataset**: Built exclusively on IMD data. Will be combined with GFSM, CAMELS-IND, IFI, and GDIS in subsequent stages to form the complete RESQ-AI platform.
"""

    REPORT_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_MD_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"[IMD Baseline] Detailed markdown report generated at: {REPORT_MD_PATH}")

    return metrics_payload, fi_df, cm, shap_status


if __name__ == "__main__":
    train_baseline()
