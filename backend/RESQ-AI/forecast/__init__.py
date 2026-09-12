"""
6-Hour Forecast Intelligence Package for RESQ-AI.
"""

from forecast.forecast_client import fetch_6hour_forecast, get_mock_6hour_forecast
from forecast.forecast_schema import ForecastPoint, ForecastPayload

__all__ = [
    "fetch_6hour_forecast",
    "get_mock_6hour_forecast",
    "ForecastPoint",
    "ForecastPayload"
]
