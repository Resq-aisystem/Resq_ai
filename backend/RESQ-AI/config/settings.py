"""
Global Project Settings and Environment Configuration for RESQ-AI.
"""

from pathlib import Path
import os
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)
except ImportError:
    pass

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

FEATURE_STORE_DIR = BASE_DIR / "datasets" / "master"
MODEL_ARTIFACTS_DIR = BASE_DIR / "models" / "artifacts"
EVALUATION_DIR = BASE_DIR / "evaluation"

# Risk Threshold Constants (Schema Defaults)
RISK_LEVEL_THRESHOLDS = {
    "LOW": (0.0, 25.0),
    "MODERATE": (25.0, 55.0),
    "HIGH": (55.0, 80.0),
    "CRITICAL": (80.0, 100.0)
}
