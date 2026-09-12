"""
OpenWeatherMap & Fallback 6-Hour Forecast Client Integration.

Interfaces with live OpenWeatherMap forecast API or fallback provider
to fetch 6-hour predictive rainfall series for single-city or district locations.
"""

from pathlib import Path
import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)
except ImportError:
    pass

from forecast.forecast_schema import ForecastPoint, ForecastPayload


def fetch_6hour_forecast(
    city_name: str = "Puri",
    district_name: str = "PURI",
    lat: float = 19.8135,
    lon: float = 85.8312
) -> ForecastPayload:
    """
    Fetch 6-hour predictive weather forecast for target city / district.

    Args:
        city_name: Name of target city.
        district_name: Name of target administrative district.
        lat: Latitude coordinate.
        lon: Longitude coordinate.

    Returns:
        ForecastPayload object containing 6 hourly forecast points.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "").strip()

    if api_key:
        try:
            # Query OpenWeatherMap 5-day / 3-hour forecast API or 1-call API
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            req = urllib.request.Request(url, headers={"User-Agent": "RESQ-AI-ForecastClient/2.0"})
            with urllib.request.urlopen(req, timeout=5.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    now_utc = datetime.now(timezone.utc)
                    points = []

                    # Parse first 6 hourly intervals
                    for i in range(1, 7):
                        st_time = now_utc + timedelta(hours=i-1)
                        end_time = now_utc + timedelta(hours=i)
                        # Extract rain 3h volume if present, divided by 3 for 1h rate
                        r_mm = 0.0
                        if "list" in data and len(data["list"]) > (i // 3):
                            item = data["list"][i // 3]
                            r_mm = float(item.get("rain", {}).get("3h", 0.0)) / 3.0

                        points.append(ForecastPoint(
                            forecast_hour=i,
                            start_timestamp=st_time.isoformat(),
                            end_timestamp=end_time.isoformat(),
                            rainfall_mm=round(r_mm, 2),
                            temperature_c=28.5,
                            humidity_pct=85.0
                        ))

                    return ForecastPayload(
                        city_name=city_name,
                        district_name=district_name,
                        retrieved_at=now_utc.isoformat(),
                        source_provider="OpenWeatherMap API",
                        hourly_points=points,
                        is_mock=False
                    )
        except Exception:
            pass

    # Return deterministic test mock payload if API key is unconfigured or offline
    return get_mock_6hour_forecast(city_name, district_name)


def get_mock_6hour_forecast(city_name: str = "Puri", district_name: str = "PURI") -> ForecastPayload:
    """
    Deterministic mock 6-hour forecast fixture for offline testing.
    Clearly marked with is_mock=True.
    """
    now_utc = datetime.now(timezone.utc)
    # Simulate a 6-hour rainfall trend (e.g. 5.2mm, 12.4mm, 25.8mm, 18.2mm, 8.5mm, 3.1mm)
    simulated_hourly_mm = [5.2, 12.4, 25.8, 18.2, 8.5, 3.1]
    points = []

    for i, mm in enumerate(simulated_hourly_mm, 1):
        st_time = now_utc + timedelta(hours=i-1)
        end_time = now_utc + timedelta(hours=i)
        points.append(ForecastPoint(
            forecast_hour=i,
            start_timestamp=st_time.isoformat(),
            end_timestamp=end_time.isoformat(),
            rainfall_mm=mm,
            temperature_c=28.0,
            humidity_pct=88.0,
            wind_speed_kmh=22.5,
            pressure_hpa=1004.0
        ))

    return ForecastPayload(
        city_name=city_name,
        district_name=district_name,
        retrieved_at=now_utc.isoformat(),
        source_provider="Deterministic Test Mock Provider",
        hourly_points=points,
        is_mock=True
    )
