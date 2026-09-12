"""
Emergency Action Plan Schema Contract for RESQ-AI.

Defines strict structured output contract for grounded emergency action plans.
Validates numerical bounds, categorical levels, and required fields.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ActionPlanContract:
    district: str
    observation_date: str
    risk: Dict[str, Any]             # {"score": float, "level": str}
    priority: Dict[str, Any]         # {"score": float, "level": str}
    situation_summary: str
    key_evidence: List[str]
    recommended_actions: List[str]
    route_recommendation: Dict[str, Any]  # {"mode": str, "risk_score": float, "explanation": str}
    monitoring_actions: List[str]
    limitations: List[str]
    evidence_quality: str = "HIGH"
    is_fallback: bool = False

    def __post_init__(self):
        # Validate risk dictionary
        r_score = float(self.risk.get("score", -1.0))
        r_level = str(self.risk.get("level", "")).upper()
        if not (0.0 <= r_score <= 100.0):
            raise ValueError(f"risk score must be between 0.0 and 100.0, got {r_score}")
        if r_level not in ["LOW", "MODERATE", "HIGH", "CRITICAL"]:
            raise ValueError(f"Invalid risk level: {r_level}")

        # Validate priority dictionary
        p_score = float(self.priority.get("score", -1.0))
        p_level = str(self.priority.get("level", "")).upper()
        if not (0.0 <= p_score <= 100.0):
            raise ValueError(f"priority score must be between 0.0 and 100.0, got {p_score}")
        if p_level not in ["P1", "P2", "P3", "P4"]:
            raise ValueError(f"Invalid priority level: {p_level}")

        # Validate route recommendation
        rm_mode = str(self.route_recommendation.get("mode", "")).upper()
        if rm_mode not in ["FASTEST", "SAFEST", "BALANCED", "NOT_AVAILABLE"]:
            raise ValueError(f"Invalid route mode: {rm_mode}")

    def to_dict(self) -> dict:
        return {
            "district": self.district,
            "observation_date": self.observation_date,
            "risk": {
                "score": round(float(self.risk["score"]), 2),
                "level": str(self.risk["level"]).upper()
            },
            "priority": {
                "score": round(float(self.priority["score"]), 2),
                "level": str(self.priority["level"]).upper()
            },
            "situation_summary": self.situation_summary,
            "key_evidence": self.key_evidence,
            "recommended_actions": self.recommended_actions,
            "route_recommendation": {
                "mode": str(self.route_recommendation.get("mode", "BALANCED")).upper(),
                "risk_score": round(float(self.route_recommendation.get("risk_score", 0.0)), 2),
                "explanation": str(self.route_recommendation.get("explanation", ""))
            },
            "monitoring_actions": self.monitoring_actions,
            "limitations": self.limitations,
            "evidence_quality": self.evidence_quality,
            "is_fallback": self.is_fallback
        }
