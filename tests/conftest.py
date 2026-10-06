"""Shared pytest fixtures — cache theory certificates within a test session."""

from __future__ import annotations

import os

import pytest

from lod_guide.paper.theory_audit import load_theory_certificates
from lod_guide.theory.types import TheoryResult


def _force_theory_verify() -> bool:
    return os.environ.get("LOD_FORCE_THEORY_VERIFY", "").strip().lower() in {"1", "true", "yes"}


@pytest.fixture(scope="session")
def theory_certs() -> list[TheoryResult]:
    """One certificate load per pytest session (audit JSON unless forced)."""
    return load_theory_certificates(force_verify=_force_theory_verify())


@pytest.fixture(scope="session")
def theory_by_layer(theory_certs: list[TheoryResult]):
    def _by_layer(layer: str) -> list[TheoryResult]:
        want = layer.upper()
        return [c for c in theory_certs if c.layer == want]

    return _by_layer
