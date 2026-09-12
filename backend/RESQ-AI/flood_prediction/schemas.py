"""
6-Hour Predictive Flood Schema Definitions for RESQ-AI.

Defines standardized data contracts for 6-hour predictive flood risk payloads.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FloodPredictionPayload:
    city_name: str
    district_name: str
    forecast_horizon_hours: int
    predicted_risk_score: float
    predicted_risk_level: str
    forecast_rainfall_total_mm: float
    peak_1h_rainfall_mm: float
    confidence_level: str               # "UNCALIBRATED"
    evidence_quality: str               # "HIGH", "MEDIUM", "LOW"
    top_contributing_factors: List[dict] = field(default_factory=list)
    model_version: str = "PREDICTIVE_FLOOD_PIPELINE_V1"

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "district_name": self.district_name,
            "forecast_horizon_hours": self.forecast_horizon_hours,
            "predicted_risk_score": round(self.predicted_risk_score, 2),
            "predicted_risk_level": self.predicted_risk_level,
            "forecast_rainfall_total_mm": round(self.forecast_rainfall_total_mm, 2),
            "peak_1h_rainfall_mm": round(self.peak_1h_rainfall_mm, 2),
            "confidence_level": self.confidence_level,
            "evidence_quality": self.evidence_quality,
            "top_contributing_factors": self.top_contributing_factors,
            "model_version": self.model_version
        }
