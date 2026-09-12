"""
IMD Rainfall Severity Baseline Prediction Interface for RESQ-AI.

Exposes a production-ready prediction endpoint for backend integration.
Clearly identifies as IMD_RAINFALL_SEVERITY_BASELINE.
"""

from pathlib import Path
import pickle
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "models" / "flood_risk" / "imd_baseline_model.pkl"

_MODEL_CACHE = None


def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model binary not found at: {MODEL_PATH}")
        with open(MODEL_PATH, "rb") as f:
            _MODEL_CACHE = pickle.load(f)
    return _MODEL_CACHE


FEATURE_NAMES = [
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


def predict_rainfall_severity(features_input: dict) -> dict:
    """
    Predict rainfall severity level using trained IMD baseline model.

    Args:
        features_input: dict containing feature names and numerical values matching FEATURE_NAMES.

    Returns:
        dict structured response payload.
    """
    model = _get_model()

    # Construct DataFrame row
    row_data = {feat: [features_input.get(feat, 0.0)] for feat in FEATURE_NAMES}
    X_df = pd.DataFrame(row_data)

    pred_class = str(model.predict(X_df)[0])
    probs = model.predict_proba(X_df)[0]
    classes = list(model.classes_)
    prob_dict = {cls_name: round(float(prob), 4) for cls_name, prob in zip(classes, probs)}
    confidence = float(np.max(probs))

    return {
        "model_type": "IMD_RAINFALL_SEVERITY_BASELINE",
        "predicted_severity": pred_class,
        "confidence": round(confidence, 4),
        "class_probabilities": prob_dict,
        "disclaimer": "This is an IMD observed-rainfall severity baseline model. It is NOT a 24–48 hour forecast and NOT the final RESQ-AI flood-risk model."
    }
