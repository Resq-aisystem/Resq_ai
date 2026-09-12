"""
Unit Tests for RESQ-AI Production Risk Inference Engine (Step 6).
"""

import unittest
from pathlib import Path
import yaml
import pandas as pd

from inference.risk_engine import get_district_risk, _load_config
from inference.schemas.risk_contract import RiskPredictionOutput, RiskLevel, EvidenceQuality

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "risk_engine.yaml"


class TestRiskEngine(unittest.TestCase):

    def test_valid_district(self):
        """Test inference for a valid district."""
        result = get_district_risk(district_name="PURI")
        self.assertIsInstance(result, RiskPredictionOutput)
        self.assertEqual(result.district, "PURI")
        self.assertTrue(0.0 <= result.risk_score <= 100.0)

    def test_invalid_district(self):
        """Test inference for an invalid non-existent district."""
        with self.assertRaises(ValueError):
            get_district_risk(district_name="NON_EXISTENT_DISTRICT_XYZ")

    def test_valid_date(self):
        """Test inference with a specific valid date."""
        result = get_district_risk(district_name="PURI", observation_date="2026-09-01")
        self.assertEqual(result.observation_date, "2026-09-01")
        self.assertTrue(0.0 <= result.risk_score <= 100.0)

    def test_unavailable_date_fallback(self):
        """Test fallback behavior when an unavailable date is requested."""
        # Request date outside dataset range
        result = get_district_risk(district_name="PURI", observation_date="1999-01-01")
        self.assertIsNotNone(result.observation_date)
        self.assertTrue(0.0 <= result.risk_score <= 100.0)

    def test_risk_score_range_and_level(self):
        """Test that risk scores are strictly bounded 0-100 and mapped to valid RiskLevel."""
        districts = ["PURI", "WAYANAD", "PATNA", "THANE"]
        for d in districts:
            res = get_district_risk(d)
            self.assertGreaterEqual(res.risk_score, 0.0)
            self.assertLessEqual(res.risk_score, 100.0)
            self.assertIn(res.risk_level, [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL])

    def test_evidence_quality(self):
        """Test evidence quality assessment."""
        res = get_district_risk("PURI")
        self.assertIn(res.evidence_quality, [EvidenceQuality.LOW, EvidenceQuality.MEDIUM, EvidenceQuality.HIGH])

    def test_no_leakage_features(self):
        """Verify that target leakage variables are explicitly excluded from config and prediction."""
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        excluded = cfg.get("excluded_leakage_features", [])
        self.assertIn("ifi_dfsi_score", excluded)
        self.assertIn("ifi_flooded_area_pct", excluded)
        self.assertIn("target_flooded_area_pct", excluded)
        self.assertIn("target_risk_level", excluded)

    def test_top_factors_generation(self):
        """Test that top contributing factors are returned and structured correctly."""
        res = get_district_risk("WAYANAD")
        self.assertGreater(len(res.top_factors), 0)
        for factor in res.top_factors:
            self.assertIsNotNone(factor.factor_name)
            self.assertIsNotNone(factor.description)
            self.assertIn(factor.direction, ["INCREASES_RISK", "DECREASES_RISK"])

    def test_deterministic_output(self):
        """Test that identical inputs produce identical risk assessments."""
        res1 = get_district_risk("PATNA", observation_date="2026-09-05")
        res2 = get_district_risk("PATNA", observation_date="2026-09-05")
        self.assertEqual(res1.risk_score, res2.risk_score)
        self.assertEqual(res1.risk_level, res2.risk_level)

    def test_risk_contract_serialization(self):
        """Test that risk output serializes correctly to JSON-compatible dictionary."""
        res = get_district_risk("PURI")
        res_dict = res.to_dict()
        self.assertIn("district", res_dict)
        self.assertIn("risk_score", res_dict)
        self.assertIn("risk_level", res_dict)
        self.assertIn("evidence_quality", res_dict)
        self.assertIn("top_factors", res_dict)
        self.assertIsInstance(res_dict["top_factors"], list)


if __name__ == "__main__":
    unittest.main()
