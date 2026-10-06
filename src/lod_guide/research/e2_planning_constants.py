"""
Shared E2 planning constants — illustrative pair vs full lattice.

The integer 50–99% lattice (1225 valid pairs) is the primary analysis surface.
ILLUSTRATIVE_PAIR is one reference row for worked examples, not the estimand.
"""

from __future__ import annotations

ILLUSTRATIVE_PAIR: tuple[float, float, str] = (0.90, 0.80, "90/80")

# Back-compat aliases used in legacy tests and certificates.
P_A_ILLUSTRATIVE = ILLUSTRATIVE_PAIR[0]
P_B_ILLUSTRATIVE = ILLUSTRATIVE_PAIR[1]
ILLUSTRATIVE_LABEL = ILLUSTRATIVE_PAIR[2]
