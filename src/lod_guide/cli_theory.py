#!/usr/bin/env python3
"""CLI for the unified theory research pipeline."""

from __future__ import annotations

import argparse
import json
import sys

from lod_guide.paper.theory_research import (
    audit_check,
    build_defects_bundle,
    build_table4,
    copy_audit_bundle,
    run_theory_depth,
    run_theory_pipeline,
    run_theory_verification,
    write_theory_summary,
)


def _cmd_verify(args: argparse.Namespace) -> int:
    result = run_theory_verification(force=args.force)
    print(json.dumps(result, indent=2))
    return 1 if result["n_failed"] else 0


def _cmd_depth(args: argparse.Namespace) -> int:
    studies = tuple(args.study) if args.study else None
    result = run_theory_depth(studies=studies)
    print(json.dumps(result, indent=2, default=str))
    return 0


def _cmd_table4(args: argparse.Namespace) -> int:
    t4 = build_table4(force_verify=args.force)
    defects = build_defects_bundle(force_verify=args.force)
    bundle = copy_audit_bundle() if args.copy_audit else {}
    print(json.dumps({"table4": t4, "defects": defects, "audit_bundle": bundle}, indent=2))
    return 0


def _cmd_audit_check(args: argparse.Namespace) -> int:
    result = audit_check(min_total=args.min_total)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def _cmd_summary(args: argparse.Namespace) -> int:
    path = write_theory_summary(force_verify=args.force)
    print(path)
    return 0


def _cmd_all(args: argparse.Namespace) -> int:
    result = run_theory_pipeline(
        verify=not args.skip_verify,
        depth=not args.skip_depth,
        table4=not args.skip_table4,
        internal_review=args.internal_review,
        summary=not args.skip_summary,
        copy_audit=not args.skip_audit_copy,
        force_verify=args.force,
        depth_studies=tuple(args.study) if args.study else None,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lod-guide-theory",
        description="LOD theory research: P1–P18 certificates, depth studies, Table 4, D1–D3 bundle.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("verify", help="Run P1–P18 verification → data/audit/")
    v.add_argument("--force", action="store_true", help="Bypass in-process verify cache")
    v.set_defaults(func=_cmd_verify)

    d = sub.add_parser("depth", help="Run theory-depth research deposits")
    d.add_argument(
        "--study",
        action="append",
        choices=[
            "identification",
            "c_optimal",
            "minimax_probit",
            "probit_robustness",
            "pre_test_lob",
            "pareto_exact_n",
        ],
        help="Run selected study only (repeatable)",
    )
    d.set_defaults(func=_cmd_depth)

    t = sub.add_parser("table4", help="Build Table 4 CSV/JSON + D1–D3 defects bundle")
    t.add_argument("--force", action="store_true", help="Re-run live verification for Table 4")
    t.add_argument("--no-copy-audit", dest="copy_audit", action="store_false")
    t.set_defaults(func=_cmd_table4)

    a = sub.add_parser("audit-check", help="Check theory_verification_latest.json")
    a.add_argument("--min-total", type=int, default=27)
    a.set_defaults(func=_cmd_audit_check)

    s = sub.add_parser("summary", help="Write THEORY_RESEARCH_SUMMARY.md")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=_cmd_summary)

    all_p = sub.add_parser("all", help="Full pipeline: verify → depth → table4 → bundle")
    all_p.add_argument("--force", action="store_true", help="Force live P1–P18 verification")
    all_p.add_argument("--skip-verify", action="store_true")
    all_p.add_argument("--skip-depth", action="store_true")
    all_p.add_argument("--skip-table4", action="store_true")
    all_p.add_argument("--skip-summary", action="store_true")
    all_p.add_argument("--skip-audit-copy", action="store_true")
    all_p.add_argument("--internal-review", action="store_true", help="Also run internal review memo")
    all_p.add_argument("--study", action="append", choices=[
        "identification", "c_optimal", "minimax_probit",
        "probit_robustness", "pre_test_lob", "pareto_exact_n",
    ])
    all_p.set_defaults(func=_cmd_all)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
