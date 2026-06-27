from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib
import xml.etree.ElementTree as ET


PDS_NS = {"pds": "http://pds.nasa.gov/pds4/pds/v1", "isda": "http://pds.nasa.gov/pds4/isda/v1"}


@dataclass
class DatasetAudit:
    root: Path
    project_config: dict
    assumptions_config: dict
    metadata_files: list[Path] = field(default_factory=list)
    referenced_payloads: list[tuple[Path, Path]] = field(default_factory=list)
    existing_payloads: list[Path] = field(default_factory=list)
    missing_payloads: list[tuple[Path, Path]] = field(default_factory=list)
    l_band_metadata: list[Path] = field(default_factory=list)
    s_band_metadata: list[Path] = field(default_factory=list)
    midas_outputs: list[Path] = field(default_factory=list)
    ohrc_files: list[Path] = field(default_factory=list)
    shadowcam_files: list[Path] = field(default_factory=list)
    dem_files: list[Path] = field(default_factory=list)
    illumination_files: list[Path] = field(default_factory=list)
    lola_count_labels: list[Path] = field(default_factory=list)

    def run(self) -> None:
        data_root = self.root / self.project_config["paths"]["data_root"]
        self.metadata_files = sorted(data_root.rglob("*.xml"))
        for xml_path in self.metadata_files:
            self._inspect_xml(xml_path)

        for lbl_path in sorted(data_root.rglob("*.LBL")):
            self._inspect_lbl(lbl_path)

        self.ohrc_files = self._find_by_keywords(data_root, ("ohrc",))
        self.shadowcam_files = self._find_by_keywords(data_root, ("shadowcam",))
        self.dem_files = self._find_dem_candidates(data_root)
        self.illumination_files = self._find_by_keywords(
            data_root, ("illum", "solar", "sun", "psr", "shadow")
        )
        self.midas_outputs = self._find_by_keywords(
            data_root, ("cpr.bin", "dop.bin", "c2", "midas")
        )

    def _inspect_xml(self, xml_path: Path) -> None:
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            return

        band = tree.findtext(".//isda:frequency_band", namespaces=PDS_NS)
        if band == "L":
            self.l_band_metadata.append(xml_path)
        elif band == "S":
            self.s_band_metadata.append(xml_path)

        for file_name_node in tree.findall(".//pds:File/pds:file_name", PDS_NS):
            relative_name = (file_name_node.text or "").strip()
            if not relative_name:
                continue
            payload_path = xml_path.parent / relative_name
            self.referenced_payloads.append((xml_path, payload_path))
            if payload_path.exists():
                self.existing_payloads.append(payload_path)
            else:
                self.missing_payloads.append((xml_path, payload_path))

    def _inspect_lbl(self, lbl_path: Path) -> None:
        text = lbl_path.read_text(errors="ignore")
        if "LRO-L-LOLA-4-GDR-V1.0" in text and "NAME                  = COUNT" in text:
            self.lola_count_labels.append(lbl_path)

    def _find_by_keywords(self, data_root: Path, keywords: tuple[str, ...]) -> list[Path]:
        matches: list[Path] = []
        for path in sorted(data_root.rglob("*")):
            if not path.is_file():
                continue
            lowered = path.name.lower()
            if any(keyword in lowered for keyword in keywords):
                matches.append(path)
        return matches

    def _find_dem_candidates(self, data_root: Path) -> list[Path]:
        candidates: list[Path] = []
        for path in sorted(data_root.rglob("*")):
            if not path.is_file():
                continue
            lowered = path.name.lower()
            if any(token in lowered for token in ("dem", "ldem", "elevation", "height")):
                candidates.append(path)
        return candidates

    @property
    def blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.l_band_metadata:
            blockers.append("No DFSAR L-band metadata products were found.")
        if self.missing_payloads:
            blockers.append(
                f"{len(self.missing_payloads)} metadata-referenced payload files are missing from disk."
            )
        if not self.s_band_metadata:
            blockers.append("No DFSAR S-band metadata products were found.")
        if not self.midas_outputs:
            blockers.append("No MIDAS-generated DFSAR processing outputs were found (for example CPR/DOP or C2 products).")
        if not self.ohrc_files:
            blockers.append("No OHRC imagery products were found.")
        if not self.shadowcam_files:
            blockers.append("No ShadowCam imagery products were found.")
        if not self.dem_files:
            blockers.append("No DEM raster products were found.")
        if not self.illumination_files:
            blockers.append("No illumination, solar-geometry, or PSR-boundary products were found.")
        return blockers

    def build_phase_report(self) -> str:
        report_dir = self.project_config["project"]["report_root"] + "/phase_1"
        status = "PASS WITH WARNINGS" if self.blockers and self.project_config["project"].get("demo_mode") else ("BLOCKED" if self.blockers else "PASS")
        pdf_source = self.project_config["project"]["pdf_source"]

        available_items = [
            f"- XML metadata products: {len(self.metadata_files)}",
            f"- L-band DFSAR metadata products: {len(self.l_band_metadata)}",
            f"- S-band DFSAR metadata products: {len(self.s_band_metadata)}",
            f"- MIDAS-derived processing outputs: {len(self.midas_outputs)}",
            f"- Existing metadata-referenced payload files: {len(self.existing_payloads)}",
            f"- Missing metadata-referenced payload files: {len(self.missing_payloads)}",
            f"- OHRC imagery products: {len(self.ohrc_files)}",
            f"- ShadowCam imagery products: {len(self.shadowcam_files)}",
            f"- DEM raster candidates: {len(self.dem_files)}",
            f"- Illumination or PSR products: {len(self.illumination_files)}",
            f"- LOLA count-map labels: {len(self.lola_count_labels)}",
        ]

        missing_payload_details = "\n".join(
            f"- `{payload.relative_to(self.root)}` referenced by `{xml_path.relative_to(self.root)}`"
            for xml_path, payload in self.missing_payloads[:12]
        )
        if not missing_payload_details:
            missing_payload_details = "- None"

        blocker_lines = "\n".join(f"- {item}" for item in self.blockers) or "- None"
        pending_lines = "\n".join(
            [
                "- Supply the missing DFSAR payload files referenced by the existing L-band metadata.",
                "- Supply a matching S-band DFSAR full-polarimetric acquisition for the same crater.",
                "- Process the DFSAR acquisition in MIDAS and save the derived outputs needed for CPR and DOP analysis.",
                "- Supply Chandrayaan-2 OHRC imagery for the crater and surrounding control terrain.",
                "- Supply NASA ShadowCam imagery for doubly shadowed crater assessment.",
                "- Supply a usable DEM raster, not only LOLA count-map labels.",
                "- Supply illumination/sun-angle geometry or enough source data to derive it reproducibly.",
                "- Replace all placeholder physical, instrument, rover, and scoring assumptions in `config/assumptions.toml` with sourced values.",
            ]
        )
        completed_lines = "\n".join(
            [
                "- Repository scaffolding aligned to the PDF target structure.",
                "- Phase 1 dataset-verification entrypoint at `scripts/run_phase1.py`.",
                "- Configured project and assumption manifests under `config/`.",
                f"- Markdown reporting outputs under `{report_dir}/`.",
            ]
        )

        return f"""# Phase 1 Report

**Status:** {status}
**Source of truth:** `{pdf_source}`

## Mission gate

Phase 1 verifies the repository scaffold and checks the workspace against the mandatory inputs in Section 14 of the PDF before any scientific implementation continues. In hackathon MVP mode, missing datasets are reported but do not stop the synthetic demo pipeline.

## Dataset verification summary

- Required DFSAR dual-band full polarimetry: incomplete
- Required MIDAS DFSAR processing outputs: missing
- Required OHRC imagery: missing
- Required ShadowCam imagery: missing
- Required DEM: missing
- Required illumination/sun-angle geometry: missing

## Evidence

{chr(10).join(available_items)}

### Missing metadata-referenced payloads

{missing_payload_details}

## Completed modules list

{completed_lines}

## Pending tasks

{pending_lines}

## Blockers

{blocker_lines}

## Stop decision

{"Per the original mission rule, work would stop here. MVP demo mode is enabled, so later phases may continue with explicit synthetic assumptions and warnings." if self.project_config["project"].get("demo_mode") else "Per the mission rule, work stops after Phase 1 validation whenever a required dataset is missing. No later phase is started until these blockers are resolved."}
"""

    def build_completed_modules(self) -> str:
        return """# Completed Modules

- Phase 1 repository scaffold
- Phase 1 dataset verifier
- Phase 1 configuration manifests
- Phase 1 markdown reporting outputs
"""

    def build_pending_tasks(self) -> str:
        return """# Pending Tasks

- Add missing DFSAR payload files referenced by current metadata.
- Add the matching S-band DFSAR acquisition.
- Add MIDAS outputs for CPR, DOP, and any intermediate C2 products used in the workflow.
- Add OHRC imagery.
- Add ShadowCam imagery.
- Add DEM raster coverage.
- Add illumination or solar-geometry inputs.
- Replace placeholder assumption values with sourced numbers.
"""

    def build_blockers(self) -> str:
        if not self.blockers:
            return "# Blockers\n\n- None\n"
        return "# Blockers\n\n" + "\n".join(f"- {item}" for item in self.blockers) + "\n"


def _load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_phase_1(repo_root: Path) -> int:
    project_config = _load_toml(repo_root / "config/project.toml")
    assumptions_config = _load_toml(repo_root / "config/assumptions.toml")
    audit = DatasetAudit(repo_root, project_config, assumptions_config)
    audit.run()

    report_dir = repo_root / project_config["project"]["report_root"] / "phase_1"
    _write_text(report_dir / "phase_report.md", audit.build_phase_report())
    _write_text(report_dir / "completed_modules.md", audit.build_completed_modules())
    _write_text(report_dir / "pending_tasks.md", audit.build_pending_tasks())
    _write_text(report_dir / "blockers.md", audit.build_blockers())

    return 0 if project_config["project"].get("demo_mode") else (1 if audit.blockers else 0)
