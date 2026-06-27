from __future__ import annotations

from src.common.grid import Grid, logistic


def compute_posterior(
    cpr: Grid,
    dop: Grid,
    entropy: Grid,
    dual_band: Grid,
    morphology: Grid,
) -> Grid:
    rows = len(cpr)
    cols = len(cpr[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            score = (
                2.6 * (cpr[r][c] - 0.5)
                - 1.4 * (dop[r][c] - 0.35)
                + 1.1 * (entropy[r][c] - 0.45)
                + 1.6 * dual_band[r][c]
                + 0.9 * morphology[r][c]
            )
            out[r][c] = logistic(score)
    return out


def compute_posterior_without_entropy(
    cpr: Grid,
    dop: Grid,
    dual_band: Grid,
    morphology: Grid,
) -> Grid:
    rows = len(cpr)
    cols = len(cpr[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            score = (
                2.6 * (cpr[r][c] - 0.5)
                - 1.4 * (dop[r][c] - 0.35)
                + 1.6 * dual_band[r][c]
                + 0.9 * morphology[r][c]
            )
            out[r][c] = logistic(score)
    return out
