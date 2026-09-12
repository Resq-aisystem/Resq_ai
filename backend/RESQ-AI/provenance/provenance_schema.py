"""
Provenance & Lineage Schema Definitions for RESQ-AI.

Defines standardized data contracts for model, dataset, and calculation provenance tracking.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ProvenanceRecord:
    source_dataset: str
    dataset_version: str
    model_version: str
    feature_version: str
    source_timestamp: str
    calculation_timestamp: str

    def to_dict(self) -> dict:
        return {
            "source_dataset": self.source_dataset,
            "dataset_version": self.dataset_version,
            "model_version": self.model_version,
            "feature_version": self.feature_version,
            "source_timestamp": self.source_timestamp,
            "calculation_timestamp": self.calculation_timestamp
        }


def create_provenance_record(
    source_dataset: str = "IMD_GFSM_CAMELS_IFI_GDIS",
    model_version: str = "RandomForest_v1_RiskEngine_v1",
    feature_version: str = "RESQ_AI_FEATURES_V1"
) -> ProvenanceRecord:
    """
    Create a standardized provenance tracking record.
    """
    now_str = datetime.now(timezone.utc).isoformat()
    return ProvenanceRecord(
        source_dataset=source_dataset,
        dataset_version="2026.09.11",
        model_version=model_version,
        feature_version=feature_version,
        source_timestamp="2026-09-11T00:00:00Z",
        calculation_timestamp=now_str
    )
