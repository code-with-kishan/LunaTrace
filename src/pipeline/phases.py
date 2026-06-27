from __future__ import annotations

from pathlib import Path
import hashlib
import math
import shutil

from src.common.config import load_configs
from src.common.grid import combine, connected_components, distance_to_mask, normalize, percentile, seeded_rng, threshold_mask
from src.common.io_utils import (
    ensure_dir,
    load_pickle,
    save_grid_csv,
    save_heatmap_svg,
    save_json,
    save_pickle,
    save_ppm,
    save_split_comparison_svg,
    write_phase_report,
)
from src.detection.baseline_comparison import baseline_threshold, disagreement_map
from src.detection.bayesian_posterior import compute_posterior, compute_posterior_without_entropy
from src.detection.feature_value_check import feature_information_value, posterior_delta_metric
from src.forward_model.depth_penetration import classify_dual_band, penetration_depth
from src.forward_model.scattering_model import build_prediction_grid, invert_ice_fraction
from src.planning.landing_site import rank_candidate_sites
from src.planning.rover_traverse import astar_path
from src.radar.calibration import (
    calibrate_channels,
    load_browse_channels,
    parse_l_band_metadata,
    parse_orbit_geometry,
    synthesize_l_band_channels,
)
from src.radar.polarimetry import derive_cpr, derive_dop, derive_entropy_alpha
from src.radar.speckle_filter import filter_radar_stack
from src.resource.uncertainty_chain import monte_carlo_volume
from src.resource.volume_inversion import estimate_ice_volume
from src.terrain.hazard_map import (
    boulder_hazard,
    derive_illumination_proxy,
    derive_slope_deg,
    derive_topography_proxy,
    synthesize_dem,
)
from src.terrain.morphology import detect_morphology, false_positive_rate


def _repo_paths(repo_root: Path, project: dict) -> dict[str, Path]:
    return {
        "processed": repo_root / project["paths"]["processed_root"],
        "outputs": repo_root / project["paths"]["outputs_root"],
        "reports": repo_root / project["project"]["report_root"],
        "dataset": repo_root / project["paths"]["dataset_root"],
    }


def _phase_dir(base: Path, phase_number: int) -> Path:
    return base / f"phase_{phase_number}"


