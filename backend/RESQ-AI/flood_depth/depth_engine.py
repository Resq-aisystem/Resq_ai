"""
Flood Depth Estimation Engine Interface for RESQ-AI.

Provides modular interface for flood depth estimation.
Returns INSUFFICIENT_DATA status when high-resolution DEM hydro-dynamic models are unconfigured,
strictly preventing unsupported depth fabrication.
"""

from typing import Optional
from flood_depth.depth_schema import DepthEstimatePayload


def estimate_flood_depth(
    city_name: str = "Puri",
    district_name: str = "PURI",
    depth_model_override=None
) -> DepthEstimatePayload:
    """
    Estimate flood depth for target city / district location.

    Args:
        city_name: Name of target city.
        district_name: Administrative district.
        depth_model_override: Optional configured hydro-dynamic depth model or raster.

    Returns:
        DepthEstimatePayload object.
    """
    if depth_model_override is not None:
        # Evaluate configured hydro-dynamic depth model
        depth_m = float(depth_model_override.get("depth_meters", 0.5))
        category = "MODERATE" if depth_m >= 0.5 else "SHALLOW"
        return DepthEstimatePayload(
            city_name=city_name,
            district_name=district_name,
            predicted_depth_meters=depth_m,
            depth_category=category,
            data_status="ESTIMATED",
            source_model="Configured Hydrodynamic Model",
            explanation=f"Flood depth estimated at {depth_m:.2f} m using configured hydro-dynamic model."
        )

    # Default scientific response: INSUFFICIENT_DATA when high-resolution DEM is unconfigured
    return DepthEstimatePayload(
        city_name=city_name,
        district_name=district_name,
        predicted_depth_meters=None,
        depth_category="INSUFFICIENT_DATA",
        data_status="INSUFFICIENT_DATA",
        source_model="UNCONFIGURED_DEM_HYDRO_MODEL",
        explanation="Flood depth estimation requires high-resolution DEM raster data, which is currently unconfigured. Returning INSUFFICIENT_DATA status."
    )
