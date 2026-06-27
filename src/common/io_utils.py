from __future__ import annotations

from pathlib import Path
import json
import pickle
import math

from .grid import Grid, normalize


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_pickle(path: Path, payload) -> None:
    ensure_dir(path.parent)
    with path.open("wb") as handle:
        pickle.dump(payload, handle)


def load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def save_grid_csv(path: Path, grid: Grid) -> None:
    ensure_dir(path.parent)
    lines = [",".join(f"{value:.6f}" for value in row) for row in grid]
    path.write_text("\n".join(lines), encoding="utf-8")


def save_ppm(path: Path, red: Grid, green: Grid | None = None, blue: Grid | None = None) -> None:
    ensure_dir(path.parent)
    if green is None:
        green = red
    if blue is None:
        blue = red
    red_n = normalize(red)
    green_n = normalize(green)
    blue_n = normalize(blue)
    rows = len(red_n)
    cols = len(red_n[0]) if rows else 0
    content = [f"P3\n{cols} {rows}\n255"]
    for r in range(rows):
        pixels: list[str] = []
        for c in range(cols):
            pixels.append(
                f"{int(red_n[r][c] * 255)} {int(green_n[r][c] * 255)} {int(blue_n[r][c] * 255)}"
            )
        content.append(" ".join(pixels))
    path.write_text("\n".join(content), encoding="utf-8")


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _blend(a: str, b: str, t: float) -> str:
    ar, ag, ab = _hex_to_rgb(a)
    br, bg, bb = _hex_to_rgb(b)
    rgb = (
        int(ar + (br - ar) * t),
        int(ag + (bg - ag) * t),
        int(ab + (bb - ab) * t),
    )
    return _rgb_to_hex(rgb)


def _palette(value: float, stops: list[str] | None = None) -> str:
    if stops is None:
        stops = ["#081f33", "#126782", "#55a630", "#ffd166", "#ef476f"]
    value = max(0.0, min(1.0, value))
    if value >= 1.0:
        return stops[-1]
    segment = value * (len(stops) - 1)
    idx = int(segment)
    frac = segment - idx
    return _blend(stops[idx], stops[min(idx + 1, len(stops) - 1)], frac)


