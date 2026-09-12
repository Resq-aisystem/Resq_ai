"""
6-Hour Flood Prediction Intelligence Package for RESQ-AI.
"""

from flood_prediction.predictor import predict_6hour_flood_risk
from flood_prediction.schemas import FloodPredictionPayload

__all__ = [
    "predict_6hour_flood_risk",
    "FloodPredictionPayload"
]
