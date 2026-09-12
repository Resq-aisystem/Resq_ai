"""
Grounded Context Builder for RESQ-AI Emergency Action Plan Engine.

Assembles verified evidence from Risk Engine, Priority Engine, and Route Risk Engine.
Strictly excludes missing value fabrication or unverified estimates.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from inference.risk_engine import get_district_risk
from priority.emergency_priority.engine import get_emergency_priority
from route_risk.route_scoring.route_service import get_rescue_route


@dataclass
class GroundedContext:
    district: str
    observation_date: str
    risk_score: float
    risk_level: str
    priority_score: float
    priority_level: str
    evidence_quality: str
    vulnerability_flags: list
    priority_factors: list
    risk_layer_breakdown: dict
    route_info: Optional[dict] = None
    limitations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "district": self.district,
            "observation_date": self.observation_date,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "priority_score": self.priority_score,
            "priority_level": self.priority_level,
            "evidence_quality": self.evidence_quality,
            "vulnerability_flags": self.vulnerability_flags,
            "priority_factors": self.priority_factors,
            "risk_layer_breakdown": self.risk_layer_breakdown,
            "route_info": self.route_info if self.route_info else "NOT_AVAILABLE",
            "limitations": self.limitations
        }


def build_grounded_context(
    district_name: str,
    observation_date: str = None,
    route_mode: str = "BALANCED",
    origin_coords: tuple = None,
    dest_coords: tuple = None
) -> GroundedContext:
    """
    Build verified grounded context from deterministic engine outputs.

    Args:
        district_name: Name of target district.
        observation_date: ISO date string 'YYYY-MM-DD'.
        route_mode: Operational route mode ("FASTEST", "SAFEST", "BALANCED").
        origin_coords: Optional tuple (lat, lon) for origin.
        dest_coords: Optional tuple (lat, lon) for destination.

    Returns:
        GroundedContext dataclass containing verified evidence.
    """
    # 1. Retrieve Risk Engine Output
    risk_output = get_district_risk(district_name, observation_date)
    risk_dict = risk_output.to_dict()

    actual_district = risk_dict["district"]
    actual_date = risk_dict["observation_date"]
    risk_score = risk_dict["risk_score"]
    risk_lvl = risk_dict["risk_level"]

    # 2. Retrieve Priority Engine Output
    priority_dict = get_emergency_priority(actual_district, actual_date)
    priority_score = priority_dict["priority_score"]
    priority_lvl = priority_dict["priority_level"]
    ev_qual = priority_dict["evidence_quality"]
    v_flags = priority_dict["vulnerability_flags"]
    p_factors = priority_dict["priority_factors"]

    # 3. Retrieve Route Risk Output (if coordinates provided or default demo corridor)
    route_info = None
    if origin_coords and dest_coords:
        try:
            r_res = get_rescue_route(
                origin_lat=origin_coords[0],
                origin_lon=origin_coords[1],
                destination_lat=dest_coords[0],
                destination_lon=dest_coords[1],
                mode=route_mode,
                observation_date=actual_date
            )
            route_info = {
                "mode": r_res["mode"],
                "selected_route_id": r_res["selected_route"]["route_id"],
                "distance_km": r_res["selected_route"]["distance_km"],
                "duration_minutes": r_res["selected_route"]["duration_minutes"],
                "route_risk_score": r_res["selected_route"]["route_risk_score"],
                "risk_level": r_res["route_risk_level"],
                "explanation": r_res["explanation"]
            }
        except Exception:
            route_info = None

    limitations = [
        "Intelligence is based on observed rainfall, terrain susceptibility, hydrology, and historical disaster priors.",
        "The LLM does not generate the underlying numerical risk, priority, or routing scores.",
        "Decision-support outputs require review by authorized emergency management personnel."
    ]

    return GroundedContext(
        district=actual_district,
        observation_date=actual_date,
        risk_score=risk_score,
        risk_level=risk_lvl,
        priority_score=priority_score,
        priority_level=priority_lvl,
        evidence_quality=ev_qual,
        vulnerability_flags=v_flags,
        priority_factors=p_factors,
        risk_layer_breakdown=risk_dict.get("layer_breakdown", {}),
        route_info=route_info,
        limitations=limitations
    )
