from __future__ import annotations

from src.common.grid import Grid, gradient_magnitude, normalize, percentile


def detect_morphology(dem: Grid, texture: Grid) -> Grid:
    rim = normalize(gradient_magnitude(dem))
    rows = len(dem)
    cols = len(dem[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            out[r][c] = min(1.0, 0.55 * rim[r][c] + 0.45 * texture[r][c])
    return out


def false_positive_rate(morphology: Grid, control_region_fraction: float = 0.18) -> float:
    rows = len(morphology)
    cols = len(morphology[0]) if rows else 0
    threshold = percentile(morphology, 0.78)
    positives = 0
    control_count = 0
    control_rows = max(1, int(rows * control_region_fraction))
    for r in range(control_rows):
        for c in range(cols):
            control_count += 1
            if morphology[r][c] >= threshold:
                positives += 1
    return positives / max(control_count, 1)