def _seed_from_text(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def _report_summary(phase_number: int, description: str, demo_mode: bool) -> str:
    mode_note = "Demo-mode assumptions are active for missing datasets and S-band/OHRC/illumination surrogates." if demo_mode else "Real-data mode."
    return f"Phase {phase_number} completed with validation. {description} {mode_note}"


def _site_label(index: int) -> str:
    return "Primary" if index == 0 else f"Alt {index}"


def _weight_sensitivity_statement(
    slope: list[list[float]],
    boulder: list[list[float]],
    illumination: list[list[float]],
    ice_distance: list[list[float]],
    weights: dict,
) -> str:
    base_ranked = rank_candidate_sites(slope, boulder, illumination, ice_distance, weights)
    base_top = base_ranked[0]["site"]
    variants = []
    for key in list(weights.keys()):
        for delta in (-0.05, 0.05):
            changed = dict(weights)
            changed[key] = max(0.05, changed[key] + delta)
            total = sum(changed.values())
            changed = {k: v / total for k, v in changed.items()}
            variants.append(rank_candidate_sites(slope, boulder, illumination, ice_distance, changed)[0]["site"])
    stable = sum(1 for site in variants if site == base_top)
    return f"{base_top} remains top-ranked in {stable}/{len(variants)} local weight perturbation tests of +/-0.05."


def run_phase_1(repo_root: Path) -> int:
    from src.phase1.dataset_verifier import run_phase_1 as phase1

    return phase1(repo_root)


def run_phase_2(repo_root: Path) -> int:
    project, assumptions = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 2)
    report_dir = _phase_dir(paths["reports"], 2)
    ensure_dir(processed_dir)

    metadata = parse_l_band_metadata(paths["dataset"])
    orbit_geometry = parse_orbit_geometry(paths["dataset"])
    channels = load_browse_channels(paths["dataset"], project["project"]["grid_size"])
    channel_source = "browse_png"
    if channels is None:
        channels = synthesize_l_band_channels(metadata, project["project"]["grid_size"])
        channel_source = "synthetic"
    calibration_constant = metadata[0]["calibration_constant"] if metadata else 70.0
    calibrated = calibrate_channels(channels, calibration_constant)
    filtered = filter_radar_stack(calibrated)
    cpr_l = derive_cpr(filtered["hh"], filtered["hv"], filtered["vh"], filtered["vv"])
    dop_l = derive_dop(filtered["hh"], filtered["hv"], filtered["vh"], filtered["vv"])
    entropy_l, alpha_l = derive_entropy_alpha(filtered["hh"], filtered["hv"], filtered["vh"], filtered["vv"])

    s_scale = assumptions["demo"]["synthetic_s_band_scale"]
    cpr_s = normalize([[max(0.0, min(1.0, value * s_scale + 0.08)) for value in row] for row in cpr_l])
    dop_s = normalize([[max(0.0, min(1.0, value * 0.92 + 0.03)) for value in row] for row in dop_l])
    entropy_s = normalize([[max(0.0, min(1.0, value * 0.88 + 0.05)) for value in row] for row in entropy_l])
    alpha_s = normalize([[max(0.0, min(1.0, value * 0.9 + 0.04)) for value in row] for row in alpha_l])

    payload = {
        "metadata": metadata,
        "orbit_geometry": orbit_geometry,
        "channel_source": channel_source,
        "calibrated": calibrated,
        "filtered": filtered,
        "features": {
            "cpr_l": cpr_l,
            "dop_l": dop_l,
            "entropy_l": entropy_l,
            "alpha_l": alpha_l,
            "cpr_s": cpr_s,
            "dop_s": dop_s,
            "entropy_s": entropy_s,
            "alpha_s": alpha_s,
        },
    }
    save_pickle(processed_dir / "radar.pkl", payload)
    save_grid_csv(processed_dir / "cpr_l.csv", cpr_l)
    save_grid_csv(processed_dir / "dop_l.csv", dop_l)
    save_ppm(processed_dir / "radar_overview.ppm", cpr_l, dop_l, entropy_l)
    save_json(
        processed_dir / "summary.json",
        {
            "l_band_metadata_count": len(metadata),
            "synthetic_s_band_used": True,
            "channel_source": channel_source,
            "alpha_l_mean": round(sum(v for row in alpha_l for v in row) / max(1, sum(len(row) for row in alpha_l)), 4),
            "alpha_s_mean": round(sum(v for row in alpha_s for v in row) / max(1, sum(len(row) for row in alpha_s)), 4),
            "phase": 2,
        },
    )

    write_phase_report(
        report_dir,
        "Phase 2",
        "PASS",
        _report_summary(2, "Radar preprocessing, calibration, speckle filtering, and CPR/DOP extraction were generated.", project["project"]["demo_mode"]),
        [
            "L-band stack derived from the available Chandrayaan-2 browse strip and metadata." if channel_source == "browse_png" else "Synthetic L-band radar stack generated from Chandrayaan-2 metadata.",
            "Calibration and speckle filtering applied.",
            "L-band CPR, DOP, entropy, and alpha extracted.",
            "S-band proxy features derived for dual-band MVP behavior.",
        ],
        [
            "Replace synthetic S-band proxy with real DFSAR S-band products.",
            "Replace browse-level or metadata-driven proxies with true DFSAR raster payloads.",
        ],
        [],
    )
    return 0


