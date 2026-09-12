"""
PRD Facility Evacuation Priority Sub-Engine for RESQ-AI.

Extends emergency priority capabilities with facility-level priority scoring (PRD_FACILITY_PRIORITY_V1).
Preserves 100% backward compatibility with district-level emergency priority engine.
"""

from typing import List, Dict, Any
from facility.impact_engine import evaluate_facility_impacts, FacilityImpactPayload


def get_facility_evacuation_priorities(
    city_name: str = "Puri",
    district_name: str = "PURI",
    observation_date: str = None
) -> List[Dict[str, Any]]:
    """
    Get ranked facility evacuation priorities for single-city MVP.

    Returns:
        List of serialized facility priority dictionary payloads sorted descending by priority_score.
    """
    impacts = evaluate_facility_impacts(city_name, district_name, observation_date)
    return [imp.to_dict() for imp in impacts]
