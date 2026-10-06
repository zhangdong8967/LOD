#!/usr/bin/env python3
"""
Run the three-layer theory verification suite (Layers A / B / C).

Deposits a JSON audit under data/audit/ and prints a summary table.
"""

from __future__ import annotations

from lod_guide.paper.theory_research import run_theory_verification
from lod_guide.theory.propositions import verify_by_layer


def main() -> None:
    result = run_theory_verification(force=False)
    certs_by_layer = {layer: verify_by_layer(layer) for layer in ("A", "B", "C")}

    print("\n=== Theory verification (three-layer) ===\n")
    for layer in ("A", "B", "C"):
        rows = certs_by_layer[layer]
        n_pass = sum(1 for c in rows if c.passed)
        print(f"Layer {layer}: {n_pass}/{len(rows)} passed")
        for c in rows:
            mark = "PASS" if c.passed else "FAIL"
            print(f"  [{mark}] {c.result_id}")

    print(f"\nAudit: {result['audit_path']}")
    print(
        f"Total: {result['n_total']} results, {result['n_failed']} failed, "
        f"sha256={result['content_sha256'][:16]}…"
    )

    if result["n_failed"]:
        raise SystemExit(f"Verification failed: {result['failed_ids']}")


if __name__ == "__main__":
    main()
