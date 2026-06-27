from __future__ import annotations

import math

from src.common.grid import Grid


LIGHT_SPEED = 299_792_458.0


def penetration_depth(frequency_hz: float, dielectric_constant: float, loss_tangent: float) -> float:
    wavelength = LIGHT_SPEED / frequency_hz
    attenuation = math.pi * max(loss_tangent, 1e-6) * math.sqrt(max(dielectric_constant, 1e-6))
    return wavelength / max(attenuation, 1e-9)


def classify_dual_band(l_cpr: Grid, s_cpr: Grid, l_depth_m: float, s_depth_m: float) -> Grid:
    rows = len(l_cpr)
    cols = len(l_cpr[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    depth_bonus = 0.2 if l_depth_m > s_depth_m else 0.0
    for r in range(rows):
        for c in range(cols):
            l_high = l_cpr[r][c] > 0.58
            s_high = s_cpr[r][c] > 0.58
            if l_high and not s_high:
                out[r][c] = 1.0 + depth_bonus
            elif l_high and s_high:
                out[r][c] = 0.66
            elif s_high and not l_high:
                out[r][c] = 0.33
            else:
                out[r][c] = 0.0
    return out
