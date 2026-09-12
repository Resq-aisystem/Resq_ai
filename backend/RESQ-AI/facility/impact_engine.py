"""
Facility Impact & Vulnerability Assessment Engine for RESQ-AI.

Calculates facility-level exposure, vulnerability, and operational priority scores.
"""

from typing import List, Dict, Any
import numpy as np

from facility.facility_schema import FacilityRecord, FacilityImpactPayload
from facility.facility_loader import load_city_facilities
from flood_zones.spatial_intersection import generate_city_flood_zones, check_point_in_flood_zone
from inference.risk_engine import get_district_risk


def evaluate_facility_impacts(
    city_name: str = "Puri",
    district_name: str = "PURI",
    observation_date: str = None
) -> List[FacilityImpactPayload]:
    """
    Evaluate facility exposure, vulnerability, and priority for all facilities in target city.

    Args:
        city_name: Name of target city.
        district_name: Target administrative district.
        observation_date: ISO date string 'YYYY-MM-DD'.

    Returns:
        List of FacilityImpactPayload objects.
    """
    facilities = load_city_facilities(city_name, district_name)
    zones_payload = generate_city_flood_zones(city_name, district_name)

    risk_output = get_district_risk(district_name, observation_date)
    base_risk = float(risk_output.to_dict()["risk_score"])

    impact_results = []

    for fac in facilities:
        is_in_fz, fz_risk_lvl = check_point_in_flood_zone(fac.latitude, fac.longitude, zones_payload)

        # Vulnerability Score
        v_score = 20.0
        reasons = []

        if fac.facility_type == "HOSPITAL":
            v_score += 30.0
            reasons.append("High vulnerability healthcare facility containing in-patients.")
            if fac.critical_patients_count and fac.critical_patients_count > 0:
                v_score += 20.0
                reasons.append(f"Contains {fac.critical_patients_count} critical ICU/life-support patients.")

        if is_in_fz:
            v_score += 25.0
            reasons.append("Facility located inside high-risk flood zone polygon.")

        v_score = float(np.clip(v_score, 0.0, 100.0))

        # Facility Priority Score (PRD_FACILITY_PRIORITY_V1 formula)
        # Priority = 40% Base District Risk + 35% Vulnerability + 25% Flood Zone Exposure
        fz_exposure_val = 100.0 if is_in_fz else 20.0
        priority_score = float(np.clip(round(0.40 * base_risk + 0.35 * v_score + 0.25 * fz_exposure_val, 2), 0.0, 100.0))

        if priority_score >= 70.0:
            p_lvl = "P1"
        elif priority_score >= 50.0:
            p_lvl = "P2"
        elif priority_score >= 30.0:
            p_lvl = "P3"
        else:
            p_lvl = "P4"

        impact_lvl = "CRITICAL" if is_in_fz and base_risk >= 55.0 else ("HIGH" if is_in_fz else "MODERATE")

        top_factors = [
            f"Facility Category: {fac.facility_type}",
            f"Flood Zone Exposure: {'INSIDE FLOOD ZONE' if is_in_fz else 'OUTSIDE FLOOD ZONE'}",
            f"Vulnerability Score: {v_score:.1f}/100"
        ]

        impact_results.append(FacilityImpactPayload(
            facility_id=fac.facility_id,
            facility_name=fac.facility_name,
            facility_type=fac.facility_type,
            risk_score=base_risk,
            impact_level=impact_lvl,
            vulnerability_score=v_score,
            priority_score=priority_score,
            priority_level=p_lvl,
            is_in_flood_zone=is_in_fz,
            top_factors=top_factors,
            reasons=reasons
        ))

    # Sort descending by priority_score
    impact_results.sort(key=lambda x: x.priority_score, reverse=True)
    return impact_results
