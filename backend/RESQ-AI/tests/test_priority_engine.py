"""
Unit Tests for RESQ-AI Emergency Priority Engine (Step 7).
"""

import unittest
from pathlib import Path
import yaml
import pandas as pd

from priority.emergency_priority.engine import get_emergency_priority
from priority.run_priority_scoring import run_batch_priority_scoring

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "priority_engine.yaml"
PRIORITY_DIR = BASE_DIR / "data" / "processed" / "priority"


class TestPriorityEngine(unittest.TestCase):

    def test_valid_district(self):
        """Test emergency priority scoring for a valid district."""
        res = get_emergency_priority(district_name="PURI")
        self.assertIsInstance(res, dict)
        self.assertEqual(res["district"], "PURI")
        self.assertTrue(0.0 <= res["priority_score"] <= 100.0)
        self.assertIn(res["priority_level"], ["P1", "P2", "P3", "P4"])

    def test_invalid_district(self):
        """Test emergency priority scoring for an invalid district."""
        with self.assertRaises(ValueError):
            get_emergency_priority(district_name="NON_EXISTENT_DISTRICT_XYZ")

    def test_valid_date(self):
        """Test emergency priority scoring with a valid date."""
        res = get_emergency_priority(district_name="PURI", observation_date="2026-09-01")
        self.assertEqual(res["observation_date"], "2026-09-01")
        self.assertTrue(0.0 <= res["priority_score"] <= 100.0)

    def test_unavailable_date_fallback(self):
        """Test date fallback handling when date is unavailable."""
        res = get_emergency_priority(district_name="PURI", observation_date="1999-01-01")
        self.assertIsNotNone(res["observation_date"])
        self.assertTrue(0.0 <= res["priority_score"] <= 100.0)

    def test_priority_score_range_and_levels(self):
        """Test score bounds [0, 100] and level mappings across multiple districts."""
        test_districts = ["ALIPURDUAR", "PURI", "WAYANAD", "PATNA"]
        for d in test_districts:
            res = get_emergency_priority(d)
            self.assertGreaterEqual(res["priority_score"], 0.0)
            self.assertLessEqual(res["priority_score"], 100.0)
            self.assertIn(res["priority_level"], ["P1", "P2", "P3", "P4"])

    def test_deterministic_output(self):
        """Test that identical inputs produce identical priority scores."""
        res1 = get_emergency_priority("PATNA", observation_date="2026-09-05")
        res2 = get_emergency_priority("PATNA", observation_date="2026-09-05")
        self.assertEqual(res1["priority_score"], res2["priority_score"])
        self.assertEqual(res1["priority_level"], res2["priority_level"])

    def test_leakage_features_excluded(self):
        """Test that target leakage variables are excluded from priority configuration."""
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        excluded = cfg.get("excluded_leakage_features", [])
        self.assertIn("ifi_dfsi_score", excluded)
        self.assertIn("ifi_flooded_area_pct", excluded)
        self.assertIn("target_flooded_area_pct", excluded)
        self.assertIn("target_risk_level", excluded)

    def test_vulnerability_flags_validity(self):
        """Test that vulnerability flags only use valid supported flag names."""
        valid_flag_names = {
            "HIGH_CURRENT_RISK",
            "HIGH_FLOOD_SUSCEPTIBILITY",
            "HIGH_HISTORICAL_FLOOD_RECURRENCE",
            "HIGH_HYDROLOGICAL_VULNERABILITY",
            "MULTI_HAZARD_HISTORY"
        }
        res = get_emergency_priority("ALIPURDUAR")
        for flag in res["vulnerability_flags"]:
            self.assertIn(flag, valid_flag_names)

        # Ensure fake flags like HOSPITAL_AT_RISK are not present
        self.assertNotIn("HOSPITAL_AT_RISK", res["vulnerability_flags"])
        self.assertNotIn("ELDERLY_POPULATION_HIGH", res["vulnerability_flags"])

    def test_evidence_based_explanation(self):
        """Test that generated factors and attention reasons are evidence-based."""
        res = get_emergency_priority("WAYANAD")
        self.assertGreater(len(res["priority_factors"]), 0)
        self.assertIsNotNone(res["recommended_attention_reason"])
        self.assertIn("WAYANAD", res["recommended_attention_reason"])

    def test_batch_ranking_and_output_files(self):
        """Test batch ranking sorting and file generation."""
        results = run_batch_priority_scoring()
        self.assertGreater(len(results), 0)

        # Verify descending order of priority scores
        scores = [r["priority_score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

        # Check file outputs
        json_path = PRIORITY_DIR / "emergency_priority_results.json"
        csv_path = PRIORITY_DIR / "emergency_priority_results.csv"
        ranking_path = PRIORITY_DIR / "emergency_priority_ranking.csv"

        self.assertTrue(json_path.exists())
        self.assertTrue(csv_path.exists())
        self.assertTrue(ranking_path.exists())


if __name__ == "__main__":
    unittest.main()
