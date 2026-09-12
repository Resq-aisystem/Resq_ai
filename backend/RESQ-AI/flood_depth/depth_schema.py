"""
Flood Depth Estimation Schema Definitions for RESQ-AI.

Defines data contracts for flood depth estimation and status reporting.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DepthEstimatePayload:
    city_name: str
    district_name: str
    predicted_depth_meters: Optional[float]
    depth_category: str                  # "NO_FLOODING", "SHALLOW", "MODERATE", "DEEP", "INSUFFICIENT_DATA"
    data_status: str                    # "INSUFFICIENT_DATA" or "ESTIMATED"
    source_model: str
    explanation: str

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "district_name": self.district_name,
            "predicted_depth_meters": round(self.predicted_depth_meters, 2) if self.predicted_depth_meters is not None else None,
            "depth_category": self.depth_category,
            "data_status": self.data_status,
            "source_model": self.source_model,
            "explanation": self.explanation
        }
