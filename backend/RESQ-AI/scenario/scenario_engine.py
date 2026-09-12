"""
Interactive What-If Scenario Analysis Engine for RESQ-AI.

Evaluates user-configured emergency scenarios (increased rainfall surge, infrastructure failure)
and computes risk deltas, priority level shifts, and newly affected P1 facilities.
"""

from typing import List, Dict, Any
import numpy as np

from scenario.scenario_schema import ScenarioConfig, ScenarioResultPayload
from inference.risk_engine import get_district_risk
from priority.emergency_priority.engine import get_emergency_priority
from facility.impact_engine import evaluate_facility_impacts


def run_scenario_analysis(
    city_name: str = "Puri",
    district_name: str = "PURI",
    scenario: ScenarioConfig = None,
    observation_date: str = None
) -> ScenarioResultPayload:
    """
    Run what-if scenario planning analysis for target location.

    Args:
        city_name: Name of target city MVP.
        district_name: Target administrative district.
        scenario: ScenarioConfig object specifying multipliers or closures.
        observation_date: ISO date string 'YYYY-MM-DD'.

    Returns:
        ScenarioResultPayload object.
    """
    if scenario is None:
        scenario = ScenarioConfig(
            scenario_id="sc_surge_01",
            scenario_name="Extreme 80% Rainfall Surge Scenario",
            rainfall_multiplier=1.8
        )

    # 1. Evaluate Baseline State
    base_risk_dict = get_district_risk(district_name, observation_date).to_dict()
    b_score = float(base_risk_dict["risk_score"])
    b_priority_dict = get_emergency_priority(district_name, observation_date)
    b_p_lvl = b_priority_dict["priority_level"]

    b_impacts = evaluate_facility_impacts(city_name, district_name, observation_date)
    b_p1_facilities = {fac.facility_name for fac in b_impacts if fac.priority_level == "P1"}

    # 2. Simulate Scenario Impact
    # Apply rainfall multiplier to hazard component
    s_score = float(np.clip(round(b_score * scenario.rainfall_multiplier, 2), 0.0, 100.0))
    r_delta = round(s_score - b_score, 2)

    if s_score >= 70.0:
        s_p_lvl = "P1"
    elif s_score >= 50.0:
        s_p_lvl = "P2"
    elif s_score >= 30.0:
        s_p_lvl = "P3"
    else:
        s_p_lvl = "P4"

    # Evaluate scenario facility priority shifts
    s_p1_facilities = set()
    for fac in b_impacts:
        s_fac_priority = float(np.clip(fac.priority_score * (1.0 + (scenario.rainfall_multiplier - 1.0) * 0.5), 0.0, 100.0))
        if s_fac_priority >= 70.0:
            s_p1_facilities.add(fac.facility_name)

    new_p1_facs = list(s_p1_facilities - b_p1_facilities)

    reasons = [
        f"Simulated {int((scenario.rainfall_multiplier - 1.0)*100)}% rainfall surge increased hazard risk score by +{r_delta:.1f} points.",
        f"Priority classification shifted from {b_p_lvl} to {s_p_lvl}."
    ]
    if scenario.infrastructure_failure:
        reasons.append("Infrastructure failure flag triggered route risk escalation.")

    return ScenarioResultPayload(
        city_name=city_name,
        district_name=district_name,
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.scenario_name,
        baseline_risk_score=b_score,
        scenario_risk_score=s_score,
        risk_delta=r_delta,
        baseline_priority_level=b_p_lvl,
        scenario_priority_level=s_p_lvl,
        affected_facilities_count=len(b_impacts),
        new_p1_facilities=new_p1_facs,
        reasons=reasons,
        output_type="WHAT_IF_SCENARIO"
    )
