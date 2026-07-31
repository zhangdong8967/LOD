"""Run all clinical scenario demos and write coverage JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide.scenarios import (
    SCENARIOS,
    coverage_summary,
    run_all_scenario_demos,
    scenarios_table,
)


def main() -> None:
    print("=" * 72)
    print("Clinical scenario catalogue")
    print("=" * 72)
    for s in SCENARIOS:
        print(
            f"{s.scenario_id:32} [{s.coverage.value:7}] "
            f"{s.goal.value:22} {s.result_type.value:12} | {s.title}"
        )
    print("--- coverage counts ---")
    print(json.dumps(coverage_summary(), indent=2))

    print("=" * 72)
    print("Running demos...")
    results = run_all_scenario_demos()
    out_dir = ROOT / "data" / "research"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "clinical_scenarios_catalog.json").write_text(
        json.dumps(
            {
                "coverage_summary": coverage_summary(),
                "scenarios": scenarios_table(),
                "demo_results": results,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    for r in results:
        status = "OK" if "error" not in r else "ERR"
        print(f"  [{status}] {r.get('scenario_id')} coverage={r.get('coverage')}")
    print("Wrote data/research/clinical_scenarios_catalog.json")


if __name__ == "__main__":
    main()
