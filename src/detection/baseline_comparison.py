from __future__ import annotations

from src.common.grid import Grid


def baseline_threshold(cpr: Grid, dop: Grid) -> Grid:
    rows = len(cpr)
    cols = len(cpr[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            out[r][c] = 1.0 if cpr[r][c] > 0.55 and dop[r][c] < 0.45 else 0.0
    return out


def disagreement_map(baseline: Grid, posterior: Grid) -> Grid:
    rows = len(baseline)
    cols = len(baseline[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            posterior_binary = 1.0 if posterior[r][c] >= 0.5 else 0.0
            out[r][c] = abs(baseline[r][c] - posterior_binary)
    return out
