"""
Automated Pipeline Tests for NASA GDIS Preprocessing & Feature Generation in RESQ-AI.

Verifies source file existence, processed datasets schema integrity, output feature matrix shape,
coordinate validity, and confirms zero modification to raw source files.
"""

import json
import os
from pathlib import Path
import unittest
import pandas as pd
import numpy as np

RAW_CSV_PATH = r"C:\Users\pabbu\Downloads\pend-gdis-1960-2018-disasterlocations-csv\pend-gdis-1960-2018-disasterlocations.csv"
BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_CSV_PATH = BASE_DIR / "data" / "processed" / "gdis" / "gdis_disaster_locations_cleaned.csv"
METADATA_JSON = BASE_DIR / "data" / "processed" / "gdis" / "gdis_metadata.json"
FEATURE_PATH = BASE_DIR / "features" / "disaster_history" / "gdis_disaster_history_features.csv"


class TestGDISPipeline(unittest.TestCase):

    def test_raw_gdis_source_exists(self):
        """Verify original downloaded NASA GDIS CSV file exists."""
        self.assertTrue(os.path.exists(RAW_CSV_PATH), f"Missing raw GDIS path: {RAW_CSV_PATH}")

    def test_processed_gdis_cleaned_csv(self):
        """Verify cleaned CSV exists, has 39,953 rows, and valid schema."""
        self.assertTrue(CLEANED_CSV_PATH.exists(), f"Missing cleaned CSV: {CLEANED_CSV_PATH}")
        df_clean = pd.read_csv(CLEANED_CSV_PATH)
        self.assertEqual(len(df_clean), 39953)

        expected_cols = ['emdat_id', 'country_name', 'event_year', 'disaster_type', 'latitude', 'longitude']
        for col in expected_cols:
            self.assertIn(col, df_clean.columns)

        # Coordinate bounds check
        self.assertTrue(df_clean['latitude'].between(-90.0, 90.0).all())
        self.assertTrue(df_clean['longitude'].between(-180.0, 180.0).all())

    def test_metadata_json_integrity(self):
        """Verify metadata JSON file exists and contains correct counts."""
        self.assertTrue(METADATA_JSON.exists(), f"Missing metadata JSON at {METADATA_JSON}")
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.assertEqual(meta["global_records_count"], 39953)
        self.assertEqual(meta["india_records_count"], 2253)
        self.assertFalse(meta["raw_file_modified"])

    def test_disaster_history_features_matrix(self):
        """Verify predictor feature CSV exists, has 728 district records, and valid bounds."""
        self.assertTrue(FEATURE_PATH.exists(), f"Missing feature CSV at {FEATURE_PATH}")
        df = pd.read_csv(FEATURE_PATH)

        self.assertEqual(len(df), 728)
        expected_cols = [
            'state', 'district',
            'gdis_historical_disaster_count', 'gdis_flood_event_count',
            'gdis_storm_event_count', 'gdis_drought_event_count',
            'gdis_extreme_temp_event_count', 'gdis_earthquake_event_count',
            'gdis_landslide_event_count', 'gdis_unique_disaster_types_count',
            'gdis_year_first_record', 'gdis_year_last_record',
            'gdis_recent_10yr_event_count', 'gdis_disaster_frequency_per_decade'
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing feature column: {col}")

        # Check non-negative bounds
        self.assertTrue((df['gdis_historical_disaster_count'] >= 0).all())
        self.assertTrue((df['gdis_flood_event_count'] >= 0).all())
        self.assertTrue((df['gdis_disaster_frequency_per_decade'] >= 0.0).all())


if __name__ == "__main__":
    unittest.main()
