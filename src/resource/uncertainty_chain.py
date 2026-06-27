from __future__ import annotations

import random

from src.common.grid import Grid
from .volume_inversion import estimate_ice_volume


def monte_carlo_volume(
    ice_fraction: Grid,
    posterior: Grid,
    pixel_area_m2: float,
    depth_m: float,
    samples: int,
    seed: int,
) -> dict:
    rng = random.Random(seed)
    expected_values: list[float] = []
    for _ in range(samples):
        jittered_ice = [[max(0.0, min(1.0, value + rng.uniform(-0.06, 0.06))) for value in row] for row in ice_fraction]
        jittered_post = [[max(0.0, min(1.0, value + rng.uniform(-0.05, 0.05))) for value in row] for row in posterior]
        jittered_area = pixel_area_m2 * rng.uniform(0.9, 1.1)
        jittered_depth = depth_m * rng.uniform(0.8, 1.15)
        result = estimate_ice_volume(jittered_ice, jittered_post, jittered_area, jittered_depth)
        expected_values.append(result["expected_m3"])
    expected_values.sort()
    low = expected_values[int(0.1 * (len(expected_values) - 1))]
    high = expected_values[int(0.9 * (len(expected_values) - 1))]
    median = expected_values[len(expected_values) // 2]
    return {
        "samples": samples,
        "low_m3": low,
        "median_m3": median,
        "high_m3": high,
        "dominant_uncertainty_source": "demo dielectric and synthetic dual-band proxy assumptions",
    }
