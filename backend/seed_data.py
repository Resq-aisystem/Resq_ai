"""
RESQ-AI Database Seed Script
Populates the SQLite database with realistic flood emergency locations and active alerts
representing an active regional flash flood emergency scenario.
"""

from datetime import datetime, timedelta
from backend.database import SessionLocal, engine, Base
from backend.models import Location, Alert

def seed_database():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if locations already exist
        existing_count = db.query(Location).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} locations. Clearing old test data for fresh demo seed...")
            db.query(Alert).delete()
            db.query(Location).delete()
            db.commit()
        
        now = datetime.utcnow()
        
        # 1. Create realistic locations
        loc1 = Location(
            name="Central River Memorial Hospital",
            type="hospital",
            address="1200 Red River St, Austin, TX",
            latitude=30.2747,
            longitude=-97.7404,
            capacity=450,
            current_occupancy=420,
            contact_name="Dr. Sarah Jenkins",
            contact_phone="512-555-0101",
            contact_email="sjenkins@centralmemorial.org",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        loc2 = Location(
            name="Riverside Elder Care Center",
            type="hospital",
            address="2400 E Riverside Dr, Austin, TX",
            latitude=30.2458,
            longitude=-97.7250,
            capacity=180,
            current_occupancy=165,
            contact_name="Marcus Vance",
            contact_phone="512-555-0102",
            contact_email="mvance@riversideelder.org",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        loc3 = Location(
            name="Highland Regional Evacuation Shelter",
            type="shelter",
            address="6001 Airport Blvd, Austin, TX",
            latitude=30.3280,
            longitude=-97.7150,
            capacity=850,
            current_occupancy=210,
            contact_name="Elena Rodriguez",
            contact_phone="512-555-0103",
            contact_email="erodriguez@travisoem.gov",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        loc4 = Location(
            name="South Congress Emergency Refuge",
            type="shelter",
            address="3800 S Congress Ave, Austin, TX",
            latitude=30.2200,
            longitude=-97.7700,
            capacity=600,
            current_occupancy=95,
            contact_name="David Brooks",
            contact_phone="512-555-0104",
            contact_email="dbrooks@austinredcross.org",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        loc5 = Location(
            name="Colorado River Municipal Water Intake",
            type="critical_infrastructure",
            address="1000 Barton Springs Rd, Austin, TX",
            latitude=30.2600,
            longitude=-97.7600,
            capacity=50,
            current_occupancy=14,
            contact_name="Eng. Robert Chen",
            contact_phone="512-555-0105",
            contact_email="rchen@austinwater.gov",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        loc6 = Location(
            name="East Austin Substation & Drainage Hub",
            type="critical_infrastructure",
            address="3200 Pleasant Valley Rd, Austin, TX",
            latitude=30.2520,
            longitude=-97.7100,
            capacity=30,
            current_occupancy=8,
            contact_name="Chief Tech Linda Martinez",
            contact_phone="512-555-0106",
            contact_email="lmartinez@austinenergy.com",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        loc7 = Location(
            name="St. David's North Medical Pavilion",
            type="hospital",
            address="12221 N Mopac Expy, Austin, TX",
            latitude=30.4050,
            longitude=-97.7050,
            capacity=320,
            current_occupancy=290,
            contact_name="Dr. James Wilson",
            contact_phone="512-555-0107",
            contact_email="jwilson@stdavidsnorth.org",
            is_active=True,
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        db.add_all([loc1, loc2, loc3, loc4, loc5, loc6, loc7])
        db.commit()
        
        # 2. Create realistic alerts tied to locations
        alert1 = Alert(
            location_id=loc2.id,  # Riverside Elder Care
            severity="critical",
            alert_type="evacuation_order",
            title="Immediate Evacuation Order: Flash Flood Inundation at Riverside Basin",
            description="Rapid flood stage surge along Town Lake / Colorado River lower basin. Predicted water level rise exceeds 2.8m within 3 hours. Ground floor isolation imminent.",
            water_level=2.8,
            predicted_peak=3.4,
            affected_population=8500,
            recommended_action="Execute Code Red facility evacuation immediately. Deploy high-clearance medical transport units to transfer 165 mobility-impaired residents to Highland Regional Shelter via Route Alpha (Safest Path). Stage inflatable rescue crafts at Pleasant Valley connector.",
            justification="Predicted water crest (3.4m) exceeds 100-year floodwall design limit by 0.6m. Resident mobility limitations necessitate a 90-minute operational lead time before road submergence.",
            status="active",
            issued_by="Travis County Emergency Operations Command / NWS Flood Intelligence",
            issued_at=now - timedelta(minutes=45),
            expires_at=now + timedelta(hours=8),
            created_at=now - timedelta(minutes=45),
            updated_at=now
        )
        
        alert2 = Alert(
            location_id=loc1.id,  # Central Memorial Hospital
            severity="high",
            alert_type="flood_warning",
            title="Severe Flood Warning: Red River Drainage Basin Overflow",
            description="Drainage capacity exceeded along Waller Creek basin. Sub-grade backup generators and emergency department ambulance bays threatened by standing surface runoff.",
            water_level=1.6,
            predicted_peak=2.1,
            affected_population=14200,
            recommended_action="Deploy secondary flood barrier gates around subterranean backup generators. Reroute non-trauma inbound ambulances to North Medical Pavilion. Prepare 45 ICU patients for vertical evacuation to 4th floor.",
            justification="Creek tributary telemetry indicates 0.35m/hr rise rate. Substation redundancy compromised if baseline exceeds 1.8m.",
            status="active",
            issued_by="City Emergency Management & USGS Hydrologic Monitoring",
            issued_at=now - timedelta(hours=1, minutes=15),
            expires_at=now + timedelta(hours=12),
            created_at=now - timedelta(hours=1, minutes=15),
            updated_at=now
        )
        
        alert3 = Alert(
            location_id=loc5.id,  # Water Intake
            severity="high",
            alert_type="flood_warning",
            title="Turbidity & Inundation Warning: Water Utility Intake Station 4",
            description="High silt velocity and debris dams forming near intake gate structure. Flood stage 1.9m above normal pool level.",
            water_level=1.9,
            predicted_peak=2.4,
            affected_population=65000,
            recommended_action="Activate automated backwash cycles, throttle secondary intake valves, and deploy municipal maintenance engineers to monitor weir stability.",
            justification="Debris loading increases pump cavitation risk. Overflow may contaminate municipal clearwell reservoirs.",
            status="active",
            issued_by="Water Resources Authority & Austin Water Utility",
            issued_at=now - timedelta(hours=2),
            expires_at=now + timedelta(hours=10),
            created_at=now - timedelta(hours=2),
            updated_at=now
        )
        
        alert4 = Alert(
            location_id=loc6.id,  # Substation
            severity="medium",
            alert_type="flood_warning",
            title="Elevated Water Watch: Pleasant Valley Low-Water Crossing",
            description="Retention basin at 82% holding capacity. Surcharge spillway activated. Surrounding arterial corridors experiencing localized ponding.",
            water_level=0.8,
            predicted_peak=1.2,
            affected_population=3200,
            recommended_action="Close Pleasant Valley low-water bridge gate. Station road crews to monitor culvert debris and divert non-emergency transit.",
            justification="Historical telemetry correlates 0.9m stage with hydroplaning risk on arterial intersections.",
            status="active",
            issued_by="Regional Transportation Management Center",
            issued_at=now - timedelta(hours=2, minutes=30),
            expires_at=now + timedelta(hours=6),
            created_at=now - timedelta(hours=2, minutes=30),
            updated_at=now
        )
        
        alert5 = Alert(
            location_id=loc3.id,  # Highland Shelter
            severity="low",
            alert_type="all_clear",
            title="Staging Readiness Alert: Primary Northern Evacuation Hub",
            description="High-ground shelter operating at normal condition. Surface drainage fully functional with zero flood ingress risk.",
            water_level=0.2,
            predicted_peak=0.4,
            affected_population=0,
            recommended_action="Maintain standby logistics, open intake gates 3 and 4 for arriving evacuees from Riverside, coordinate medical intake triage with Red Cross staff.",
            justification="Elevation sits 28m above the 500-year floodplain; confirmed safe haven for regional reception.",
            status="active",
            issued_by="Department of Homeland Security & Emergency Management",
            issued_at=now - timedelta(hours=3),
            expires_at=now + timedelta(hours=24),
            created_at=now - timedelta(hours=3),
            updated_at=now
        )
        
        alert6 = Alert(
            location_id=loc7.id,  # St. David's North
            severity="low",
            alert_type="flood_warning",
            title="Advisory: Stormwater Runoff Ingress on Perimeter Access Road",
            description="Catch basin siltation causing slow ponding along perimeter road. Hospital core facility unaffected.",
            water_level=0.3,
            predicted_peak=0.5,
            affected_population=1100,
            recommended_action="Clear northern catch basins and direct arriving transit through South gate entrance.",
            justification="Surface ponding limited to outer ring road; no clinical or patient care impact.",
            status="active",
            issued_by="City Emergency Management",
            issued_at=now - timedelta(hours=4),
            expires_at=now + timedelta(hours=12),
            created_at=now - timedelta(hours=4),
            updated_at=now
        )
        
        db.add_all([alert1, alert2, alert3, alert4, alert5, alert6])
        db.commit()
        
        print("Successfully seeded 7 locations and 6 active alerts into flood_response.db!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
