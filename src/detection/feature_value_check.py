from __future__ import annotations

from src.common.grid import Grid, mean


def feature_information_value(feature: Grid, posterior: Grid) -> float:
    rows = len(feature)
    cols = len(feature[0]) if rows else 0
    high_feature = []
    low_feature = []
    for r in range(rows):
        for c in range(cols):
            if feature[r][c] >= 0.5:
                high_feature.append(posterior[r][c])
            else:
                low_feature.append(posterior[r][c])
    if not high_feature or not low_feature:
        return 0.0
    return abs(sum(high_feature) / len(high_feature) - sum(low_feature) / len(low_feature))


def posterior_delta_metric(with_entropy: Grid, without_entropy: Grid) -> float:
    rows = len(with_entropy)
    cols = len(with_entropy[0]) if rows else 0
    total = 0.0
    count = 0
    for r in range(rows):
        for c in range(cols):
            total += abs(with_entropy[r][c] - without_entropy[r][c])
            count += 1
    return total / max(count, 1)
