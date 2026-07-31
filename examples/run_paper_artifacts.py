"""Build unified paper figures/tables/captions + internal review memo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide.paper.build_artifacts import build_paper_artifacts


def main() -> None:
    man = build_paper_artifacts(skip_heavy_exact=False)
    print(json.dumps(man, indent=2))
    print("\nWrote paper_artifacts/ — see paper_artifacts/README.md")


if __name__ == "__main__":
    main()
