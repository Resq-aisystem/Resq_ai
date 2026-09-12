"""
Architecture Verification Tests for RESQ-AI.

Ensures directory tree integrity, module importability, and schema output contract consistency
without requiring any real or synthetic dataset files.
"""

from pathlib import Path
import unittest
from inference.schemas.risk_contract import RiskPredictionOutput, RiskLevel, RiskFactor


class TestRESQAIArchitecture(unittest.TestCase):

    def test_directory_structure_exists(self):
        """Verify that all core project directories exist in expected locations."""
        base_dir = Path(__file__).resolve().parent.parent

        required_dirs = [
            "data/raw/imd",
            "data/raw/gfsm",
            "data/raw/camels_ind",
            "data/raw/ifi",
            "data/raw/gdis",
            "data/interim",
            "data/processed",
            "preprocessing/imd",
            "preprocessing/gfsm",
            "preprocessing/camels_ind",
            "preprocessing/ifi",
            "preprocessing/gdis",
            "features/rainfall",
            "features/susceptibility",
            "features/hydrology",
            "features/flood_history",
            "features/disaster_history",
            "features/master",
            "datasets/master",
            "models/flood_risk",
            "models/susceptibility",
            "models/artifacts",
            "training/scripts",
            "training/configs",
            "training/experiments",
            "evaluation/metrics",
            "evaluation/reports",
            "evaluation/plots",
            "explainability/feature_importance",
            "explainability/shap",
            "inference/schemas",
            "inference/preprocessing",
            "inference/prediction",
            "priority/exposure",
            "priority/emergency_priority",
            "route_risk/road_risk",
            "route_scoring",
            "route_modes",
            "action_plan",
            "notebooks",
            "reports",
            "config"
        ]

        # Route risk subdirectories check
        route_risk_dirs = [
            "route_risk/road_risk",
            "route_risk/route_scoring",
            "route_risk/route_modes"
        ]

        for rel_path in required_dirs:
            if rel_path in ["route_scoring", "route_modes"]:
                rel_path = f"route_risk/{rel_path}"
            dir_path = base_dir / rel_path
            self.assertTrue(dir_path.exists(), f"Missing required directory: {rel_path}")
            self.assertTrue(dir_path.is_dir(), f"Path is not a directory: {rel_path}")

    def test_schema_contract_instantiation(self):
        """Verify that RiskPredictionOutput schema contract validates correctly."""
        sample_output = RiskPredictionOutput(
            risk_score=75.5,
            risk_level=RiskLevel.HIGH,
            confidence=0.92,
            top_factors=[
                RiskFactor(
                    factor_name="Extreme 24h Rainfall",
                    impact_weight=0.65,
                    description="High intensity rainfall recorded in IMD district dataset"
                )
            ],
            priority_score=85.0
        )

        self.assertEqual(sample_output.risk_score, 75.5)
        self.assertEqual(sample_output.risk_level, RiskLevel.HIGH)
        self.assertEqual(sample_output.confidence, 0.92)
        self.assertEqual(len(sample_output.top_factors), 1)
        self.assertEqual(sample_output.priority_score, 85.0)

    def test_schema_contract_boundary_validation(self):
        """Verify schema boundary validation rules (e.g. risk score range 0-100)."""
        with self.assertRaises(ValueError):
            # Risk score > 100 should raise ValidationError
            RiskPredictionOutput(
                risk_score=150.0,
                risk_level=RiskLevel.CRITICAL,
                confidence=0.8,
                top_factors=[],
                priority_score=50.0
            )


if __name__ == "__main__":
    unittest.main()

