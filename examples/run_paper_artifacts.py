"""Build unified paper figures/tables/captions + internal review memo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide.paper.build_artifacts import build_paper_artifacts


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build paper_artifacts/ manuscript bundle")
    p.add_argument(
        "--refresh-theory",
        action="store_true",
        help="Rerun verify_all_propositions() instead of reusing theory audit JSON",
    )
    p.add_argument(
        "--refresh-exact",
        action="store_true",
        help="Rerun run_exact_power_study() instead of reusing exact_vs_asymptotic_power.json",
    )
    p.add_argument(
        "--full-verify",
        action="store_true",
        help="Alias for --refresh-theory --refresh-exact",
    )
    p.add_argument(
        "--legacy-figures",
        action="store_true",
        help="Also regenerate legacy developer figure bundles (Fig M/C/D/L/T…)",
    )
    p.add_argument(
        "--no-prune-figures",
        action="store_true",
        help="Keep stale PNG/PDF files in figures/methodology/ after build",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    full = args.full_verify
    man = build_paper_artifacts(
        skip_heavy_exact=not (args.refresh_exact or full),
        skip_heavy_theory=not (args.refresh_theory or full),
        legacy_figures=args.legacy_figures,
        prune_legacy_figures=not args.no_prune_figures,
    )
    print(json.dumps(man, indent=2))
    print("\nWrote paper_artifacts/ — see paper_artifacts/README.md")


if __name__ == "__main__":
    main()
