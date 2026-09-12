"""
Flood Zone Polygon Schema Definitions for RESQ-AI.

Defines spatial polygon structures and resolution metadata for 100m target flood zone mapping.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FloodZonePolygon:
    zone_id: str
    risk_level: str                       # "LOW", "MODERATE", "HIGH", "CRITICAL"
    bounding_box: List[float]             # [min_lat, min_lon, max_lat, max_lon]
    coordinates: List[List[float]]        # Polygon boundary coordinate list [[lat, lon], ...]
    area_sq_km: float

    def to_dict(self) -> dict:
        return {
            "zone_id": self.zone_id,
            "risk_level": self.risk_level,
            "bounding_box": self.bounding_box,
            "coordinates": self.coordinates,
            "area_sq_km": round(self.area_sq_km, 3)
        }


@dataclass
class FloodZonePayload:
    city_name: str
    district_name: str
    target_resolution_m: int = 100
    source_resolution_m: int = 1000
    resampling_method: str = "Bilinear Interpolation"
    zones: List[FloodZonePolygon] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "district_name": self.district_name,
            "target_resolution_m": self.target_resolution_m,
            "source_resolution_m": self.source_resolution_m,
            "resampling_method": self.resampling_method,
            "zone_count": len(self.zones),
            "zones": [z.to_dict() for z in self.zones]
        }
