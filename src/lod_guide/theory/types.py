"""
Shared types for the three-layer theory architecture.

Layer A — Analytic theorems (closed-form proofs, no Monte Carlo).
Layer B — Finite-sample bounds (enumeration / exact formulas).
Layer C — Numerical certificates (Monte Carlo or grid verification).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TheoryLayer = Literal["A", "B", "C"]


@dataclass(frozen=True)
class TheoryResult:
    """Unified result for theorems, bounds, and certificates."""

    result_id: str
    layer: TheoryLayer
    statement: str
    passed: bool
    proof_sketch: str
    details: dict

    @property
    def proposition_id(self) -> str:
        """Backward-compatible alias for ``result_id``."""
        return self.result_id

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "proposition_id": self.result_id,
            "layer": self.layer,
            "statement": self.statement,
            "passed": self.passed,
            "proof_sketch": self.proof_sketch,
            "details": self.details,
        }


# Backward-compatible alias used by existing tests and propositions.py
PropositionCertificate = TheoryResult
