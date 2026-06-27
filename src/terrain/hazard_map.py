from __future__ import annotations

import math

from src.common.grid import Grid, crater_field, gradient_magnitude, normalize, seeded_rng, smooth


def synthesize_dem(grid_size: int, seed: int) -> Grid:
    rng = seeded_rng(seed + 29)
    field = crater_field(grid_size, grid_size, rng)
    dem = [[1800.0 - 240.0 * field[r][c] + 18.0 * math.sin(r / 6.0) for c in range(grid_size)] for r in range(grid_size)]
    return smooth(dem, 1)


def derive_topography_proxy(texture: Grid, orbit_geometry: dict, seed: int) -> Grid:
    rows = len(texture)
    cols = len(texture[0]) if rows else 0
    if rows == 0 or cols == 0:
        return []
    rng = seeded_rng(seed + 29)
    crater = crater_field(rows, cols, rng)
    pitch_term = abs(orbit_geometry.get("pitch_mean_deg", 0.0)) / 10.0
    roll_term = abs(orbit_geometry.get("roll_mean_deg", 0.0)) / 40.0
    topography: Grid = []
    for r in range(rows):
        row: list[float] = []
        row_bias = math.sin((r / max(rows - 1, 1)) * math.pi) * pitch_term
        for c in range(cols):
            col_bias = abs(c / max(cols - 1, 1) - 0.5) * roll_term
            row.append(0.55 * crater[r][c] + 0.30 * texture[r][c] + 0.10 * row_bias + 0.05 * col_bias)
        topography.append(row)
    return smooth(normalize(topography), 1)


def derive_illumination_proxy(dem: Grid, orbit_geometry: dict, rim_bias: float) -> Grid:
    rows = len(dem)
    cols = len(dem[0]) if rows else 0
    if rows == 0 or cols == 0:
        return []
    grad = normalize(gradient_magnitude(dem))
    yaw_phase = math.radians(orbit_geometry.get("yaw_mean_deg", 0.0))
    phi_phase = math.radians(orbit_geometry.get("phi_mean_deg", 0.0))
    illum: Grid = []
    for r in range(rows):
        row: list[float] = []
        for c in range(cols):
            rr = r / max(rows - 1, 1)
            cc = c / max(cols - 1, 1)
            rim = abs(rr - 0.5) * 1.2 + abs(cc - 0.5) * 0.8
            directional = 0.5 + 0.25 * math.cos((cc * math.pi) + yaw_phase) + 0.15 * math.sin((rr * math.pi) + phi_phase)
            row.append(rim_bias * rim + 0.35 * directional - 0.25 * grad[r][c])
        illum.append(row)
    return normalize(illum)


def derive_slope_deg(dem: Grid) -> Grid:
    grad = gradient_magnitude(dem)
    return normalize([[min(30.0, value * 6.5) / 30.0 for value in row] for row in grad])


def boulder_hazard(texture: Grid, slope: Grid) -> Grid:
    return normalize([[0.65 * texture[r][c] + 0.35 * slope[r][c] for c in range(len(texture[0]))] for r in range(len(texture))])
