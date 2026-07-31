#!/usr/bin/env python3
"""
Run the three-layer theory verification suite (Layers A / B / C).

Deposits a JSON audit under data/audit/ and prints a summary table.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from lod_guide.theory.audit import sha256_hex
from lod_guide.theory.propositions import verify_all_propositions, verify_by_layer

OUT = Path(__file__).resolve().parents[1] / "data" / "audit"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    certs = verify_all_propositions()

    by_layer = {"A": verify_by_layer("A"), "B": verify_by_layer("B"), "C": verify_by_layer("C")}
    failed = [c for c in certs if not c.passed]

    print("\n=== Theory verification (three-layer) ===\n")
    for layer in ("A", "B", "C"):
        rows = by_layer[layer]
        n_pass = sum(1 for c in rows if c.passed)
        print(f"Layer {layer}: {n_pass}/{len(rows)} passed")
        for c in rows:
            mark = "PASS" if c.passed else "FAIL"
            print(f"  [{mark}] {c.result_id}")

    payload = {
        "protocol_id": "LOD-THEORY-VERIFY-v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "n_total": len(certs),
        "n_failed": len(failed),
        "layers": {
            k: {
                "count": len(v),
                "passed": sum(1 for c in v if c.passed),
                "results": [c.to_dict() for c in v],
            }
            for k, v in by_layer.items()
        },
        "all_results": [c.to_dict() for c in certs],
    }
    payload["content_sha256"] = sha256_hex(
        {k: v for k, v in payload.items() if k != "content_sha256"}
    )

    path = OUT / "theory_verification_latest.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nAudit: {path}")
    print(f"Total: {len(certs)} results, {len(failed)} failed, sha256={payload['content_sha256'][:16]}…")

    if failed:
        raise SystemExit(f"Verification failed: {[c.result_id for c in failed]}")


if __name__ == "__main__":
    main()
