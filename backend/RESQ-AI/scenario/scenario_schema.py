"""
What-If Scenario Planning Schema Definitions for RESQ-AI.

Defines schemas for scenario parameters, risk deltas, and comparison payloads.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ScenarioConfig:
    scenario_id: str
    scenario_name: str
    rainfall_multiplier: float = 1.0
    infrastructure_failure: bool = False
    road_closure_ids: List[str] = field(default_factory=list)


@dataclass
class ScenarioResultPayload:
    city_name: str
    district_name: str
    scenario_id: str
    scenario_name: str
    baseline_risk_score: float
    scenario_risk_score: float
    risk_delta: float
    baseline_priority_level: str
    scenario_priority_level: str
    affected_facilities_count: int
    new_p1_facilities: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    output_type: str = "WHAT_IF_SCENARIO"

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "district_name": self.district_name,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "baseline_risk_score": round(self.baseline_risk_score, 2),
            "scenario_risk_score": round(self.scenario_risk_score, 2),
            "risk_delta": round(self.risk_delta, 2),
            "baseline_priority_level": self.baseline_priority_level,
            "scenario_priority_level": self.scenario_priority_level,
            "affected_facilities_count": self.affected_facilities_count,
            "new_p1_facilities": self.new_p1_facilities,
            "reasons": self.reasons,
            "output_type": self.output_type
        }
