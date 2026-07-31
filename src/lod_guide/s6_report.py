"""
S6 — Mandatory reporting template for guidance recommendations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from lod_guide.challenge import POSITIONING_STATEMENT


@dataclass
class GuidanceReport:
    goal: str
    use_case: str | None
    result_type: str
    diagnostics_summary: dict[str, Any]
    correction_method: str
    model_path: str
    parametric_ok: bool
    sample_size: dict[str, Any]
    assumptions_passed: list[str]
    assumptions_failed: list[str]
    warnings: list[str] = field(default_factory=list)
    lob: float | None = None
    lod: float | None = None
    sensitivity: dict[str, Any] | None = None
    positioning: str = POSITIONING_STATEMENT


    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# LoD Guidance Report",
            "",
            f"**Positioning:** {self.positioning}",
            "",
            "## S0 Goal",
            f"- Goal: `{self.goal}`",
            f"- Use case: `{self.use_case}`",
            "",
            "## S1 Result type",
            f"- `{self.result_type}`",
            "",
            "## S2 Diagnostics",
        ]
        for k, v in self.diagnostics_summary.items():
            lines.append(f"- **{k}**: {v}")
        lines += [
            "",
            "## S3 Correction",
            f"- Method: `{self.correction_method}`",
            f"- Parametric OK: **{self.parametric_ok}**",
            "",
            "## S4 Model path",
            f"- `{self.model_path}`",
        ]
        if self.lob is not None or self.lod is not None:
            lines += [
                "",
                "## Estimates (if applicable)",
                f"- LoB: {self.lob}",
                f"- LoD: {self.lod}",
            ]
        lines += [
            "",
            "## S5 Sample size",
        ]
        multilevel = self.sample_size.get("multilevel_lod_design")
        for k, v in self.sample_size.items():
            if k == "multilevel_lod_design":
                continue
            lines.append(f"- **{k}**: {v}")
        if multilevel:
            lines += [
                "",
                "### S5 multilevel LoD design (P15/P16 gate + P13 minimax)",
                f"- Identifiable: **{multilevel.get('identifiable')}**",
                f"- Method: `{multilevel.get('method')}`",
            ]
            rec = multilevel.get("recommended_design") or {}
            if rec:
                lines.append(
                    f"- Recommended concentrations: {rec.get('concentrations')} "
                    f"(n/level: {rec.get('n_per_level')})"
                )
            if multilevel.get("se_at_plan") is not None:
                lines.append(f"- SE(log10 LoD) at plan: {multilevel['se_at_plan']:.4f}")
            if multilevel.get("worst_case_se") is not None:
                lines.append(f"- Worst-case SE(log10 LoD): {multilevel['worst_case_se']:.4f}")
            if multilevel.get("improvement_worst_case_ratio") is not None:
                lines.append(
                    f"- Minimax vs folklore (worst-case SE ratio): "
                    f"{multilevel['improvement_worst_case_ratio']:.2f}×"
                )
        lines += ["", "## Assumptions passed"]
        lines += [f"- {a}" for a in self.assumptions_passed] or ["- (none)"]
        lines += ["", "## Assumptions failed"]
        lines += [f"- {a}" for a in self.assumptions_failed] or ["- (none)"]
        if self.warnings:
            lines += ["", "## Warnings"]
            lines += [f"- {w}" for w in self.warnings]
        if self.sensitivity:
            lines += ["", "## S7 Sensitivity (summary)"]
            for k, v in self.sensitivity.items():
                lines.append(f"- **{k}**: {v}")
        lines.append("")
        return "\n".join(lines)