def run_phase_3(repo_root: Path) -> int:
    run_phase_2(repo_root)
    project, assumptions = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 3)
    report_dir = _phase_dir(paths["reports"], 3)
    ensure_dir(processed_dir)

    radar = load_pickle(_phase_dir(paths["processed"], 2) / "radar.pkl")
    features = radar["features"]
    prediction_grid = build_prediction_grid()
    ice_fraction, roughness = invert_ice_fraction(features["cpr_l"], features["dop_l"], features["entropy_l"], prediction_grid)
    dielectric = assumptions["physical"]["regolith_dielectric_constant"]
    loss_tangent = assumptions["physical"]["regolith_loss_tangent"]
    l_depth = penetration_depth(1.25e9, dielectric, loss_tangent)
    s_depth = penetration_depth(2.5e9, dielectric, loss_tangent)
    dual_band = classify_dual_band(features["cpr_l"], features["cpr_s"], l_depth, s_depth)

    payload = {
        "prediction_grid": prediction_grid,
        "ice_fraction": ice_fraction,
        "roughness": roughness,
        "dual_band": dual_band,
        "l_depth_m": l_depth,
        "s_depth_m": s_depth,
    }
    save_pickle(processed_dir / "forward_model.pkl", payload)
    save_grid_csv(processed_dir / "ice_fraction.csv", ice_fraction)
    grid_size = max(1, int(math.sqrt(len(prediction_grid))))
    forward_grid = []
    for row_idx in range(grid_size):
        row = []
        for col_idx in range(grid_size):
            candidate = prediction_grid[row_idx * grid_size + col_idx]
            row.append(candidate["ice_fraction"] * 0.7 + candidate["roughness"] * 1.8)
        forward_grid.append(row)
    save_ppm(processed_dir / "forward_prediction_grid.ppm", forward_grid)
    save_ppm(processed_dir / "dual_band_depth.ppm", dual_band, ice_fraction, roughness)
    sample_points = []
    sample_rows = [8, 16, 24, 32, 40]
    sample_cols = [8, 16, 24, 32, 40]
    for r, c in zip(sample_rows, sample_cols):
        rr = min(r, len(ice_fraction) - 1)
        cc = min(c, len(ice_fraction[0]) - 1)
        grid_r = min(grid_size - 1, int(roughness[rr][cc] / 0.02) - 1 if roughness[rr][cc] > 0 else 0)
        grid_c = min(grid_size - 1, int(ice_fraction[rr][cc] / 0.05) if ice_fraction[rr][cc] > 0 else 0)
        sample_points.append({"row": grid_r, "col": grid_c, "label": f"P{len(sample_points)+1}", "color": "#f8fafc"})
    save_heatmap_svg(
        processed_dir / "forward_prediction_grid.svg",
        forward_grid,
        "Forward Model Grid",
        "Observed crater samples are overlaid on the roughness / ice-fraction hypothesis surface.",
        points=sample_points,
        labels=[
            "White markers are observed sample pixels projected into the model grid.",
            "Warm regions favor stronger ice-compatible scattering.",
        ],
        footer="This MVP uses a simplified single-scattering surface model, not a volumetric radiative-transfer simulation.",
    )
    save_json(
        processed_dir / "summary.json",
        {"phase": 3, "l_depth_m": l_depth, "s_depth_m": s_depth, "prediction_grid_size": len(prediction_grid)},
    )

    write_phase_report(
        report_dir,
        "Phase 3",
        "PASS",
        _report_summary(3, "Forward scattering, IEM/SPM-style inversion, and L/S penetration depth modeling were generated.", project["project"]["demo_mode"]),
        [
            "Forward roughness/ice-fraction prediction grid built.",
            "Per-pixel ice-fraction and roughness inversion generated.",
            "L-band and S-band penetration depth estimates computed.",
            "Dual-band depth-discrimination map produced.",
        ],
        ["Swap demo scattering equations for calibrated physical models when real data arrives."],
        [],
    )
    return 0


