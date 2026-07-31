#!/usr/bin/env python3
"""
One-click runner for the full LOD guidance / research / theory pipeline.

Usage:
    python examples/run_all_analyses.py              # full suite
    python examples/run_all_analyses.py --quick        # skip heavy MC / download
    python examples/run_all_analyses.py --skip-tests # no pytest
    python examples/run_all_analyses.py --only theory,deep-research

Writes a master log to data/audit/run_all_analyses_latest.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
AUDIT = ROOT / "data" / "audit"


def _run_step(name: str, fn) -> dict:
    t0 = time.perf_counter()
    record = {"step": name, "ok": False, "elapsed_s": None, "error": None}
    try:
        fn()
        record["ok"] = True
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc()
    record["elapsed_s"] = round(time.perf_counter() - t0, 2)
    status = "OK" if record["ok"] else "FAIL"
    print(f"\n[{status}] {name} ({record['elapsed_s']}s)")
    if record["error"]:
        print(record["error"])
    return record


def _shell(name: str, cmd: list[str], *, cwd: Path | None = None) -> dict:
    def runner() -> None:
        subprocess.run(cmd, cwd=cwd or ROOT, check=True)

    return _run_step(name, runner)


def _script(name: str, rel_path: str) -> dict:
    def runner() -> None:
        subprocess.run([sys.executable, str(ROOT / rel_path)], cwd=ROOT, check=True)

    return _run_step(name, runner)


def _import_run(module_path: str, func_name: str = "main") -> dict:
    """Run a module under ``src/`` (not ``examples/``)."""
    def runner() -> None:
        import importlib

        mod = importlib.import_module(module_path)
        getattr(mod, func_name)()

    return _run_step(module_path, runner)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run all LOD project analyses")
    p.add_argument("--quick", action="store_true", help="Skip download, heavy MC, paper build")
    p.add_argument("--skip-tests", action="store_true", help="Skip pytest")
    p.add_argument(
        "--only",
        type=str,
        default="",
        help="Comma-separated subset: theory,theory-depth,tests,pipeline-demo,deep-research,"
        "scenarios,transparent,benchmark,paper,download",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    want_all = not only

    def want(name: str) -> bool:
        return want_all or name in only

    print("=" * 72)
    print("LOD — run_all_analyses")
    print(f"Started {datetime.now(UTC).isoformat()}")
    print(f"Root: {ROOT}")
    print("=" * 72)

    records: list[dict] = []

    if want("theory"):
        records.append(_script("theory verification", "examples/run_theory_verification.py"))

    if want("theory-depth"):
        records.append(_script("theory depth studies", "examples/run_theory_depth.py"))

    if want("tests") and not args.skip_tests:
        records.append(
            _shell(
                "pytest (theory suite)",
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_theory_propositions.py",
                    "tests/test_theory_depth.py",
                    "tests/test_theory_layers.py",
                    "tests/test_theory_extensions.py",
                    "tests/test_theory_completion.py",
                ],
            )
        )

    if want("pipeline-demo"):

        def pipeline_demo() -> None:
            import numpy as np

            from lod_guide import run_guidance
            from lod_guide.s0_goal import Goal
            from lod_guide.s4_gated_lob import LoBEstimationMode
            from lod_guide.data.simulate import sim_skewed_hetero_blanks

            ds = sim_skewed_hetero_blanks(seed=0)
            blank = np.asarray(ds.values, dtype=float)
            for mode in (
                LoBEstimationMode.STANDARD,
                LoBEstimationMode.GATED_UNSPLIT,
                LoBEstimationMode.GATED_SAMPLE_SPLIT,
            ):
                res = run_guidance(
                    goal=Goal.G1_VERIFY_LOD,
                    result_type="continuous",
                    values=blank,
                    use_case="skew_blank_lob_demo",
                    lob_estimation_mode=mode,
                )
                print(f"  mode={mode.value} lob={res.report.lob} path={res.model_path.value}")

        records.append(_run_step("pipeline sample-split demo", pipeline_demo))

    if want("deep-research"):
        records.append(_script("deep research", "examples/run_deep_research.py"))

    if want("scenarios"):
        records.append(_script("clinical scenarios", "examples/run_clinical_scenarios.py"))

    if want("transparent"):
        records.append(_script("transparent analysis", "examples/run_transparent_analysis.py"))

    if want("benchmark") and not args.quick:
        records.append(_script("diverse benchmark", "examples/run_diverse_benchmark.py"))

    if want("paper") and not args.quick:
        records.append(_script("paper artifacts", "examples/run_paper_artifacts.py"))

    if want("download") and not args.quick:
        records.append(
            _shell("download tier-A datasets", [sys.executable, "-m", "lod_guide.data.download_real"])
        )

    n_ok = sum(1 for r in records if r["ok"])
    payload = {
        "run_id": "LOD-RUN-ALL-v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "quick": args.quick,
        "skip_tests": args.skip_tests,
        "only": sorted(only) if only else "all",
        "n_steps": len(records),
        "n_ok": n_ok,
        "n_failed": len(records) - n_ok,
        "steps": records,
    }
    AUDIT.mkdir(parents=True, exist_ok=True)
    out = AUDIT / "run_all_analyses_latest.json"
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 72)
    print(f"Finished: {n_ok}/{len(records)} steps OK")
    print(f"Log: {out}")
    print("=" * 72)

    if n_ok < len(records):
        failed = [r["step"] for r in records if not r["ok"]]
        raise SystemExit(f"Failed steps: {failed}")


if __name__ == "__main__":
    main()
