"""
LoD_95 semantics: analytical 5% miss vs inferential alpha/beta.

At LoD_95 the operational definition is p(c*) = 0.95, so Pr(miss | at LoD) = 0.05
(the rare-miss idea behind detection limits). Verification adds a finite-n layer:
alpha controls false alarm under H0; beta (or 1 - gamma) controls failure to confirm
the written claim under the planning alternative. These quantities are aligned in
spirit but not interchangeable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

LOD95_TARGET_P = 0.95
OPERATIONAL_MISS_RATE = 1.0 - LOD95_TARGET_P  # 0.05 at LoD_95
DEFAULT_ALPHA = 0.05


@dataclass(frozen=True)
class DualFivePercentFrame:
    """Analytical (assay) vs inferential (verification) 5% layers."""

    p0: float
    operational_miss_rate: float
    alpha: float
    analytical_layer: str
    inferential_layer: str
    planner_note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def dual_five_percent_frame(
    *,
    p0: float = LOD95_TARGET_P,
    alpha: float = DEFAULT_ALPHA,
) -> DualFivePercentFrame:
    miss = 1.0 - float(p0)
    return DualFivePercentFrame(
        p0=float(p0),
        operational_miss_rate=miss,
        alpha=float(alpha),
        analytical_layer=(
            f"At LoD benchmark p0={p0:.2f}, Pr(miss | c*)={miss:.2f} "
            "(operational rare miss that defines a detection limit)."
        ),
        inferential_layer=(
            f"Finite-n verification: alpha={alpha:.2f} bounds false rejection under H0; "
            "beta or 1-gamma bounds failure to confirm the written claim under the "
            "planning alternative."
        ),
        planner_note=(
            "S5 returns finite n* matching prespecified OC; no n-to-infinity extrapolation."
        ),
    )


def format_semantics_markdown(frame: DualFivePercentFrame | None = None) -> str:
    f = frame or dual_five_percent_frame()
    return "\n".join(
        [
            "## LoD_95 semantics (analytical vs inferential 5%)",
            f"- **Analytical:** {f.analytical_layer}",
            f"- **Inferential:** {f.inferential_layer}",
            f"- **Planner:** {f.planner_note}",
        ]
    )
