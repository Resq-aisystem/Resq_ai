"""
OSRM Routing API Client Integration for RESQ-AI.

Interfaces with OSRM (Open Source Routing Machine) engine to fetch candidate
road geometries, distances (km), and durations (minutes).
Provides robust network handling and clean test fixtures for offline testing.
"""

from pathlib import Path
import json
import urllib.request
import urllib.parse
import yaml

from route_risk.route_scoring.route_contract import Coordinates, RouteRequest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "route_risk.yaml"

_CONFIG_CACHE = None


def _load_osrm_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "osrm": {
                    "base_url": "http://router.project-osrm.org",
                    "profile": "driving",
                    "timeout_seconds": 5.0
                }
            }
    return _CONFIG_CACHE


def fetch_osrm_routes(origin: Coordinates, destination: Coordinates) -> list:
    """
    Fetch candidate route geometries from OSRM endpoint.

    Args:
        origin: Origin Coordinates object.
        destination: Destination Coordinates object.

    Returns:
        List of dict objects containing distance_km, duration_minutes, and waypoints geometry.
        Returns empty list or mock routes if service is unreachable.
    """
    cfg = _load_osrm_config()
    osrm_cfg = cfg.get("osrm", {})
    base_url = osrm_cfg.get("base_url", "http://router.project-osrm.org")
    profile = osrm_cfg.get("profile", "driving")
    timeout = float(osrm_cfg.get("timeout_seconds", 5.0))

    # OSRM expects: /route/v1/profile/lon1,lat1;lon2,lat2?overview=full&geometries=geojson&alternatives=true
    coordinates_str = f"{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}"
    url = f"{base_url}/route/v1/{profile}/{coordinates_str}?overview=full&geometries=geojson&alternatives=true"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RESQ-AI-RoutingClient/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("code") == "Ok" and "routes" in data:
                    parsed_routes = []
                    for idx, r in enumerate(data["routes"]):
                        dist_km = r["distance"] / 1000.0
                        dur_min = r["duration"] / 60.0
                        geometry = r.get("geometry", {}).get("coordinates", [])
                        parsed_routes.append({
                            "route_id": f"osrm_route_{idx + 1}",
                            "distance_km": round(dist_km, 2),
                            "duration_minutes": round(dur_min, 2),
                            "waypoints": geometry,
                            "is_mock": False
                        })
                    return parsed_routes
    except Exception as e:
        # Service unreachable or offline in test environment
        pass

    # Fallback to test mock fixture if network query fails
    return get_mock_osrm_response(origin, destination)


def get_mock_osrm_response(origin: Coordinates, destination: Coordinates) -> list:
    """
    Mock unit-test fixture ONLY used for offline testing or when live OSRM is unreachable.
    Clearly marked with is_mock=True.
    """
    # Calculate straight-line distance heuristic
    d_lat = destination.latitude - origin.latitude
    d_lon = destination.longitude - origin.longitude
    base_dist = math_hypot_approx(d_lat, d_lon) * 111.0  # Approx 111 km per degree

    base_dist = max(5.0, base_dist)

    # Generate 3 realistic candidate routes (Main Highway, Scenic Detour, Alternative Bypass)
    return [
        {
            "route_id": "mock_route_1_direct",
            "distance_km": round(base_dist, 2),
            "duration_minutes": round((base_dist / 60.0) * 60.0, 2),  # 60 km/h average
            "waypoints": [[origin.longitude, origin.latitude], [destination.longitude, destination.latitude]],
            "is_mock": True
        },
        {
            "route_id": "mock_route_2_detour",
            "distance_km": round(base_dist * 1.18, 2),
            "duration_minutes": round(((base_dist * 1.18) / 70.0) * 60.0, 2),  # Faster highway, longer distance
            "waypoints": [[origin.longitude, origin.latitude], [origin.longitude + d_lon*0.5, origin.latitude + d_lat*0.3], [destination.longitude, destination.latitude]],
            "is_mock": True
        },
        {
            "route_id": "mock_route_3_bypass",
            "distance_km": round(base_dist * 1.35, 2),
            "duration_minutes": round(((base_dist * 1.35) / 55.0) * 60.0, 2),  # Longer detour
            "waypoints": [[origin.longitude, origin.latitude], [origin.longitude - d_lon*0.3, origin.latitude + d_lat*0.7], [destination.longitude, destination.latitude]],
            "is_mock": True
        }
    ]


def math_hypot_approx(dx: float, dy: float) -> float:
    return (dx*dx + dy*dy)**0.5