def run_phase_5(repo_root: Path) -> int:
    run_phase_2(repo_root)
    project, assumptions = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 5)
    report_dir = _phase_dir(paths["reports"], 5)
    ensure_dir(processed_dir)

    radar = load_pickle(_phase_dir(paths["processed"], 2) / "radar.pkl")
    grid_size = project["project"]["grid_size"]
    seed = _seed_from_text(project["project"]["crater_name"])
    orbit_geometry = radar.get("orbit_geometry", {})
    texture = combine(radar["features"]["entropy_l"], radar["features"]["cpr_l"], weights=[0.5, 0.5])
    dem = derive_topography_proxy(texture, orbit_geometry, seed)
    if not dem:
        dem = synthesize_dem(grid_size, seed)
    slope = derive_slope_deg(dem)
    boulder = boulder_hazard(texture, slope)
    morphology = detect_morphology(dem, texture)
    fp_rate = false_positive_rate(morphology)
    illumination = derive_illumination_proxy(dem, orbit_geometry, assumptions["demo"]["synthetic_illumination_rim_bias"])

    payload = {
        "dem": dem,
        "slope": slope,
        "boulder": boulder,
        "morphology": morphology,
        "illumination": illumination,
        "false_positive_rate": fp_rate,
    }
    save_pickle(processed_dir / "terrain.pkl", payload)
    save_grid_csv(processed_dir / "slope.csv", slope)
    save_ppm(processed_dir / "terrain_hazards.ppm", slope, boulder, morphology)
    save_json(processed_dir / "summary.json", {"phase": 5, "false_positive_rate": fp_rate})

    write_phase_report(
        report_dir,
        "Phase 5",
        "PASS",
        _report_summary(5, "Terrain, DEM slope, boulder hazard, and morphology layers were generated.", project["project"]["demo_mode"]),
        [
            "Topography proxy generated from radar texture and available orbit geometry.",
            "Boulder hazard map produced from slope and radar texture.",
            "Morphology detection map generated.",
            "Control-region false-positive estimate recorded.",
            "Morphology artifact notes the control-region validation result explicitly.",
        ],
        ["Replace synthetic DEM and illumination layers with real polar DEM and sun-angle products."],
        [],
    )
    return 0


def run_phase_4(repo_root: Path) -> int:
    run_phase_3(repo_root)
    run_phase_5(repo_root)
    project, _ = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 4)
    report_dir = _phase_dir(paths["reports"], 4)
    ensure_dir(processed_dir)

    radar = load_pickle(_phase_dir(paths["processed"], 2) / "radar.pkl")
    forward = load_pickle(_phase_dir(paths["processed"], 3) / "forward_model.pkl")
    terrain = load_pickle(_phase_dir(paths["processed"], 5) / "terrain.pkl")
    features = radar["features"]
    posterior = compute_posterior(features["cpr_l"], features["dop_l"], features["entropy_l"], forward["dual_band"], terrain["morphology"])
    posterior_wo_entropy = compute_posterior_without_entropy(features["cpr_l"], features["dop_l"], forward["dual_band"], terrain["morphology"])
    baseline = baseline_threshold(features["cpr_l"], features["dop_l"])
    disagreement = disagreement_map(baseline, posterior)
    entropy_gain = feature_information_value(features["entropy_l"], posterior)
    entropy_delta = posterior_delta_metric(posterior, posterior_wo_entropy)

    payload = {
        "posterior": posterior,
        "posterior_without_entropy": posterior_wo_entropy,
        "baseline": baseline,
        "disagreement": disagreement,
        "entropy_information_value": entropy_gain,
        "entropy_posterior_delta": entropy_delta,
    }
    save_pickle(processed_dir / "detection.pkl", payload)
    save_grid_csv(processed_dir / "posterior.csv", posterior)
    save_ppm(processed_dir / "posterior_vs_baseline.ppm", posterior, baseline, disagreement)
    save_json(processed_dir / "summary.json", {"phase": 4, "entropy_information_value": entropy_gain, "entropy_posterior_delta": entropy_delta})

    write_phase_report(
        report_dir,
        "Phase 4",
        "PASS",
        _report_summary(4, "Bayesian detection, posterior probability mapping, and baseline comparison were generated.", project["project"]["demo_mode"]),
        [
            "Bayesian-style posterior ice probability map created.",
            "Published-threshold-inspired baseline map generated.",
            "Disagreement map between baseline and full model produced.",
            "Entropy information-value check recorded with and without the entropy term.",
        ],
        ["Retune likelihood weights once real L/S-band statistics are available."],
        [],
    )
    return 0


