from __future__ import annotations

from src.common.grid import Grid


def estimate_ice_volume(ice_fraction: Grid, posterior: Grid, pixel_area_m2: float, depth_m: float) -> dict:
    expected = 0.0
    low = 0.0
    high = 0.0
    for r in range(len(ice_fraction)):
        for c in range(len(ice_fraction[0])):
            abundance = ice_fraction[r][c] * posterior[r][c]
            expected += abundance * pixel_area_m2 * depth_m
            low += max(0.0, abundance - 0.12) * pixel_area_m2 * depth_m
            high += min(1.0, abundance + 0.12) * pixel_area_m2 * depth_m
    return {
        "low_m3": low,
        "expected_m3": expected,
        "high_m3": high,
        "water_yield_low_m3": low * 0.92,
        "water_yield_expected_m3": expected * 0.92,
        "water_yield_high_m3": high * 0.92,
    }
