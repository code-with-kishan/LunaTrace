from __future__ import annotations

from src.common.grid import Grid


def build_prediction_grid() -> list[dict]:
    grid: list[dict] = []
    roughness_values = [0.02 * idx for idx in range(1, 16)]
    ice_values = [0.05 * idx for idx in range(0, 17)]
    for roughness in roughness_values:
        for ice_fraction in ice_values:
            dielectric = 2.3 + 1.4 * ice_fraction
            cpr_pred = min(1.0, 0.22 + 0.95 * ice_fraction + 0.35 * roughness + 0.08 * dielectric)
            dop_pred = max(0.0, 0.58 - 0.42 * ice_fraction + 0.18 * roughness)
            entropy_pred = min(1.0, 0.30 + 0.25 * roughness + 0.16 * ice_fraction)
            grid.append(
                {
                    "roughness": roughness,
                    "ice_fraction": ice_fraction,
                    "dielectric": dielectric,
                    "cpr_pred": cpr_pred,
                    "dop_pred": dop_pred,
                    "entropy_pred": entropy_pred,
                }
            )
    return grid


def invert_ice_fraction(cpr: Grid, dop: Grid, entropy: Grid, prediction_grid: list[dict]) -> tuple[Grid, Grid]:
    rows = len(cpr)
    cols = len(cpr[0]) if rows else 0
    ice_fraction: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    roughness: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            best = None
            best_cost = float("inf")
            for candidate in prediction_grid:
                cost = (
                    abs(candidate["cpr_pred"] - cpr[r][c]) * 1.5
                    + abs(candidate["dop_pred"] - dop[r][c])
                    + abs(candidate["entropy_pred"] - entropy[r][c]) * 0.8
                )
                if cost < best_cost:
                    best_cost = cost
                    best = candidate
            ice_fraction[r][c] = best["ice_fraction"] if best else 0.0
            roughness[r][c] = best["roughness"] if best else 0.0
    return ice_fraction, roughness
