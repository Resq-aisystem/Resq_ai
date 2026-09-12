"""
30-Minute Real-Time Update Status Schema for RESQ-AI.

Defines standardized data contracts for update interval tracking and pipeline status.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class UpdateStatusPayload:
    last_update_timestamp: str
    next_update_timestamp: str
    update_interval_minutes: int = 30
    status: str = "IDLE"                  # "IDLE", "RUNNING", "COMPLETED", "FAILED"
    city_scope: str = "Puri"
    components_refreshed: list = None

    def __post_init__(self):
        if self.components_refreshed is None:
            self.components_refreshed = [
                "forecast_ingestion",
                "flood_prediction",
                "facility_impact",
                "priority_ranking",
                "route_analysis",
                "action_plan_context"
            ]

    def to_dict(self) -> dict:
        return {
            "last_update_timestamp": self.last_update_timestamp,
            "next_update_timestamp": self.next_update_timestamp,
            "update_interval_minutes": self.update_interval_minutes,
            "status": self.status,
            "city_scope": self.city_scope,
            "components_refreshed": self.components_refreshed
        }
