from __future__ import annotations

import math

from src.common.grid import Grid, normalize


def derive_cpr(hh: Grid, hv: Grid, vh: Grid, vv: Grid) -> Grid:
    rows = len(hh)
    cols = len(hh[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            opposite = hv[r][c] + vh[r][c] + 1e-6
            same = hh[r][c] + vv[r][c] + 1e-6
            out[r][c] = opposite / same
    return normalize(out)


def derive_dop(hh: Grid, hv: Grid, vh: Grid, vv: Grid) -> Grid:
    rows = len(hh)
    cols = len(hh[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            s0 = hh[r][c] + hv[r][c] + vh[r][c] + vv[r][c] + 1e-6
            s1 = hh[r][c] - vv[r][c]
            s2 = hv[r][c] - vh[r][c]
            s3 = hh[r][c] + vv[r][c] - hv[r][c] - vh[r][c]
            out[r][c] = min(1.0, math.sqrt(s1 * s1 + s2 * s2 + s3 * s3) / s0)
    return normalize(out)


def derive_entropy_alpha(hh: Grid, hv: Grid, vh: Grid, vv: Grid) -> tuple[Grid, Grid]:
    rows = len(hh)
    cols = len(hh[0]) if rows else 0
    entropy: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    alpha: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            components = [hh[r][c] + 1e-6, hv[r][c] + 1e-6, vh[r][c] + 1e-6, vv[r][c] + 1e-6]
            total = sum(components)
            probs = [value / total for value in components]
            entropy[r][c] = -sum(p * math.log(p, 4) for p in probs)
            alpha[r][c] = math.degrees(math.atan2(hv[r][c] + vh[r][c], hh[r][c] + vv[r][c] + 1e-6)) / 90.0
    return normalize(entropy), normalize(alpha)
