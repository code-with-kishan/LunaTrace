from __future__ import annotations

import heapq
import math

from src.common.grid import Grid


def _neighbors(r: int, c: int, rows: int, cols: int):
    for rr, cc in (
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
        (r - 1, c - 1),
        (r - 1, c + 1),
        (r + 1, c - 1),
        (r + 1, c + 1),
    ):
        if 0 <= rr < rows and 0 <= cc < cols:
            yield rr, cc


def astar_path(
    start: tuple[int, int],
    goal: tuple[int, int],
    slope_cost: Grid,
    boulder_cost: Grid,
    illumination_cost: Grid,
    comms_cost: Grid,
    slip_cost: Grid,
    thermal_limit_steps: int,
) -> dict:
    rows = len(slope_cost)
    cols = len(slope_cost[0]) if rows else 0
    queue = [(0.0, 0, start)]
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    g_score = {start: 0.0}
    steps_taken = {start: 0}
    best_candidate = start
    best_distance = abs(goal[0] - start[0]) + abs(goal[1] - start[1])

    while queue:
        _, _, current = heapq.heappop(queue)
        distance = abs(goal[0] - current[0]) + abs(goal[1] - current[1])
        if distance < best_distance:
            best_distance = distance
            best_candidate = current
        if current == goal:
            break
        current_steps = steps_taken[current]
        if current_steps > thermal_limit_steps:
            continue
        for nxt in _neighbors(current[0], current[1], rows, cols):
            move_cost = math.sqrt(2.0) if nxt[0] != current[0] and nxt[1] != current[1] else 1.0
            cost = (
                move_cost
                + 2.4 * slope_cost[nxt[0]][nxt[1]]
                + 1.8 * boulder_cost[nxt[0]][nxt[1]]
                + 1.2 * illumination_cost[nxt[0]][nxt[1]]
                + 0.8 * comms_cost[nxt[0]][nxt[1]]
                + 1.4 * slip_cost[nxt[0]][nxt[1]]
            )
            tentative = g_score[current] + cost
            if tentative < g_score.get(nxt, float("inf")):
                g_score[nxt] = tentative
                steps_taken[nxt] = current_steps + 1
                heuristic = math.hypot(goal[0] - nxt[0], goal[1] - nxt[1])
                heapq.heappush(queue, (tentative + heuristic, current_steps + 1, nxt))
                came_from[nxt] = current

    if goal not in came_from:
        excess_steps = max(0, steps_taken.get(best_candidate, thermal_limit_steps) - thermal_limit_steps)
        return {
            "status": "infeasible",
            "binding_constraint": "thermal survival limit",
            "path": [],
            "total_cost": None,
            "closest_feasible_gap_steps": best_distance,
            "thermal_excess_steps": excess_steps,
            "staged_traverse_note": "Consider an intermediate sunlit rest stop before entering the deepest shadowed zone.",
        }

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return {
        "status": "feasible",
        "binding_constraint": "none",
        "path": path,
        "total_cost": g_score[goal],
        "steps": len(path),
    }
