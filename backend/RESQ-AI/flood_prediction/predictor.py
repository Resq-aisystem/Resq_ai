"""
6-Hour Predictive Flood Intelligence Interface for RESQ-AI.

Combines 6-hour weather forecast series with observed IMD rainfall baseline predictions,
GFSM terrain flood susceptibility, and CAMELS hydrology features.
"""

from typing import Dict, Any, Optional
import numpy as np

from forecast.forecast_client import fetch_6hour_forecast
from flood_prediction.schemas import FloodPredictionPayload
from inference.risk_engine import get_district_risk


def predict_6hour_flood_risk(
    city_name: str = "Puri",
    district_name: str = "PURI",
    observation_date: str = None,
    forecast_override=None
) -> FloodPredictionPayload:
    """
    Predict 6-hour forward-looking flood risk score and level for target location.

    Args:
        city_name: Name of city MVP.
        district_name: Administrative district.
        observation_date: ISO date string 'YYYY-MM-DD'.
        forecast_override: Optional custom ForecastPayload for scenario analysis.

    Returns:
        FloodPredictionPayload object.
    """
    # 1. Fetch 6-hour forecast
    if forecast_override:
        f_payload = forecast_override
    else:
        f_payload = fetch_6hour_forecast(city_name=city_name, district_name=district_name)

    tot_mm = f_payload.total_6h_rainfall_mm()
    peak_mm = f_payload.peak_1h_rainfall_mm()

    # 2. Fetch baseline risk score from Risk Engine
    risk_output = get_district_risk(district_name, observation_date)
    risk_dict = risk_output.to_dict()
    base_risk = float(risk_dict["risk_score"])
    ev_qual = risk_dict["evidence_quality"]

    # 3. Compute 6-hour Forecast Rainfall Impact Factor
    # Scale total 6h rainfall (e.g. 50mm -> 40 points) and peak 1h rainfall (e.g. 25mm -> 30 points)
    f_impact = np.clip(tot_mm * 0.8 + peak_mm * 1.2, 0.0, 100.0)

    # 4. Composite Forward Risk Score (60% baseline situational risk + 40% 6h forecast impact)
    comp_score = float(np.clip(round(0.60 * base_risk + 0.40 * f_impact, 2), 0.0, 100.0))

    # 5. Assign Level
    if comp_score >= 80.0:
        pred_level = "CRITICAL"
    elif comp_score >= 55.0:
        pred_level = "HIGH"
    elif comp_score >= 25.0:
        pred_level = "MODERATE"
    else:
        pred_level = "LOW"

    # 6. Top Factors
    top_factors = [
        {
            "factor": "6-Hour Forecast Rainfall Total",
            "impact": round(tot_mm, 2),
            "description": f"Predicted 6-hour cumulative precipitation: {tot_mm:.1f} mm (Peak 1h rate: {peak_mm:.1f} mm/h)"
        },
        {
            "factor": "Situational Risk Baseline",
            "impact": round(base_risk, 2),
            "description": f"Layer 1-3 baseline hazard risk score: {base_risk:.1f}/100 ({risk_dict['risk_level']})"
        }
    ]

    return FloodPredictionPayload(
        city_name=city_name,
        district_name=district_name,
        forecast_horizon_hours=6,
        predicted_risk_score=comp_score,
        predicted_risk_level=pred_level,
        forecast_rainfall_total_mm=tot_mm,
        peak_1h_rainfall_mm=peak_mm,
        confidence_level="UNCALIBRATED",
        evidence_quality=ev_qual,
        top_contributing_factors=top_factors,
        model_version="PREDICTIVE_FLOOD_PIPELINE_V1"
    )
