#!/usr/bin/env python3
"""Run theory-depth studies (identification, c-optimal, minimax, gated LoB, Pareto exact n)."""

from __future__ import annotations

import json

from lod_guide.paper.theory_audit import certs_from_audit, theory_audit_ok
from lod_guide.paper.theory_research import audit_check, run_theory_depth
from lod_guide.theory.propositions import verify_all_propositions


def main() -> None:
    result = run_theory_depth()
    for name, out in result["studies"].items():
        print(f"[{name}] {out.get('path', out.get('study_id'))}")
        if out.get("headline"):
            print(json.dumps(out["headline"], indent=2))

    if theory_audit_ok():
        certs = certs_from_audit()
        print(
            "Theory results: "
            f"{len(certs)} total, 0 failed (from data/audit/theory_verification_latest.json)"
        )
    else:
        certs = verify_all_propositions()
        failed = [c.result_id for c in certs if not c.passed]
        print(f"Theory results: {len(certs)} total, {len(failed)} failed")
        if failed:
            raise SystemExit(f"Failed: {failed}")

    check = audit_check()
    if not check.get("ok"):
        print("Warning: theory audit not OK — run `make theory-verify` or `lod-guide-theory verify`")


if __name__ == "__main__":
    main()
