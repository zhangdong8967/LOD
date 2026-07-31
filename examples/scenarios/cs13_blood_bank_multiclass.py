"""Clinical scenario demo: CS13_BLOOD_BANK_MULTICLASS"""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from lod_guide.scenarios import get_scenario, run_scenario_demo

def main() -> None:
    sc = get_scenario("CS13_BLOOD_BANK_MULTICLASS")
    print(f"=== {sc.scenario_id}: {sc.title} ===")
    print(f"Lab question: {sc.lab_question}")
    print(f"Goal={sc.goal.value} | Type={sc.result_type.value} | Coverage={sc.coverage.value}")
    print(f"Notes: {sc.notes}")
    print("--- result ---")
    print(json.dumps(run_scenario_demo("CS13_BLOOD_BANK_MULTICLASS"), indent=2, default=str))

if __name__ == "__main__":
    main()