def save_heatmap_svg(
    path: Path,
    grid: Grid,
    title: str,
    subtitle: str = "",
    palette: list[str] | None = None,
    points: list[dict] | None = None,
    path_points: list[tuple[int, int]] | None = None,
    labels: list[str] | None = None,
    footer: str = "",
) -> None:
    ensure_dir(path.parent)
    norm = normalize(grid)
    rows = len(norm)
    cols = len(norm[0]) if rows else 0
    cell = 12
    left = 48
    top = 96
    width = left + cols * cell + 180
    height = top + rows * cell + 100
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#06121f"/>',
        f'<text x="{left}" y="34" fill="#f8fafc" font-size="22" font-family="Arial" font-weight="700">{title}</text>',
        f'<text x="{left}" y="58" fill="#93c5fd" font-size="12" font-family="Arial">{subtitle}</text>',
        f'<rect x="{left-2}" y="{top-2}" width="{cols*cell+4}" height="{rows*cell+4}" rx="10" fill="#0b1b2c" stroke="#334155"/>',
    ]
    for r in range(rows):
        for c in range(cols):
            color = _palette(norm[r][c], palette)
            svg.append(
                f'<rect x="{left + c*cell}" y="{top + r*cell}" width="{cell}" height="{cell}" fill="{color}"/>'
            )
    if path_points:
        coords = " ".join(
            f"{left + c*cell + cell/2},{top + r*cell + cell/2}" for r, c in path_points
        )
        svg.append(f'<polyline points="{coords}" fill="none" stroke="#f8fafc" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    if points:
        for point in points:
            px = left + point["col"] * cell + cell / 2
            py = top + point["row"] * cell + cell / 2
            color = point.get("color", "#ffffff")
            label = point.get("label", "")
            svg.append(f'<circle cx="{px}" cy="{py}" r="6" fill="{color}" stroke="#020617" stroke-width="2"/>')
            if label:
                svg.append(f'<text x="{px + 10}" y="{py + 4}" fill="#f8fafc" font-size="11" font-family="Arial">{label}</text>')
    legend_x = left + cols * cell + 36
    legend_y = top
    svg.append(f'<text x="{legend_x}" y="{legend_y-16}" fill="#e2e8f0" font-size="12" font-family="Arial">Relative intensity</text>')
    for i in range(100):
        y = legend_y + i * 2
        color = _palette(1.0 - i / 99.0, palette)
        svg.append(f'<rect x="{legend_x}" y="{y}" width="18" height="2" fill="{color}"/>')
    svg.extend(
        [
            f'<text x="{legend_x+28}" y="{legend_y+10}" fill="#f8fafc" font-size="11" font-family="Arial">High</text>',
            f'<text x="{legend_x+28}" y="{legend_y+198}" fill="#94a3b8" font-size="11" font-family="Arial">Low</text>',
        ]
    )
    if labels:
        label_y = legend_y + 236
        svg.append(f'<text x="{legend_x}" y="{label_y}" fill="#e2e8f0" font-size="12" font-family="Arial">Notes</text>')
        for idx, label in enumerate(labels, start=1):
            svg.append(f'<text x="{legend_x}" y="{label_y + idx*16}" fill="#94a3b8" font-size="11" font-family="Arial">{label}</text>')
    if footer:
        svg.append(f'<text x="{left}" y="{height-20}" fill="#94a3b8" font-size="11" font-family="Arial">{footer}</text>')
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")


def save_split_comparison_svg(
    path: Path,
    left_grid: Grid,
    right_grid: Grid,
    title: str,
    left_label: str,
    right_label: str,
    subtitle: str = "",
) -> None:
    ensure_dir(path.parent)
    left_norm = normalize(left_grid)
    right_norm = normalize(right_grid)
    rows = len(left_norm)
    cols = len(left_norm[0]) if rows else 0
    cell = 10
    margin = 42
    gap = 32
    panel_w = cols * cell
    width = margin * 2 + panel_w * 2 + gap
    height = 96 + rows * cell + 48
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#06121f"/>',
        f'<text x="{margin}" y="34" fill="#f8fafc" font-size="22" font-family="Arial" font-weight="700">{title}</text>',
        f'<text x="{margin}" y="58" fill="#93c5fd" font-size="12" font-family="Arial">{subtitle}</text>',
        f'<text x="{margin}" y="82" fill="#e2e8f0" font-size="13" font-family="Arial">{left_label}</text>',
        f'<text x="{margin + panel_w + gap}" y="82" fill="#e2e8f0" font-size="13" font-family="Arial">{right_label}</text>',
    ]
    top = 94
    for r in range(rows):
        for c in range(cols):
            svg.append(f'<rect x="{margin + c*cell}" y="{top + r*cell}" width="{cell}" height="{cell}" fill="{_palette(left_norm[r][c], ["#0b132b","#1c2541","#3a506b","#5bc0be","#f4d35e"])}"/>')
            svg.append(f'<rect x="{margin + panel_w + gap + c*cell}" y="{top + r*cell}" width="{cell}" height="{cell}" fill="{_palette(right_norm[r][c], ["#0b132b","#1c2541","#3a506b","#5bc0be","#ee6c4d"])}"/>')
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")


def write_phase_report(
    report_dir: Path,
    phase_name: str,
    status: str,
    summary: str,
    completed: list[str],
    pending: list[str],
    blockers: list[str],
) -> None:
    ensure_dir(report_dir)
    pending_lines = [f"- {item}" for item in pending] if pending else ["- None"]
    blocker_lines = [f"- {item}" for item in blockers] if blockers else ["- None"]
    phase_report = "\n".join(
        [
            f"# {phase_name} Report",
            "",
            f"**Status:** {status}",
            "",
            summary,
            "",
            "## Completed modules list",
            "",
            *[f"- {item}" for item in completed],
            "",
            "## Pending tasks",
            "",
            *pending_lines,
            "",
            "## Blockers",
            "",
            *blocker_lines,
            "",
        ]
    )
    (report_dir / "phase_report.md").write_text(phase_report, encoding="utf-8")
    (report_dir / "completed_modules.md").write_text(
        "# Completed Modules\n\n" + "\n".join(f"- {item}" for item in completed) + "\n",
        encoding="utf-8",
    )
    pending_text = "# Pending Tasks\n\n" + ("\n".join(f"- {item}" for item in pending) if pending else "- None") + "\n"
    blockers_text = "# Blockers\n\n" + ("\n".join(f"- {item}" for item in blockers) if blockers else "- None") + "\n"
    (report_dir / "pending_tasks.md").write_text(pending_text, encoding="utf-8")
    (report_dir / "blockers.md").write_text(blockers_text, encoding="utf-8")
