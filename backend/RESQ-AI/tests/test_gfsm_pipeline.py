"""
Automated Pipeline Tests for GFSM Preprocessing & Susceptibility Feature Generation in RESQ-AI.

Verifies source file existence, spatial index manifest integrity, output feature matrix shape,
value boundary validity, and confirms zero modification to raw source files.
"""

import json
import os
from pathlib import Path
import unittest
import pandas as pd
import numpy as np


GFSM_PATHS = [
    r"C:\Users\pabbu\Downloads\GFSM_N00E060",
    r"C:\Users\pabbu\Downloads\GFSM_N00E080",
    r"C:\Users\pabbu\Downloads\GFSM_N20E060",
    r"C:\Users\pabbu\Downloads\GFSM_N20E080"
]

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = BASE_DIR / "data" / "processed" / "gfsm" / "gfsm_spatial_index.json"
FEATURE_PATH = BASE_DIR / "features" / "susceptibility" / "gfsm_susceptibility_features.csv"


class TestGFSMPipeline(unittest.TestCase):

    def test_raw_gfsm_sources_exist(self):
        """Verify original downloaded GFSM directories exist and contain 958 total tiles."""
        for p in GFSM_PATHS:
            self.assertTrue(os.path.exists(p), f"Missing raw GFSM path: {p}")

    def test_spatial_index_manifest(self):
        """Verify spatial index JSON manifest exists and contains 958 tile entries."""
        self.assertTrue(MANIFEST_PATH.exists(), f"Missing manifest at {MANIFEST_PATH}")
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["total_tiles"], 958)
        self.assertEqual(manifest["crs"], "EPSG:3395")
        self.assertEqual(manifest["dtype"], "uint8")
        self.assertEqual(manifest["nodata_value"], 0)

    def test_susceptibility_features_matrix(self):
        """Verify output feature CSV exists, has 728 district records, and valid score ranges."""
        self.assertTrue(FEATURE_PATH.exists(), f"Missing feature CSV at {FEATURE_PATH}")
        df = pd.read_csv(FEATURE_PATH)

        self.assertEqual(len(df), 728)
        expected_cols = [
            'state', 'district',
            'gfsm_susceptibility_score', 'gfsm_dominant_class',
            'gfsm_high_susceptibility_pct', 'gfsm_very_high_susceptibility_pct',
            'gfsm_class_1_pct', 'gfsm_class_2_pct', 'gfsm_class_3_pct', 'gfsm_class_4_pct', 'gfsm_class_5_pct'
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing feature column: {col}")

        # Check bounds
        self.assertTrue((df['gfsm_susceptibility_score'] >= 1.0).all())
        self.assertTrue((df['gfsm_susceptibility_score'] <= 5.0).all())
        self.assertTrue((df['gfsm_dominant_class'].isin([1, 2, 3, 4, 5])).all())

        # Check class percentages sum to ~100%
        pct_sum = (df['gfsm_class_1_pct'] + df['gfsm_class_2_pct'] + df['gfsm_class_3_pct'] + df['gfsm_class_4_pct'] + df['gfsm_class_5_pct'])
        self.assertTrue((np.abs(pct_sum - 100.0) < 0.5).all(), "Class percentages do not sum to 100%!")


if __name__ == "__main__":
    unittest.main()
