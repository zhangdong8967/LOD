"""
Seed-locked reproducibility deposit for confirmatory tables/figures.

Writes data/research/REPRODUCIBILITY.json with seeds, versions, and artifact hashes.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

from lod_guide import __version__

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "research"

# Locked seeds for confirmatory blocks (do not change without bumping study_id)
LOCKED_SEEDS = {
    "exact_power_study": 11,
    "type1_calibration": 42,
    "operating_characteristics": 1,
    "lob_coverage": 2,
    "reagent_discrimination_mc": 7,
    "bootstrap_estradiol": 17,
    "precision_profile": 0,
    "continuous_models": 0,
}


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_reproducibility_deposit(
    *,
    extra_artifacts: list[Path] | None = None,
) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    artifacts = [
        OUT / "exact_vs_asymptotic_power.json",
        OUT / "type1_calibration.json",
        OUT / "precision_profile_loq.json",
        OUT / "ep17_estradiol_analysis.json",
        OUT / "reagent_discrimination_eval.json",
        OUT / "operating_characteristics.json",
        OUT / "lob_coverage.json",
        ROOT / "paper_artifacts" / "MANIFEST.json",
        ROOT / "paper_artifacts" / "tables" / "Table03_exact_vs_asymptotic.csv",
        ROOT / "paper_artifacts" / "tables" / "Table04_propositions_P1_P6.csv",
    ]
    if extra_artifacts:
        artifacts.extend(extra_artifacts)

    hashed = []
    for p in artifacts:
        hashed.append({"path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p), "sha256": _sha256_file(p)})

    payload = {
        "deposit_id": "LOD-GUIDE-REPRO-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "lod_guide_version": __version__,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "locked_seeds": LOCKED_SEEDS,
        "artifacts": hashed,
        "how_to_reproduce": [
            "pip install -e '.[dev]'",
            "python -m lod_guide.data.download_real",
            "python examples/run_deep_research.py",
            "make paper-artifacts",
            "python -m lod_guide.research.reproducibility_deposit",
        ],
        "policy": (
            "Changing LOCKED_SEEDS requires bumping deposit_id. "
            "Primary small-n claims must cite exact/Fisher–Boschloo tables, not asymptotic alone."
        ),
    }
    path = OUT / "REPRODUCIBILITY.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(build_reproducibility_deposit(), indent=2)[:1500])
