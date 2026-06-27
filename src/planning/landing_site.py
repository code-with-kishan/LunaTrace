from __future__ import annotations

from src.common.grid import Grid


def rank_candidate_sites(
    slope: Grid,
    boulder: Grid,
    illumination: Grid,
    ice_distance: Grid,
    weights: dict,
) -> list[dict]:
    rows = len(slope)
    cols = len(slope[0]) if rows else 0
    ranked: list[dict] = []
    max_distance = max(value for row in ice_distance for value in row) or 1.0
    edge_margin = max(2, min(rows, cols) // 12)
    for r in range(rows):
        for c in range(cols):
            if (
                slope[r][c] > 0.6
                or boulder[r][c] > 0.7
                or illumination[r][c] < 0.2
                or r < edge_margin
                or c < edge_margin
                or r >= rows - edge_margin
                or c >= cols - edge_margin
            ):
                continue
            edge_clearance = min(r, c, rows - 1 - r, cols - 1 - c) / max(min(rows, cols) / 2.0, 1.0)
            score = (
                weights["illumination_safety"] * illumination[r][c]
                + weights["slope_safety"] * (1.0 - slope[r][c])
                + weights["boulder_safety"] * (1.0 - boulder[r][c])
                + weights["ice_proximity"] * (1.0 - ice_distance[r][c] / max_distance)
            )
            score *= 0.85 + 0.15 * edge_clearance
            ranked.append({"row": r, "col": c, "score": score})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    selected: list[dict] = []
    min_spacing = max(4, min(rows, cols) // 7)
    for candidate in ranked:
        if any(abs(candidate["row"] - item["row"]) + abs(candidate["col"] - item["col"]) < min_spacing for item in selected):
            continue
        site = dict(candidate)
        site["site"] = f"LS-{len(selected) + 1}"
        selected.append(site)
        if len(selected) == 6:
            break
    if selected:
        return selected
    fallback = [(rows // 5, cols // 2), (rows // 4, cols // 3), (rows // 4, (2 * cols) // 3)]
    for idx, (r, c) in enumerate(fallback, start=1):
        score = (
            weights["illumination_safety"] * illumination[r][c]
            + weights["slope_safety"] * (1.0 - slope[r][c])
            + weights["boulder_safety"] * (1.0 - boulder[r][c])
            + weights["ice_proximity"] * (1.0 - ice_distance[r][c] / max_distance)
        )
        selected.append({"site": f"LS-{idx}", "row": r, "col": c, "score": score})
    selected.sort(key=lambda item: item["score"], reverse=True)
    return selected