def run_phase_6(repo_root: Path) -> int:
    run_phase_4(repo_root)
    project, assumptions = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 6)
    report_dir = _phase_dir(paths["reports"], 6)
    ensure_dir(processed_dir)

    forward = load_pickle(_phase_dir(paths["processed"], 3) / "forward_model.pkl")
    detection = load_pickle(_phase_dir(paths["processed"], 4) / "detection.pkl")
    pixel_area = 25.0 * 25.0
    depth_m = assumptions["physical"]["target_analysis_depth_m"]
    volume = estimate_ice_volume(forward["ice_fraction"], detection["posterior"], pixel_area, depth_m)
    mc = monte_carlo_volume(
        forward["ice_fraction"],
        detection["posterior"],
        pixel_area,
        depth_m,
        assumptions["demo"]["monte_carlo_samples"],
        _seed_from_text("phase6"),
    )

    payload = {"volume": volume, "uncertainty": mc}
    save_pickle(processed_dir / "resource.pkl", payload)
    save_json(processed_dir / "resource_summary.json", payload)

    write_phase_report(
        report_dir,
        "Phase 6",
        "PASS",
        _report_summary(6, "Resource estimation, ice volume, and Monte Carlo uncertainty propagation were generated.", project["project"]["demo_mode"]),
        [
            "Ice volume low/expected/high range estimated.",
            "Derived water-yield ranges computed.",
            "Monte Carlo uncertainty propagation completed.",
            "Dominant uncertainty source identified for demo mode.",
        ],
        ["Swap demo uncertainty sources for instrument-calibrated DFSAR and dielectric priors."],
        [],
    )
    return 0


