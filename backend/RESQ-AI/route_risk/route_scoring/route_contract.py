"""
Route Scoring & Input Contract Schema for RESQ-AI.

Defines input request schemas, supported route modes, coordinate bounds,
and output response contracts for rescue route evaluation.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


class RouteMode(str, Enum):
    FASTEST = "FASTEST"
    SAFEST = "SAFEST"
    BALANCED = "BALANCED"


@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"Latitude must be between -90.0 and 90.0, got {self.latitude}")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"Longitude must be between -180.0 and 180.0, got {self.longitude}")

    def to_dict(self) -> dict:
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass
class RouteRequest:
    origin: Coordinates
    destination: Coordinates
    mode: RouteMode = RouteMode.BALANCED
    observation_date: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.mode, str):
            self.mode = RouteMode(self.mode.upper())


@dataclass
class RouteCandidate:
    route_id: str
    distance_km: float
    duration_minutes: float
    route_risk_score: float
    risk_level: str
    route_mode_score: float
    selected: bool
    risk_exposure_summary: Dict[str, Any]
    explanation: str
    waypoints: List[List[float]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "distance_km": round(self.distance_km, 2),
            "duration_minutes": round(self.duration_minutes, 2),
            "route_risk_score": round(self.route_risk_score, 2),
            "risk_level": self.risk_level,
            "route_mode_score": round(self.route_mode_score, 4),
            "selected": self.selected,
            "risk_exposure_summary": self.risk_exposure_summary,
            "explanation": self.explanation,
            "waypoints_count": len(self.waypoints)
        }


@dataclass
class RouteResponsePayload:
    origin: Coordinates
    destination: Coordinates
    mode: RouteMode
    selected_route: RouteCandidate
    alternative_routes: List[RouteCandidate]
    route_risk_level: str
    explanation: str
    evidence_quality: str = "HIGH"
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "origin": self.origin.to_dict(),
            "destination": self.destination.to_dict(),
            "mode": self.mode.value if isinstance(self.mode, RouteMode) else str(self.mode),
            "selected_route": self.selected_route.to_dict(),
            "alternative_routes": [r.to_dict() for r in self.alternative_routes],
            "route_risk_level": self.route_risk_level,
            "explanation": self.explanation,
            "evidence_quality": self.evidence_quality,
            "limitations": self.limitations
        }
