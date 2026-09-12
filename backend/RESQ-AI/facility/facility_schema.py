"""
Facility Impact & Vulnerability Schema Definitions for RESQ-AI.

Defines standardized schemas for facility records, vulnerable populations,
and facility-level impact payloads.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FacilityRecord:
    facility_id: str
    facility_name: str
    facility_type: str                   # "HOSPITAL", "EMERGENCY_CENTER", "SHELTER", "SCHOOL"
    latitude: float
    longitude: float
    capacity: int = 100
    elderly_count: Optional[int] = None
    mobility_impaired_count: Optional[int] = None
    patient_count: Optional[int] = None
    critical_patients_count: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "facility_id": self.facility_id,
            "facility_name": self.facility_name,
            "facility_type": self.facility_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacity": self.capacity,
            "elderly_count": self.elderly_count if self.elderly_count is not None else "DATA_UNAVAILABLE",
            "mobility_impaired_count": self.mobility_impaired_count if self.mobility_impaired_count is not None else "DATA_UNAVAILABLE",
            "patient_count": self.patient_count if self.patient_count is not None else "DATA_UNAVAILABLE",
            "critical_patients_count": self.critical_patients_count if self.critical_patients_count is not None else "DATA_UNAVAILABLE"
        }


@dataclass
class FacilityImpactPayload:
    facility_id: str
    facility_name: str
    facility_type: str
    risk_score: float
    impact_level: str
    vulnerability_score: float
    priority_score: float
    priority_level: str
    is_in_flood_zone: bool
    top_factors: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "facility_id": self.facility_id,
            "facility_name": self.facility_name,
            "facility_type": self.facility_type,
            "risk_score": round(self.risk_score, 2),
            "impact_level": self.impact_level,
            "vulnerability_score": round(self.vulnerability_score, 2),
            "priority_score": round(self.priority_score, 2),
            "priority_level": self.priority_level,
            "is_in_flood_zone": self.is_in_flood_zone,
            "top_factors": self.top_factors,
            "reasons": self.reasons
        }
