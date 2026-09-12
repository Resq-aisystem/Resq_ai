"""
Automated Pipeline Tests for CAMELS-IND Preprocessing & Hydrology Feature Generation in RESQ-AI.

Verifies source file existence, processed datasets schema integrity, output feature matrix shape,
value boundary validity, and confirms zero modification to raw source files.
"""

import json
import os
from pathlib import Path
import unittest
import pandas as pd
import numpy as np

RAW_DIR = r"C:\Users\pabbu\Downloads\CAMELS_IND_All_Catchments"
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_CATCHMENTS = BASE_DIR / "data" / "processed" / "camels_ind" / "camels_ind_catchments_cleaned.csv"
PROCESSED_FORCINGS = BASE_DIR / "data" / "processed" / "camels_ind" / "camels_ind_forcings_summary.csv"
METADATA_JSON = BASE_DIR / "data" / "processed" / "camels_ind" / "camels_ind_metadata.json"
FEATURE_PATH = BASE_DIR / "features" / "hydrology" / "camels_ind_hydrology_features.csv"


class TestCAMELSINDPipeline(unittest.TestCase):

    def test_raw_camels_ind_source_exists(self):
        """Verify original downloaded CAMELS-IND directory exists."""
        self.assertTrue(os.path.exists(RAW_DIR), f"Missing raw CAMELS-IND path: {RAW_DIR}")
        attr_csv_path = os.path.join(RAW_DIR, "attributes_csv")
        self.assertTrue(os.path.exists(attr_csv_path))

    def test_processed_catchment_tables(self):
        """Verify cleaned catchments and forcings summary CSVs exist and contain 472 rows."""
        self.assertTrue(PROCESSED_CATCHMENTS.exists(), f"Missing catchments CSV: {PROCESSED_CATCHMENTS}")
        df_cat = pd.read_csv(PROCESSED_CATCHMENTS)
        self.assertEqual(len(df_cat), 472)

        self.assertTrue(PROCESSED_FORCINGS.exists(), f"Missing forcings summary CSV: {PROCESSED_FORCINGS}")
        df_f = pd.read_csv(PROCESSED_FORCINGS)
        self.assertEqual(len(df_f), 472)

    def test_metadata_json_integrity(self):
        """Verify metadata JSON file exists and contains correct catchment count."""
        self.assertTrue(METADATA_JSON.exists(), f"Missing metadata JSON at {METADATA_JSON}")
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.assertEqual(meta["total_catchments"], 472)
        self.assertEqual(meta["total_forcing_files"], 472)
        self.assertFalse(meta["raw_directory_modified"])

    def test_hydrology_features_matrix(self):
        """Verify output feature CSV exists, has 728 district records, and valid bounds."""
        self.assertTrue(FEATURE_PATH.exists(), f"Missing feature CSV at {FEATURE_PATH}")
        df = pd.read_csv(FEATURE_PATH)

        self.assertEqual(len(df), 728)
        expected_cols = [
            'state', 'district',
            'camels_aridity_index', 'camels_p_mean_mm_day', 'camels_q_mean_mm_day',
            'camels_runoff_ratio', 'camels_soil_moisture_mean_kg_m2',
            'camels_soil_moisture_lvl1_top', 'camels_soil_moisture_lvl4_deep',
            'camels_soil_conductivity_top', 'camels_soil_awc_top',
            'camels_high_precip_freq_days', 'camels_low_precip_freq_days',
            'camels_elevation_mean_m', 'camels_slope_mean_deg',
            'camels_forest_cover_pct', 'camels_dam_count', 'camels_dam_storage_capacity_mcm'
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing feature column: {col}")

        # Check bounds
        self.assertTrue((df['camels_aridity_index'] > 0).all())
        self.assertTrue((df['camels_runoff_ratio'] >= 0.0).all())
        self.assertTrue((df['camels_runoff_ratio'] <= 1.0).all())
        self.assertTrue((df['camels_soil_moisture_mean_kg_m2'] > 0).all())


if __name__ == "__main__":
    unittest.main()
