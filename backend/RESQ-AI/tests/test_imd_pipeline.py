"""
Automated Pipeline Tests for IMD Dataset Processing in RESQ-AI.

Verifies cleaned data integrity, feature dataset completeness, summary JSON accuracy,
and confirms that the raw dataset file was not modified.
"""

import json
import os
from pathlib import Path
import unittest
import pandas as pd


RAW_DATA_PATH = r"C:\Users\pabbu\Downloads\rainfall_districtwise_daily_imd.csv.csv"
BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DATA_PATH = BASE_DIR / "data" / "processed" / "imd" / "imd_rainfall_cleaned.csv"
FEATURE_DATA_PATH = BASE_DIR / "features" / "rainfall" / "imd_rainfall_features.csv"
SUMMARY_JSON_PATH = BASE_DIR / "data" / "interim" / "imd_dataset_summary.json"


class TestIMDPipeline(unittest.TestCase):

    def test_raw_dataset_exists_and_unmodified(self):
        """Verify raw IMD dataset file exists at absolute path and is accessible."""
        self.assertTrue(os.path.exists(RAW_DATA_PATH), f"Raw dataset missing at: {RAW_DATA_PATH}")
        df_raw = pd.read_csv(RAW_DATA_PATH)
        self.assertEqual(len(df_raw), 17457, f"Raw row count changed! Expected 17457, got {len(df_raw)}")
        self.assertEqual(len(df_raw.columns), 22, f"Raw column count changed! Expected 22, got {len(df_raw.columns)}")

    def test_cleaned_dataset_integrity(self):
        """Verify cleaned dataset loads, contains 17457 rows and expected standardized columns."""
        self.assertTrue(CLEANED_DATA_PATH.exists(), f"Cleaned dataset missing at: {CLEANED_DATA_PATH}")
        df_clean = pd.read_csv(CLEANED_DATA_PATH)

        self.assertEqual(len(df_clean), 17457)
        self.assertEqual(len(df_clean.columns), 22)

        expected_cols = [
            'state', 'district', 'date',
            'daily_actual_mm', 'daily_normal_mm', 'daily_departure_perc', 'daily_category',
            'weekly_actual_mm', 'weekly_normal_mm', 'weekly_departure_perc', 'weekly_category',
            'cumulative_actual_mm', 'cumulative_normal_mm', 'cumulative_departure_perc', 'cumulative_category',
            'monthly_actual_mm', 'monthly_normal_mm', 'monthly_departure_perc', 'monthly_category'
        ]
        for col in expected_cols:
            self.assertIn(col, df_clean.columns, f"Missing expected clean column: {col}")

    def test_rainfall_numeric_bounds(self):
        """Verify no negative rainfall values in daily actual or normal columns."""
        df_clean = pd.read_csv(CLEANED_DATA_PATH)
        self.assertTrue((df_clean['daily_actual_mm'] >= 0).all(), "Found negative daily_actual_mm values!")
        self.assertTrue((df_clean['daily_normal_mm'] >= 0).all(), "Found negative daily_normal_mm values!")

    def test_feature_dataset_completeness(self):
        """Verify generated feature dataset exists, shape is valid, and key features are present."""
        self.assertTrue(FEATURE_DATA_PATH.exists(), f"Feature dataset missing at: {FEATURE_DATA_PATH}")
        df_feat = pd.read_csv(FEATURE_DATA_PATH)

        self.assertEqual(len(df_feat), 17457)

        required_features = [
            'state', 'district', 'date',
            'rolling_3d_rainfall_mm', 'rolling_7d_rainfall_mm', 'rolling_14d_rainfall_mm',
            'rolling_3d_max_mm', 'rolling_7d_max_mm',
            'rainfall_anomaly_mm', 'is_rainy_day', 'consecutive_rainy_days'
        ]
        for feat in required_features:
            self.assertIn(feat, df_feat.columns, f"Missing feature column: {feat}")

        # Check feature bounds
        self.assertTrue((df_feat['rolling_3d_rainfall_mm'] >= 0).all(), "Negative rolling_3d_rainfall_mm values!")
        self.assertTrue((df_feat['is_rainy_day'].isin([0, 1])).all(), "is_rainy_day contains non-binary values!")

    def test_summary_json_integrity(self):
        """Verify dataset summary JSON exists and contains matching metrics."""
        self.assertTrue(SUMMARY_JSON_PATH.exists(), f"Summary JSON missing at: {SUMMARY_JSON_PATH}")
        with open(SUMMARY_JSON_PATH, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["row_count"], 17457)
        self.assertEqual(summary["column_count"], 22)
        self.assertEqual(summary["unique_states"], 39)
        self.assertEqual(summary["unique_districts"], 728)
        self.assertFalse(summary["cleaning_summary"]["raw_file_modified"])


if __name__ == "__main__":
    unittest.main()
