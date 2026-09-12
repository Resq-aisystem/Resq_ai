"""
Automated Pipeline Tests for IFI Preprocessing, Features & Targets in RESQ-AI.

Verifies source file existence, processed datasets schema integrity, output feature matrix shape,
target matrix boundary validity, and confirms zero modification to raw source files.
"""

import json
import os
from pathlib import Path
import unittest
import pandas as pd
import numpy as np

RAW_DIR = r"C:\Users\pabbu\Downloads\16994648"
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DISTRICTS = BASE_DIR / "data" / "processed" / "ifi" / "ifi_districts_cleaned.csv"
PROCESSED_EVENTS = BASE_DIR / "data" / "processed" / "ifi" / "ifi_event_inventory_cleaned.csv"
METADATA_JSON = BASE_DIR / "data" / "processed" / "ifi" / "ifi_metadata.json"

FEATURE_PATH = BASE_DIR / "features" / "flood_history" / "ifi_flood_history_features.csv"
TARGET_PATH = BASE_DIR / "data" / "processed" / "ifi" / "ifi_flood_targets.csv"


class TestIFIPipeline(unittest.TestCase):

    def test_raw_ifi_source_exists(self):
        """Verify original downloaded IFI directory exists."""
        self.assertTrue(os.path.exists(RAW_DIR), f"Missing raw IFI path: {RAW_DIR}")
        self.assertTrue(os.path.exists(os.path.join(RAW_DIR, "DFSI.csv")))
        self.assertTrue(os.path.exists(os.path.join(RAW_DIR, "India_Flood_Inventory_v3.csv")))

    def test_processed_ifi_tables(self):
        """Verify cleaned district and event inventory CSVs exist."""
        self.assertTrue(PROCESSED_DISTRICTS.exists(), f"Missing districts CSV: {PROCESSED_DISTRICTS}")
        df_dist = pd.read_csv(PROCESSED_DISTRICTS)
        self.assertEqual(len(df_dist), 732)

        self.assertTrue(PROCESSED_EVENTS.exists(), f"Missing events CSV: {PROCESSED_EVENTS}")
        df_ev = pd.read_csv(PROCESSED_EVENTS)
        self.assertEqual(len(df_ev), 6876)

    def test_metadata_json_integrity(self):
        """Verify metadata JSON file exists and contains correct counts."""
        self.assertTrue(METADATA_JSON.exists(), f"Missing metadata JSON at {METADATA_JSON}")
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.assertEqual(meta["district_table_rows"], 732)
        self.assertEqual(meta["event_inventory_rows"], 6876)
        self.assertFalse(meta["raw_directory_modified"])

    def test_flood_history_features_matrix(self):
        """Verify predictor feature CSV exists, has 728 district records, and valid bounds."""
        self.assertTrue(FEATURE_PATH.exists(), f"Missing feature CSV at {FEATURE_PATH}")
        df = pd.read_csv(FEATURE_PATH)

        self.assertEqual(len(df), 728)
        expected_cols = [
            'state', 'district',
            'ifi_dfsi_score', 'ifi_flooded_area_pct', 'ifi_permanent_water_pct',
            'ifi_historical_event_count', 'ifi_mean_flood_duration_days',
            'ifi_total_fatalities', 'ifi_total_injured', 'ifi_flood_recurrence_rate'
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing feature column: {col}")

        # Check bounds
        self.assertTrue((df['ifi_dfsi_score'] >= 0.0).all())
        self.assertTrue((df['ifi_flooded_area_pct'] >= 0.0).all())
        self.assertTrue((df['ifi_flooded_area_pct'] <= 100.0).all())

    def test_target_matrix_integrity(self):
        """Verify ground-truth target CSV exists, has 728 district records, and valid risk levels."""
        self.assertTrue(TARGET_PATH.exists(), f"Missing target CSV at {TARGET_PATH}")
        df = pd.read_csv(TARGET_PATH)

        self.assertEqual(len(df), 728)
        expected_cols = [
            'state', 'district',
            'target_flooded_area_pct', 'target_dfsi_score',
            'target_flood_risk_binary', 'target_risk_level'
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing target column: {col}")

        # Check target values
        self.assertTrue((df['target_flood_risk_binary'].isin([0, 1])).all())
        valid_levels = {'LOW', 'MODERATE', 'HIGH', 'CRITICAL'}
        for lvl in df['target_risk_level'].unique():
            self.assertIn(lvl, valid_levels)


if __name__ == "__main__":
    unittest.main()
