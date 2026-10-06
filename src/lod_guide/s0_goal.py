"""
S0 — Fix the scientific goal (estimand) before any formula.

Locked goals E1–E3 (do not invent ad-hoc goals without extending this enum).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Goal(str, Enum):
    """Primary scientific goal for an LoD evaluation episode."""

    E1_VERIFY_LOD = "E1_VERIFY_LOD"
    """Single-method LoD verification (rate or concentration claim)."""

    E2_COMPARE_REAGENTS = "E2_COMPARE_REAGENTS"
    """Compare two reagents / lots (Δp or ΔLoD)."""

    LOQ_PRECISION = "LOQ_PRECISION"
    """LoQ / precision claim (CV or CI width)."""

    E3_QUALITATIVE_KN = "E3_QUALITATIVE_KN"
    """Qualitative k/n detection claim."""


GOAL_DESCRIPTIONS: dict[Goal, str] = {
    Goal.E1_VERIFY_LOD: (
        "Verify a single claimed LoD (parametric concentration, "
        "hit-rate / detection probability, or nonparametric percentile)."
    ),
    Goal.E2_COMPARE_REAGENTS: (
        "Compare LoD-related performance between two reagents or lots; "
        "requires powered contrast on observed rates or LoD estimates."
    ),
    Goal.LOQ_PRECISION: (
        "Establish or verify LoQ via precision profile (target CV% or total error)."
    ),
    Goal.E3_QUALITATIVE_KN: (
        "Qualitative claim that at least k of n replicates are positive "
        "at a stated concentration / LoD level."
    ),
}


# Primary lab use-cases mapped to goals (frozen for v0.1)
PRIMARY_USE_CASES: dict[str, Goal] = {
    "verify_manufacturer_lod_claim": Goal.E1_VERIFY_LOD,
    "ldt_lod_establishment": Goal.E1_VERIFY_LOD,
    "kit_a_vs_kit_b_near_lod": Goal.E2_COMPARE_REAGENTS,
    "lot_to_lot_lod_check": Goal.E2_COMPARE_REAGENTS,
    "functional_sensitivity_loq": Goal.LOQ_PRECISION,
    "nat_hit_rate_kn": Goal.E3_QUALITATIVE_KN,
    "immunoassay_qualitative_cutoff": Goal.E3_QUALITATIVE_KN,
}


@dataclass(frozen=True)
class GoalSpec:
    """User declaration at S0."""

    goal: Goal
    use_case: str | None = None
    notes: str = ""

    def validate(self) -> None:
        if self.use_case is not None and self.use_case not in PRIMARY_USE_CASES:
            # Allow custom labels, but warn via notes convention
            pass
        if self.use_case in PRIMARY_USE_CASES and PRIMARY_USE_CASES[self.use_case] != self.goal:
            raise ValueError(
                f"use_case '{self.use_case}' maps to {PRIMARY_USE_CASES[self.use_case].value}, "
                f"not {self.goal.value}"
            )


def declare_goal(goal: Goal | str, use_case: str | None = None, notes: str = "") -> GoalSpec:
    """S0 entry point: lock the estimand."""
    g = Goal(goal) if isinstance(goal, str) else goal
    spec = GoalSpec(goal=g, use_case=use_case, notes=notes)
    spec.validate()
    return spec
