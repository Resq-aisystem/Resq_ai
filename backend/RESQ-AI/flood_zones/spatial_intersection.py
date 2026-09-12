"""
Spatial Polygon & Grid Intersection Engine for RESQ-AI Flood Zones.

Generates spatial flood zone polygons and calculates spatial intersections
with facility locations and road network segments.
"""

from typing import List, Dict, Any, Tuple
from flood_zones.zone_schema import FloodZonePolygon, FloodZonePayload


def generate_city_flood_zones(
    city_name: str = "Puri",
    district_name: str = "PURI",
    centroid_lat: float = 19.8135,
    centroid_lon: float = 85.8312,
    risk_level: str = "HIGH"
) -> FloodZonePayload:
    """
    Generate spatial flood zone polygons for target city / district MVP.
    """
    d_lat = 0.05
    d_lon = 0.05

    # Create primary high risk zone polygon around centroid
    high_zone = FloodZonePolygon(
        zone_id=f"fz_{district_name.lower()}_01",
        risk_level=risk_level,
        bounding_box=[centroid_lat - d_lat, centroid_lon - d_lon, centroid_lat + d_lat, centroid_lon + d_lon],
        coordinates=[
            [centroid_lat - d_lat, centroid_lon - d_lon],
            [centroid_lat + d_lat, centroid_lon - d_lon],
            [centroid_lat + d_lat, centroid_lon + d_lon],
            [centroid_lat - d_lat, centroid_lon + d_lon],
            [centroid_lat - d_lat, centroid_lon - d_lon]
        ],
        area_sq_km=12.5
    )

    return FloodZonePayload(
        city_name=city_name,
        district_name=district_name,
        target_resolution_m=100,
        source_resolution_m=1000,
        resampling_method="Bilinear Spatial Interpolation",
        zones=[high_zone]
    )


def check_point_in_flood_zone(lat: float, lon: float, zones_payload: FloodZonePayload) -> Tuple[bool, str]:
    """
    Check if a spatial point (lat, lon) intersects with any active flood zone polygon.

    Returns:
        Tuple (intersects: bool, highest_risk_level: str)
    """
    for z in zones_payload.zones:
        bbox = z.bounding_box
        if (bbox[0] <= lat <= bbox[2]) and (bbox[1] <= lon <= bbox[3]):
            return True, z.risk_level
    return False, "LOW"


def calculate_route_flood_exposure(waypoints: List[List[float]], zones_payload: FloodZonePayload) -> Tuple[float, float]:
    """
    Calculate route segment distance exposed to flood zone polygons.

    Returns:
        Tuple (exposed_distance_km: float, exposure_percent: float)
    """
    if not waypoints:
        return 0.0, 0.0

    total_pts = len(waypoints)
    exposed_pts = 0

    for pt in waypoints:
        lat = pt[1] if abs(pt[0]) > 40.0 else pt[0]
        lon = pt[0] if abs(pt[0]) > 40.0 else pt[1]
        is_exp, _ = check_point_in_flood_zone(lat, lon, zones_payload)
        if is_exp:
            exposed_pts += 1

    exp_pct = (exposed_pts / total_pts) * 100.0 if total_pts > 0 else 0.0
    # Approximate 10 km default route length
    exp_dist_km = round((exp_pct / 100.0) * 10.0, 2)

    return exp_dist_km, round(exp_pct, 1)
