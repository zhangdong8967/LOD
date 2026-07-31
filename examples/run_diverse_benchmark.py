"""Run guidance across real + simulated diverse LoD datasets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide.challenge import manifesto_markdown
from lod_guide.data import build_catalogue, run_diverse_benchmark
from lod_guide.figures import generate_challenge_figures


def main() -> None:
    print(manifesto_markdown())
    print("\n" + "=" * 72)
    print("Building catalogue (download real if needed + simulate diverse cases)...")
    cat = build_catalogue(download=True)
    for e in cat:
        print(f"  [{e.source:10}] {e.dataset_id:32} type={e.result_type:12} tags={e.challenge_tags}")

    print("\nRunning S0–S7 on each dataset...")
    rows = run_diverse_benchmark(download=False)
    out_json = ROOT / "data" / "benchmark_results.json"
    out_json.write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_json}")
    for r in rows:
        print(
            f"  {r.get('dataset_id', '?'):32} path={r.get('model_path', '?'):28} "
            f"n={r.get('n_per_arm', '?'):>5} parametric={r.get('parametric_ok')}"
        )

    print("\nGenerating challenge figures...")
    for p in generate_challenge_figures():
        print(" ", p)


if __name__ == "__main__":
    main()
