from __future__ import annotations

from src.common.grid import Grid, mean, smooth, stddev


def lee_filter(grid: Grid, radius: int = 1, noise_floor: float = 0.08) -> Grid:
    local_mean = smooth(grid, radius)
    local_var = smooth([[value * value for value in row] for row in grid], radius)
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    out: Grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
    global_noise = max(noise_floor, stddev(grid) * 0.25)
    for r in range(rows):
        for c in range(cols):
            variance = max(0.0, local_var[r][c] - local_mean[r][c] ** 2)
            weight = variance / max(variance + global_noise, 1e-9)
            out[r][c] = local_mean[r][c] + weight * (grid[r][c] - local_mean[r][c])
    return out


def filter_radar_stack(stack: dict[str, Grid]) -> dict[str, Grid]:
    return {key: lee_filter(grid, 1) if key != "base" else grid for key, grid in stack.items()}
