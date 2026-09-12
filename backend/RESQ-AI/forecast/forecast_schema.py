"""
6-Hour Forecast Schema Definitions for RESQ-AI.

Defines standardized data contracts for 6-hour predictive weather forecast ingestion.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ForecastPoint:
    forecast_hour: int              # 1 to 6
    start_timestamp: str
    end_timestamp: str
    rainfall_mm: float
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    pressure_hpa: Optional[float] = None

    def __post_init__(self):
        if not (1 <= self.forecast_hour <= 6):
            raise ValueError(f"forecast_hour must be between 1 and 6, got {self.forecast_hour}")
        if self.rainfall_mm < 0.0:
            raise ValueError(f"rainfall_mm cannot be negative, got {self.rainfall_mm}")

    def to_dict(self) -> dict:
        return {
            "forecast_hour": self.forecast_hour,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "rainfall_mm": round(self.rainfall_mm, 2),
            "temperature_c": round(self.temperature_c, 1) if self.temperature_c is not None else None,
            "humidity_pct": round(self.humidity_pct, 1) if self.humidity_pct is not None else None,
            "wind_speed_kmh": round(self.wind_speed_kmh, 1) if self.wind_speed_kmh is not None else None,
            "pressure_hpa": round(self.pressure_hpa, 1) if self.pressure_hpa is not None else None
        }


@dataclass
class ForecastPayload:
    city_name: str
    district_name: str
    retrieved_at: str
    source_provider: str
    forecast_horizon_hours: int = 6
    hourly_points: List[ForecastPoint] = field(default_factory=list)
    is_mock: bool = False

    def total_6h_rainfall_mm(self) -> float:
        return round(sum(p.rainfall_mm for p in self.hourly_points), 2)

    def peak_1h_rainfall_mm(self) -> float:
        if not self.hourly_points:
            return 0.0
        return round(max(p.rainfall_mm for p in self.hourly_points), 2)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "district_name": self.district_name,
            "retrieved_at": self.retrieved_at,
            "source_provider": self.source_provider,
            "forecast_horizon_hours": self.forecast_horizon_hours,
            "total_6h_rainfall_mm": self.total_6h_rainfall_mm(),
            "peak_1h_rainfall_mm": self.peak_1h_rainfall_mm(),
            "hourly_points": [p.to_dict() for p in self.hourly_points],
            "is_mock": self.is_mock
        }
