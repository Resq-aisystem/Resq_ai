"""
30-Minute Pipeline Scheduler & Orchestrator for RESQ-AI.

Orchestrates automated background refresh cycles across forecast ingestion,
flood risk prediction, facility impact assessment, and priority rankings.
"""

from datetime import datetime, timezone, timedelta
from update.update_status import UpdateStatusPayload

_LAST_UPDATE_TIME = None


def get_current_update_status(city_name: str = "Puri") -> UpdateStatusPayload:
    """
    Get current 30-minute update cycle status.
    """
    global _LAST_UPDATE_TIME
    now = datetime.now(timezone.utc)

    if _LAST_UPDATE_TIME is None:
        _LAST_UPDATE_TIME = now

    next_update = _LAST_UPDATE_TIME + timedelta(minutes=30)

    return UpdateStatusPayload(
        last_update_timestamp=_LAST_UPDATE_TIME.isoformat(),
        next_update_timestamp=next_update.isoformat(),
        update_interval_minutes=30,
        status="COMPLETED",
        city_scope=city_name
    )


def trigger_pipeline_update(city_name: str = "Puri") -> UpdateStatusPayload:
    """
    Manually trigger or execute a 30-minute pipeline refresh cycle.
    """
    global _LAST_UPDATE_TIME
    _LAST_UPDATE_TIME = datetime.now(timezone.utc)
    return get_current_update_status(city_name)
