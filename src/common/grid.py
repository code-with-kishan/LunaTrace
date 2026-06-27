from __future__ import annotations

import math
import random


Grid = list[list[float]]


def seeded_rng(seed: int) -> random.Random:
    return random.Random(seed)


def zeros(rows: int, cols: int, value: float = 0.0) -> Grid:
    return [[value for _ in range(cols)] for _ in range(rows)]


def shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0]) if grid else 0


def normalize(grid: Grid) -> Grid:
    flat = [value for row in grid for value in row]
    minimum = min(flat)
    maximum = max(flat)
    if maximum - minimum < 1e-12:
        return zeros(len(grid), len(grid[0]), 0.0)
    return [[(value - minimum) / (maximum - minimum) for value in row] for row in grid]


def combine(*grids: Grid, weights: list[float] | None = None) -> Grid:
    if not grids:
        return []
    rows, cols = shape(grids[0])
    if weights is None:
        weights = [1.0] * len(grids)
    total = sum(weights) or 1.0
    out = zeros(rows, cols)
    for r in range(rows):
        for c in range(cols):
            out[r][c] = sum(grid[r][c] * w for grid, w in zip(grids, weights)) / total
    return out


def smooth(grid: Grid, radius: int = 1) -> Grid:
    rows, cols = shape(grid)
    out = zeros(rows, cols)
    for r in range(rows):
        for c in range(cols):
            total = 0.0
            count = 0
            for rr in range(max(0, r - radius), min(rows, r + radius + 1)):
                for cc in range(max(0, c - radius), min(cols, c + radius + 1)):
                    total += grid[rr][cc]
                    count += 1
            out[r][c] = total / max(count, 1)
    return out


def map_grid(grid: Grid, fn) -> Grid:
    return [[fn(value, r, c) for c, value in enumerate(row)] for r, row in enumerate(grid)]


def add_noise(grid: Grid, rng: random.Random, amplitude: float) -> Grid:
    return [[value + rng.uniform(-amplitude, amplitude) for value in row] for row in grid]


def subtract(a: Grid, b: Grid) -> Grid:
    rows, cols = shape(a)
    return [[a[r][c] - b[r][c] for c in range(cols)] for r in range(rows)]


def gradient_magnitude(grid: Grid) -> Grid:
    rows, cols = shape(grid)
    out = zeros(rows, cols)
    for r in range(rows):
        for c in range(cols):
            left = grid[r][max(c - 1, 0)]
            right = grid[r][min(c + 1, cols - 1)]
            up = grid[max(r - 1, 0)][c]
            down = grid[min(r + 1, rows - 1)][c]
            dx = (right - left) * 0.5
            dy = (down - up) * 0.5
            out[r][c] = math.sqrt(dx * dx + dy * dy)
    return out


def percentile(grid: Grid, q: float) -> float:
    flat = sorted(value for row in grid for value in row)
    if not flat:
        return 0.0
    index = min(len(flat) - 1, max(0, int(q * (len(flat) - 1))))
    return flat[index]


def mean(grid: Grid) -> float:
    flat = [value for row in grid for value in row]
    return sum(flat) / max(len(flat), 1)


def stddev(grid: Grid) -> float:
    mu = mean(grid)
    flat = [value for row in grid for value in row]
    return math.sqrt(sum((value - mu) ** 2 for value in flat) / max(len(flat), 1))


def crater_field(rows: int, cols: int, rng: random.Random) -> Grid:
    out = zeros(rows, cols)
    center_r = rows / 2.0
    center_c = cols / 2.0
    for r in range(rows):
        for c in range(cols):
            dr = (r - center_r) / rows
            dc = (c - center_c) / cols
            radius = math.sqrt(dr * dr + dc * dc)
            bowl = math.exp(-(radius * 4.2) ** 2)
            rim = math.exp(-((radius - 0.28) / 0.05) ** 2)
            lobes = 0.18 * math.sin(8.0 * math.atan2(dr + 1e-6, dc + 1e-6))
            out[r][c] = 0.65 * bowl + 0.35 * rim + lobes + rng.uniform(-0.06, 0.06)
    return normalize(smooth(out, 1))


def threshold_mask(grid: Grid, threshold: float) -> list[list[int]]:
    return [[1 if value >= threshold else 0 for value in row] for row in grid]


def distance_to_mask(mask: list[list[int]]) -> Grid:
    rows = len(mask)
    cols = len(mask[0]) if rows else 0
    points = [(r, c) for r in range(rows) for c in range(cols) if mask[r][c]]
    out = zeros(rows, cols)
    for r in range(rows):
        for c in range(cols):
            if mask[r][c]:
                out[r][c] = 0.0
                continue
            if not points:
                out[r][c] = float(rows + cols)
                continue
            out[r][c] = min(abs(pr - r) + abs(pc - c) for pr, pc in points)
    return out


def logistic(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def resample_grid(grid: Grid, out_rows: int, out_cols: int) -> Grid:
    rows, cols = shape(grid)
    if rows == 0 or cols == 0 or out_rows <= 0 or out_cols <= 0:
        return zeros(out_rows, out_cols)
    out = zeros(out_rows, out_cols)
    for r in range(out_rows):
        row_start = int(r * rows / out_rows)
        row_end = max(row_start + 1, int((r + 1) * rows / out_rows))
        for c in range(out_cols):
            col_start = int(c * cols / out_cols)
            col_end = max(col_start + 1, int((c + 1) * cols / out_cols))
            total = 0.0
            count = 0
            for rr in range(row_start, min(row_end, rows)):
                for cc in range(col_start, min(col_end, cols)):
                    total += grid[rr][cc]
                    count += 1
            out[r][c] = total / max(count, 1)
    return out


def connected_components(mask: list[list[int]]) -> list[list[tuple[int, int]]]:
    rows = len(mask)
    cols = len(mask[0]) if rows else 0
    seen: set[tuple[int, int]] = set()
    components: list[list[tuple[int, int]]] = []
    for r in range(rows):
        for c in range(cols):
            if not mask[r][c] or (r, c) in seen:
                continue
            stack = [(r, c)]
            seen.add((r, c))
            component: list[tuple[int, int]] = []
            while stack:
                rr, cc = stack.pop()
                component.append((rr, cc))
                for nr in range(max(0, rr - 1), min(rows, rr + 2)):
                    for nc in range(max(0, cc - 1), min(cols, cc + 2)):
                        if (nr, nc) == (rr, cc) or not mask[nr][nc] or (nr, nc) in seen:
                            continue
                        seen.add((nr, nc))
                        stack.append((nr, nc))
            components.append(component)
    return components