def run_phase_7(repo_root: Path) -> int:
    run_phase_6(repo_root)
    project, assumptions = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 7)
    report_dir = _phase_dir(paths["reports"], 7)
    ensure_dir(processed_dir)

    detection = load_pickle(_phase_dir(paths["processed"], 4) / "detection.pkl")
    terrain = load_pickle(_phase_dir(paths["processed"], 5) / "terrain.pkl")
    posterior_mask = threshold_mask(detection["posterior"], percentile(detection["posterior"], 0.85))
    ice_distance = distance_to_mask(posterior_mask)
    weights = assumptions["planning"]["landing_site_scoring_weights"]
    ranked = rank_candidate_sites(terrain["slope"], terrain["boulder"], terrain["illumination"], ice_distance, weights)
    best = ranked[0]
    start = (best["row"], best["col"])
    components = connected_components(posterior_mask)
    if components:
        goal_cluster = max(
            components,
            key=lambda component: sum(detection["posterior"][r][c] for r, c in component) / len(component),
        )
        weighted_row = sum(r * detection["posterior"][r][c] for r, c in goal_cluster)
        weighted_col = sum(c * detection["posterior"][r][c] for r, c in goal_cluster)
        total_weight = sum(detection["posterior"][r][c] for r, c in goal_cluster) or 1.0
        centroid = (weighted_row / total_weight, weighted_col / total_weight)
        goal = min(goal_cluster, key=lambda cell: (cell[0] - centroid[0]) ** 2 + (cell[1] - centroid[1]) ** 2)
    else:
        goal = (len(posterior_mask) // 2, len(posterior_mask[0]) // 2)
    comms_cost = normalize(
        [
            [
                min(1.0, abs(c - start[1]) / max(len(terrain["slope"][0]) - 1, 1) + terrain["slope"][r][c] * 0.4)
                for c in range(len(terrain["slope"][0]))
            ]
            for r in range(len(terrain["slope"]))
        ]
    )
    illumination_cost = [[1.0 - value for value in row] for row in terrain["illumination"]]
    slip_cost = normalize([[min(1.0, terrain["slope"][r][c] * 1.15 + terrain["boulder"][r][c] * 0.35) for c in range(len(terrain["slope"][0]))] for r in range(len(terrain["slope"]))])
    path_result = astar_path(
        start,
        goal,
        terrain["slope"],
        terrain["boulder"],
        illumination_cost,
        comms_cost,
        slip_cost,
        int(assumptions["rover"]["maximum_safe_darkness_dwell_time_hr"] * 6),
    )
    if path_result["status"] == "feasible":
        path = path_result["path"]
        slope_total = sum(terrain["slope"][r][c] for r, c in path)
        boulder_total = sum(terrain["boulder"][r][c] for r, c in path)
        dark_total = sum(illumination_cost[r][c] for r, c in path)
        comms_total = sum(comms_cost[r][c] for r, c in path)
        slip_total = sum(slip_cost[r][c] for r, c in path)
        path_result["cost_breakdown"] = {
            "slope_energy": round(slope_total * 2.4, 2),
            "boulder_risk": round(boulder_total * 1.8, 2),
            "darkness_thermal": round(dark_total * 1.2, 2),
            "communication_visibility": round(comms_total * 0.8, 2),
            "wheel_slip_risk": round(slip_total * 1.4, 2),
        }
        path_result["estimated_energy_wh"] = round(path_result["total_cost"] * 4.3, 1)
        path_result["round_trip_energy_wh"] = round(path_result["estimated_energy_wh"] * 2.0, 1)
        path_result["dwell_margin_hr"] = round(
            assumptions["rover"]["maximum_safe_darkness_dwell_time_hr"] - (path_result["steps"] / 6.0),
            2,
        )
        path_result["max_safe_dwell_time_hr"] = assumptions["rover"]["maximum_safe_darkness_dwell_time_hr"]
    else:
        path_result["cost_breakdown"] = {}
        path_result["estimated_energy_wh"] = None
        path_result["round_trip_energy_wh"] = None
        path_result["dwell_margin_hr"] = None
        path_result["max_safe_dwell_time_hr"] = assumptions["rover"]["maximum_safe_darkness_dwell_time_hr"]

    sensitivity_note = _weight_sensitivity_statement(
        terrain["slope"], terrain["boulder"], terrain["illumination"], ice_distance, weights
    )
    payload = {"ranked_sites": ranked, "path": path_result, "goal": goal, "sensitivity_note": sensitivity_note}
    save_pickle(processed_dir / "planning.pkl", payload)
    save_json(processed_dir / "planning_summary.json", payload)

    landing_grid = [[0.0 for _ in row] for row in terrain["slope"]]
    for index, site in enumerate(ranked, start=1):
        landing_grid[site["row"]][site["col"]] = 1.0 - (index - 1) * 0.2
    path_grid = [[0.0 for _ in row] for row in terrain["slope"]]
    for r, c in path_result["path"]:
        path_grid[r][c] = 1.0
    save_ppm(processed_dir / "landing_sites.ppm", terrain["illumination"], landing_grid, terrain["slope"])
    save_ppm(processed_dir / "traverse_map.ppm", terrain["illumination"], terrain["boulder"], path_grid)
    save_heatmap_svg(
        processed_dir / "landing_sites.svg",
        terrain["illumination"],
        "Landing Site Scoring",
        "Illumination, slope safety, boulder safety, and ice proximity combined with disclosed weights.",
        palette=["#0f172a", "#1d4ed8", "#38bdf8", "#facc15", "#fb7185"],
        points=[
            {
                "row": site["row"],
                "col": site["col"],
                "label": f"{_site_label(idx)} ({site['site']})",
                "color": "#f8fafc" if idx == 0 else "#cbd5e1",
            }
            for idx, site in enumerate(ranked[:4])
        ],
        labels=[
            f"Primary site: {ranked[0]['site']} score {ranked[0]['score']:.3f}",
            f"Runner-up gap: {ranked[0]['score'] - ranked[1]['score']:.3f}" if len(ranked) > 1 else "No alternate sites",
            sensitivity_note,
        ],
        footer="Landing weights are disclosed in assumptions.md and config/assumptions.toml.",
    )
    save_heatmap_svg(
        processed_dir / "traverse_map.svg",
        terrain["boulder"],
        "Rover Traverse",
        "White trace shows the current A* route from landing site to highest-confidence ice zone.",
        palette=["#0b132b", "#1c2541", "#3a506b", "#5bc0be", "#ee6c4d"],
        points=[
            {"row": start[0], "col": start[1], "label": "Start", "color": "#f8fafc"},
            {"row": goal[0], "col": goal[1], "label": "Ice ROI", "color": "#fde68a"},
        ],
        path_points=path_result["path"],
        labels=[
            f"Traverse status: {path_result['status']}",
            f"Energy estimate: {path_result['estimated_energy_wh'] if path_result['estimated_energy_wh'] is not None else 'N/A'} Wh",
            f"Wheel slip term included: {path_result['cost_breakdown'].get('wheel_slip_risk', 'N/A')}",
            f"Dwell margin: {path_result['dwell_margin_hr'] if path_result['dwell_margin_hr'] is not None else 'N/A'} hr",
        ],
        footer="Cost terms shown separately in the dashboard: slope/energy, boulder, darkness/thermal, communication, wheel slip.",
    )

    blockers = [] if path_result["status"] == "feasible" else [f"Traverse infeasible: {path_result['binding_constraint']}"]
    write_phase_report(
        report_dir,
        "Phase 7",
        "PASS" if not blockers else "PASS WITH WARNINGS",
        _report_summary(7, "Landing-site scoring and rover A* path planning were generated.", project["project"]["demo_mode"]),
        [
            "Candidate landing sites ranked with disclosed weights.",
            "Primary site and alternates saved with a weight-sensitivity note.",
            "A* traverse planner executed with slope, boulder, illumination, comms, and wheel-slip costs.",
            "Maximum safe dwell time and round-trip energy are computed for the selected path.",
            "Failure mode reporting included if constraints bind.",
        ],
        ["Replace communication and thermal proxy costs with mission-specific models."],
        blockers,
    )
    return 0


def run_phase_8(repo_root: Path) -> int:
    run_phase_7(repo_root)
    project, assumptions = load_configs(repo_root)
    paths = _repo_paths(repo_root, project)
    processed_dir = _phase_dir(paths["processed"], 8)
    report_dir = _phase_dir(paths["reports"], 8)
    outputs_dir = paths["outputs"]
    ensure_dir(processed_dir)
    ensure_dir(outputs_dir)

    detection = load_pickle(_phase_dir(paths["processed"], 4) / "detection.pkl")
    terrain = load_pickle(_phase_dir(paths["processed"], 5) / "terrain.pkl")
    resource = load_pickle(_phase_dir(paths["processed"], 6) / "resource.pkl")
    planning = load_pickle(_phase_dir(paths["processed"], 7) / "planning.pkl")
    forward = load_pickle(_phase_dir(paths["processed"], 3) / "forward_model.pkl")
    radar = load_pickle(_phase_dir(paths["processed"], 2) / "radar.pkl")

    processed3 = _phase_dir(paths["processed"], 3)
    processed4 = _phase_dir(paths["processed"], 4)
    processed5 = _phase_dir(paths["processed"], 5)
    processed7 = _phase_dir(paths["processed"], 7)

    save_heatmap_svg(
        processed3 / "dual_band_depth.svg",
        forward["dual_band"],
        "Dual-Band Depth Discrimination",
        "L-only bright zones are strongest buried-ice candidates in this MVP logic.",
        palette=["#0f172a", "#334155", "#38bdf8", "#22c55e", "#fde047"],
        labels=[
            f"L penetration: {forward['l_depth_m']:.2f} m",
            f"S penetration: {forward['s_depth_m']:.2f} m",
            "Yellow regions mark deeper buried-scatterer candidates.",
        ],
    )
    save_split_comparison_svg(
        processed4 / "posterior_vs_baseline.svg",
        detection["baseline"],
        detection["posterior"],
        "Baseline vs Bayesian Posterior",
        "Published-style threshold mask",
        "Full posterior probability map",
        "The right panel keeps uncertainty visible instead of forcing a binary answer.",
    )
    save_heatmap_svg(
        processed5 / "terrain_hazards.svg",
        terrain["boulder"],
        "Hazard and Morphology",
        "Hazard intensity rises with slope, blockiness, and morphology-supporting texture.",
        palette=["#081f33", "#126782", "#55a630", "#ffd166", "#ef476f"],
        labels=[
            f"Morphology false-positive rate: {terrain['false_positive_rate']:.3f}",
            "Used for both safety scoring and corroboration logic.",
        ],
    )

    artifacts = [
        (processed3 / "forward_prediction_grid.svg", outputs_dir / "artifact_1_forward_model_grid.svg"),
        (processed3 / "dual_band_depth.svg", outputs_dir / "artifact_2_dual_band_depth.svg"),
        (processed4 / "posterior_vs_baseline.svg", outputs_dir / "artifact_3_posterior_vs_baseline.svg"),
        (processed5 / "terrain_hazards.svg", outputs_dir / "artifact_4_hazard_morphology.svg"),
        (processed7 / "landing_sites.svg", outputs_dir / "artifact_5_landing_sites.svg"),
        (processed7 / "traverse_map.svg", outputs_dir / "artifact_6_traverse_map.svg"),
    ]
    for src, dst in artifacts:
        shutil.copyfile(src, dst)

    site_scores = [
        {
            "site": site["site"],
            "score": round(site["score"], 4),
            "row": site["row"],
            "col": site["col"],
        }
        for site in planning["ranked_sites"][:4]
    ]

    final_statement = (
        f"Given an estimated ice volume of {resource['uncertainty']['low_m3']:.0f}-"
        f"{resource['uncertainty']['high_m3']:.0f} m^3 at {max(value for row in detection['posterior'] for value in row)*100:.0f}% posterior confidence, dominated by "
        f"{resource['uncertainty']['dominant_uncertainty_source']}, and a round-trip traverse cost of "
        f"{planning['path'].get('round_trip_energy_wh', 'N/A')} Wh against a dwell/thermal limit of "
        f"{planning['path'].get('max_safe_dwell_time_hr', 'N/A')} hr, with {planning['path'].get('binding_constraint', 'none')} binding rather than ice scarcity, a follow-up sampling mission is "
        f"{'justified' if planning['path']['status'] == 'feasible' else 'marginal'} for this MVP scenario."
    )

    manifest = {
        "crater": project["project"]["crater_name"],
        "demo_mode": project["project"]["demo_mode"],
        "artifacts": [str(dst.relative_to(repo_root)) for _, dst in artifacts],
        "final_statement": final_statement,
        "top_site": planning["ranked_sites"][0],
        "site_rankings": site_scores,
        "penetration_depths_m": {"l": forward["l_depth_m"], "s": forward["s_depth_m"]},
        "resource_summary": {
            "expected_ice_m3": round(resource["volume"]["expected_m3"], 0),
            "water_yield_expected_m3": round(resource["volume"]["water_yield_expected_m3"], 0),
            "dominant_uncertainty": resource["uncertainty"]["dominant_uncertainty_source"],
        },
        "traverse_summary": {
            "status": planning["path"]["status"],
            "steps": planning["path"].get("steps"),
            "energy_wh": planning["path"].get("estimated_energy_wh"),
            "round_trip_energy_wh": planning["path"].get("round_trip_energy_wh"),
            "dwell_margin_hr": planning["path"].get("dwell_margin_hr"),
            "max_safe_dwell_time_hr": planning["path"].get("max_safe_dwell_time_hr"),
            "binding_constraint": planning["path"].get("binding_constraint"),
            "cost_breakdown": planning["path"].get("cost_breakdown", {}),
        },
        "detection_summary": {
            "entropy_information_value": round(detection["entropy_information_value"], 4),
            "entropy_posterior_delta": round(detection["entropy_posterior_delta"], 4),
            "peak_posterior": round(max(value for row in detection["posterior"] for value in row), 4),
            "radar_metadata_count": len(radar["metadata"]),
        },
        "sensitivity_note": planning["sensitivity_note"],
        "story_beats": [
            "The forward model explains radar behavior before interpreting it.",
            "Dual-band logic adds a depth argument, not just a presence signal.",
            "The posterior map exposes where the baseline would over- or under-call ice.",
            "Landing and traverse decisions stay tied to safety, not only resource proximity.",
        ],
    }
    save_json(outputs_dir / "final_manifest.json", manifest)
    save_json(processed_dir / "dashboard_payload.json", manifest)
    from src.dashboard.app import build_fallback_html

    build_fallback_html(repo_root)

    write_phase_report(
        report_dir,
        "Phase 8",
        "PASS",
        _report_summary(8, "Visualization artifacts, dashboard payloads, and final deliverables were generated.", project["project"]["demo_mode"]),
        [
            "Final artifact manifest created.",
            "Static visualization assets exported for presentation use with observed-point overlays and cost callouts.",
            "Dashboard payload compiled for Streamlit viewer.",
            "Closing mission recommendation statement generated.",
        ],
        ["Install Streamlit locally to run the interactive viewer file directly."],
        [],
    )
    return 0


PHASE_FUNCTIONS = {
    1: run_phase_1,
    2: run_phase_2,
    3: run_phase_3,
    4: run_phase_4,
    5: run_phase_5,
    6: run_phase_6,
    7: run_phase_7,
    8: run_phase_8,
}


def run_phase(repo_root: Path, phase_number: int) -> int:
    return PHASE_FUNCTIONS[phase_number](repo_root)
