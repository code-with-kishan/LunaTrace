from __future__ import annotations

from pathlib import Path
import tomllib


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_configs(repo_root: Path) -> tuple[dict, dict]:
    project = load_toml(repo_root / "config/project.toml")
    assumptions = load_toml(repo_root / "config/assumptions.toml")
    return project, assumptions
