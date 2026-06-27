from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.phase1.dataset_verifier import run_phase_1  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_phase_1(REPO_ROOT))
