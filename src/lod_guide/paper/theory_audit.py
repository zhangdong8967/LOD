"""Reuse theory verification audit JSON instead of rerunning slow MC certificates."""

from __future__ import annotations

import json
import os
from pathlib import Path

from lod_guide.theory.propositions import verify_all_propositions
from lod_guide.theory.types import TheoryResult

ROOT = Path(__file__).resolve().parents[3]
THEORY_AUDIT = ROOT / "data" / "audit" / "theory_verification_latest.json"
PAPER_AUDIT = ROOT / "paper_artifacts" / "audit"
PAPER_TABLE4 = (
    ROOT / "paper_artifacts" / "tables" / "manuscript" / "Table04_propositions_P1_P18.csv"
)
PAPER_DEFECTS = ROOT / "paper_artifacts" / "audit" / "D1_D3_verification_defects.json"


def refresh_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def theory_audit_ok(*, min_total: int = 27) -> bool:
    if not THEORY_AUDIT.is_file():
        return False
    try:
        payload = json.loads(THEORY_AUDIT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return payload.get("n_failed", 1) == 0 and payload.get("n_total", 0) >= min_total


def theory_bundle_ok() -> bool:
    """True when audit passes and paper_artifacts theory bundle is in sync."""
    if not theory_audit_ok():
        return False
    mirror = PAPER_AUDIT / THEORY_AUDIT.name
    if not mirror.is_file() or not PAPER_TABLE4.is_file() or not PAPER_DEFECTS.is_file():
        return False
    try:
        src_sha = json.loads(THEORY_AUDIT.read_text(encoding="utf-8")).get("content_sha256")
        dst_sha = json.loads(mirror.read_text(encoding="utf-8")).get("content_sha256")
    except (json.JSONDecodeError, OSError):
        return False
    return bool(src_sha) and src_sha == dst_sha


def certs_from_audit() -> list[TheoryResult]:
    payload = json.loads(THEORY_AUDIT.read_text(encoding="utf-8"))
    certs: list[TheoryResult] = []
    for layer in ("A", "B", "C"):
        block = payload.get("layers", {}).get(layer, {})
        for row in block.get("results", []):
            certs.append(
                TheoryResult(
                    result_id=row["result_id"],
                    layer=row["layer"],
                    statement=row["statement"],
                    passed=bool(row["passed"]),
                    proof_sketch=row.get("proof_sketch", ""),
                    details=row.get("details") or {},
                )
            )
    return certs


def load_theory_certificates(*, force_verify: bool = False) -> list[TheoryResult]:
    if force_verify or refresh_flag("LOD_REFRESH_THEORY") or not theory_audit_ok():
        print("[paper] loading theory certificates: running verify_all_propositions()...", flush=True)
        return verify_all_propositions()
    print(
        "[paper] loading theory certificates from data/audit/theory_verification_latest.json "
        "(set LOD_REFRESH_THEORY=1 to rerun)",
        flush=True,
    )
    return certs_from_audit()
