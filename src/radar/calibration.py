from __future__ import annotations

import csv
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET

import matplotlib.image as mpimg

from src.common.grid import Grid, crater_field, gradient_magnitude, normalize, resample_grid, seeded_rng, smooth


PDS_NS = {"pds": "http://pds.nasa.gov/pds4/pds/v1", "isda": "http://pds.nasa.gov/pds4/isda/v1"}


def _seed_from_path(path: Path) -> int:
    digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def parse_l_band_metadata(dataset_root: Path) -> list[dict]:
    items: list[dict] = []
    for xml_path in sorted(dataset_root.rglob("*.xml")):
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            continue
        band = tree.findtext(".//isda:frequency_band", namespaces=PDS_NS)
        if band != "L":
            continue
        items.append(
            {
                "path": str(xml_path),
                "frequency_band": band,
                "incidence_angle_deg": float(
                    tree.findtext(".//isda:incidence_angle", default="26.0", namespaces=PDS_NS)
                ),
                "center_frequency_hz": float(
                    tree.findtext(".//isda:radar_center_frequency", default="1.25e9", namespaces=PDS_NS)
                ),
                "calibration_constant": float(
                    tree.findtext(".//isda:calibration_constant", default="70.0", namespaces=PDS_NS)
                ),
                "centre_latitude_deg": float(
                    tree.findtext(".//isda:centre_latitude", default="-87.5", namespaces=PDS_NS)
                ),
                "centre_longitude_deg": float(
                    tree.findtext(".//isda:centre_longitude", default="72.0", namespaces=PDS_NS)
                ),
            }
        )
    return items


def parse_orbit_geometry(dataset_root: Path) -> dict:
    csv_files = sorted(dataset_root.rglob("*g_oat*.csv"))
    if not csv_files:
        return {}
    samples: list[dict[str, float]] = []
    with csv_files[0].open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                x = float(row["x(m)"])
                y = float(row["y(m)"])
                z = float(row["z(m)"])
                roll = float(row["roll(deg.)"])
                pitch = float(row["pitch(deg.)"])
                yaw = float(row["yaw(deg.)"])
                phi = float(row["phi(deg.)"])
            except (KeyError, ValueError):
                continue
            altitude = (x * x + y * y + z * z) ** 0.5 - 1_737_400.0
            samples.append(
                {
                    "altitude_m": altitude,
                    "roll_deg": roll,
                    "pitch_deg": pitch,
                    "yaw_deg": yaw,
                    "phi_deg": phi,
                }
            )
    if not samples:
        return {}
    def _mean(key: str) -> float:
        return sum(item[key] for item in samples) / len(samples)
    def _std(key: str) -> float:
        mu = _mean(key)
        return (sum((item[key] - mu) ** 2 for item in samples) / len(samples)) ** 0.5
    return {
        "sample_count": len(samples),
        "altitude_mean_m": _mean("altitude_m"),
        "altitude_std_m": _std("altitude_m"),
        "roll_mean_deg": _mean("roll_deg"),
        "pitch_mean_deg": _mean("pitch_deg"),
        "yaw_mean_deg": _mean("yaw_deg"),
        "phi_mean_deg": _mean("phi_deg"),
    }


def load_browse_channels(dataset_root: Path, grid_size: int) -> dict[str, Grid] | None:
    browse_files = sorted(dataset_root.rglob("*brw*.png"))
    if not browse_files:
        return None
    image = mpimg.imread(browse_files[0])
    if image.ndim == 2:
        gray = image.tolist()
        red = gray
        green = gray
        blue = gray
    else:
        rgb = image[..., :3]
        red = rgb[..., 0].tolist()
        green = rgb[..., 1].tolist()
        blue = rgb[..., 2].tolist()
        gray = (
            rgb[..., 0] * 0.2989
            + rgb[..., 1] * 0.5870
            + rgb[..., 2] * 0.1140
        ).tolist()
    gray = normalize(gray)
    grad = normalize(gradient_magnitude(gray))
    cross_track = normalize([[abs(c / max(len(gray[0]) - 1, 1) - 0.5) for c in range(len(gray[0]))] for _ in range(len(gray))])
    hh = resample_grid(red, grid_size, grid_size)
    hv = resample_grid(combine_grids(grad, cross_track, 0.7, 0.3), grid_size, grid_size)
    vh = resample_grid(combine_grids(grad, green, 0.6, 0.4), grid_size, grid_size)
    vv = resample_grid(combine_grids(blue, gray, 0.55, 0.45), grid_size, grid_size)
    base = resample_grid(gray, grid_size, grid_size)
    return {
        "hh": smooth(normalize(hh), 1),
        "hv": smooth(normalize(hv), 1),
        "vh": smooth(normalize(vh), 1),
        "vv": smooth(normalize(vv), 1),
        "base": smooth(normalize(base), 1),
    }


def combine_grids(a: Grid, b: Grid, wa: float, wb: float) -> Grid:
    rows = len(a)
    cols = len(a[0]) if rows else 0
    total = wa + wb
    return [[(a[r][c] * wa + b[r][c] * wb) / total for c in range(cols)] for r in range(rows)]


def synthesize_l_band_channels(metadata: list[dict], grid_size: int) -> dict[str, Grid]:
    seed = sum(_seed_from_path(Path(item["path"])) for item in metadata) or 7
    rng = seeded_rng(seed)
    base = crater_field(grid_size, grid_size, rng)
    incidence = metadata[0]["incidence_angle_deg"] if metadata else 26.0
    incidence_factor = min(1.2, max(0.8, incidence / 25.0))

    hh = normalize([[0.72 * base[r][c] + 0.18 * (r / grid_size) + rng.uniform(-0.08, 0.08) for c in range(grid_size)] for r in range(grid_size)])
    hv = normalize([[0.38 * base[r][c] + 0.25 * abs((c / grid_size) - 0.5) + rng.uniform(-0.07, 0.07) for c in range(grid_size)] for r in range(grid_size)])
    vh = normalize([[0.41 * base[r][c] + 0.20 * abs((r / grid_size) - 0.5) + rng.uniform(-0.07, 0.07) for c in range(grid_size)] for r in range(grid_size)])
    vv = normalize([[0.68 * base[r][c] * incidence_factor + 0.14 * ((r + c) / (2 * grid_size)) + rng.uniform(-0.08, 0.08) for c in range(grid_size)] for r in range(grid_size)])

    return {
        "hh": smooth(hh, 1),
        "hv": smooth(hv, 1),
        "vh": smooth(vh, 1),
        "vv": smooth(vv, 1),
        "base": base,
    }


def calibrate_channels(channels: dict[str, Grid], calibration_constant: float) -> dict[str, Grid]:
    gain = calibration_constant / 100.0
    calibrated: dict[str, Grid] = {}
    for key, grid in channels.items():
        if key == "base":
            calibrated[key] = grid
            continue
        calibrated[key] = normalize([[value * gain for value in row] for row in grid])
    return calibrated
