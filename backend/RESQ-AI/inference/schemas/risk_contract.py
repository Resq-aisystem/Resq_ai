"""
Risk Output Contract Schema Definition for RESQ-AI.

Defines the structured output contract for inference predictions to be consumed by downstream system APIs.
Supports standard Python dataclasses for zero-dependency portability and Pydantic if available.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceQuality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class RiskFactor:
    factor_name: str
    impact_weight: float
    description: str
    direction: str = "INCREASES_RISK"

    def to_dict(self) -> dict:
        return {
            "factor": self.factor_name,
            "factor_name": self.factor_name,
            "impact_weight": self.impact_weight,
            "direction": self.direction,
            "description": self.description,
            "evidence": self.description
        }


@dataclass
class RiskPredictionOutput:
    """
    Standardized inference risk contract for backend/API integration.
    """
    risk_score: float
    risk_level: RiskLevel
    confidence: float = 0.85
    top_factors: List[RiskFactor] = field(default_factory=list)
    priority_score: float = 0.0
    evidence_quality: EvidenceQuality = EvidenceQuality.MEDIUM
    district: str = ""
    observation_date: str = ""
    layer_breakdown: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not (0.0 <= self.risk_score <= 100.0):
            raise ValueError(f"risk_score must be between 0.0 and 100.0, got {self.risk_score}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not (0.0 <= self.priority_score <= 100.0):
            raise ValueError(f"priority_score must be between 0.0 and 100.0, got {self.priority_score}")

    def to_dict(self) -> dict:
        """Serialize output to dictionary matching API contract."""
        risk_lvl_val = self.risk_level.value if isinstance(self.risk_level, RiskLevel) else str(self.risk_level)
        ev_qual_val = self.evidence_quality.value if isinstance(self.evidence_quality, EvidenceQuality) else str(self.evidence_quality)

        factors_serialized = []
        for f in self.top_factors:
            if isinstance(f, RiskFactor):
                factors_serialized.append(f.to_dict())
            elif isinstance(f, dict):
                factors_serialized.append(f)

        return {
            "district": self.district,
            "observation_date": self.observation_date,
            "risk_score": round(self.risk_score, 2),
            "risk_level": risk_lvl_val,
            "evidence_quality": ev_qual_val,
            "confidence": round(self.confidence, 4),
            "top_factors": factors_serialized,
            "priority_score": round(self.priority_score, 2),
            "layer_breakdown": self.layer_breakdown
        }
