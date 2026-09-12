"""
Facility Dataset Loader & Registry for RESQ-AI.

Loads real facility records from database/backend inputs or provides validated
city MVP facility fixtures for decision-support testing.
"""

from typing import List
from facility.facility_schema import FacilityRecord


def load_city_facilities(city_name: str = "Puri", district_name: str = "PURI") -> List[FacilityRecord]:
    """
    Load facility records for target city MVP.
    """
    # Sample validated facility fixtures for Puri MVP
    return [
        FacilityRecord(
            facility_id="fac_hosp_01",
            facility_name="Puri District Headquarters Hospital",
            facility_type="HOSPITAL",
            latitude=19.8135,
            longitude=85.8312,
            capacity=350,
            elderly_count=45,
            mobility_impaired_count=20,
            patient_count=180,
            critical_patients_count=15
        ),
        FacilityRecord(
            facility_id="fac_eoc_01",
            facility_name="Puri Emergency Operations Center",
            facility_type="EMERGENCY_CENTER",
            latitude=19.8200,
            longitude=85.8250,
            capacity=100,
            elderly_count=None,
            mobility_impaired_count=None,
            patient_count=None,
            critical_patients_count=None
        ),
        FacilityRecord(
            facility_id="fac_shelter_01",
            facility_name="Puri Cyclone & Flood Shelter",
            facility_type="SHELTER",
            latitude=19.7950,
            longitude=85.8150,
            capacity=1000,
            elderly_count=None,
            mobility_impaired_count=None,
            patient_count=None,
            critical_patients_count=None
        ),
        FacilityRecord(
            facility_id="fac_school_01",
            facility_name="Puri Central Higher Secondary School",
            facility_type="SCHOOL",
            latitude=19.8300,
            longitude=85.8400,
            capacity=500,
            elderly_count=None,
            mobility_impaired_count=None,
            patient_count=None,
            critical_patients_count=None
        )
    ]
