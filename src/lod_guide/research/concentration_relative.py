"""
Effect of verification concentration relative to LoD on LoD evaluation.

Operating points
----------------
Let LoD_γ be defined by p(LoD_γ)=γ (typically γ=0.95).
Study material concentration c is expressed as r = c / LoD_γ.

- r < 1  (below LoD): true hit rate p(c) < γ → single-kit “≥γ” claims often fail
  even for a correctly calibrated method; kit contrasts Δp(c) depend on curve shapes.
- r = 1  (at LoD): intended operating point for γ-claims and fair comparisons near claim.
- r > 1  (above LoD): p(c)→1 for competent methods → “easy pass” verification;
  Δp between kits shrinks (saturation) → discrimination power collapses.

This module simulates those effects under a logistic p(c) model and reports
verification pass probability and comparative miss probability β as functions of r.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.special import expit, logit
from scipy.stats import binom, norm

from lod_guide.research.reagent_discrimination import LogisticLoDCurve
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research"


@dataclass(frozen=True)
class KitCurve:
    """Kit-specific logistic curve; LoD_γ may differ via horizontal shift."""

    name: str
    slope: float = 2.0
    gamma: float = 0.95
    # lod_shift_log10: log10(LoD_kit / LoD_ref). Positive => worse (higher LoD).
    lod_shift_log10: float = 0.0

    def p_at_relative_to_ref_lod(self, r: float) -> float:
        """
        r = c / LoD_ref where LoD_ref is a reference method's LoD_γ.
        For this kit, effective log10(c/LoD_kit) = log10(r) - lod_shift_log10.
        """
        if r <= 0:
            return 0.0
        # For reference kit (shift=0): p = expit(slope*(log10(r) + logit(gamma)/slope))
        # = expit(slope*log10(r) + logit(gamma))
        z = self.slope * (np.log10(r) - self.lod_shift_log10) + logit(self.gamma)
        return float(expit(z))


def verify_claim_pass_prob(
    p_true: float,
    n: int,
    claim_p0: float = 0.95,
    *,
    rule: str = "wilson_lower_ge_claim",
    alpha: float = 0.05,
) -> float:
    """
    Probability that a verification study 'passes' a claim p>=p0.

    rule='all_positive': pass if X=n (folklore)
    rule='rate_ge_claim': pass if X/n >= claim_p0
    rule='wilson_lower_ge_claim': pass if Wilson lower bound >= claim_p0
      (strict; for small n often never passes — illustrates need for proper n)
    """
    from lod_guide.theory.exact import wilson_interval

    xs = np.arange(0, n + 1)
    pmf = binom.pmf(xs, n, p_true)
    passes = np.zeros(n + 1, dtype=bool)
    for x in xs:
        if rule == "all_positive":
            passes[x] = x == n
        elif rule == "rate_ge_claim":
            passes[x] = (x / n) >= claim_p0 - 1e-15
        elif rule == "wilson_lower_ge_claim":
            low, _ = wilson_interval(int(x), n, alpha=alpha)
            passes[x] = low >= claim_p0 - 1e-15
        else:
            raise ValueError(rule)
    return float(np.sum(pmf[passes]))


def evaluate_concentration_grid(
    *,
    relative_levels: tuple[float, ...] = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0),
    n_verify: int = 20,
    n_compare: int = 20,
    claim_p0: float = 0.95,
    alpha: float = 0.05,
    kit_a: KitCurve | None = None,
    kit_b: KitCurve | None = None,
) -> dict:
    """
    kit_a: reference-like (shift=0)
    kit_b: worse LoD (positive shift) so that at r=1, p_A≈0.95, p_B lower
    Default shift chosen so at r=1, p_B≈0.80.
    """
    kit_a = kit_a or KitCurve("kit_A_ref", lod_shift_log10=0.0)
    if kit_b is None:
        # Solve shift so p_B(1)=0.80
        # expit(slope*(0 - shift) + logit(gamma)) = 0.80
        # slope*(-shift) + logit(gamma) = logit(0.80)
        shift = (logit(kit_a.gamma) - logit(0.80)) / kit_a.slope
        kit_b = KitCurve("kit_B_worse", slope=kit_a.slope, gamma=kit_a.gamma, lod_shift_log10=float(shift))

    rows = []
    for r in relative_levels:
        pa = kit_a.p_at_relative_to_ref_lod(r)
        pb = kit_b.p_at_relative_to_ref_lod(r)
        # single-kit verification of claim at this concentration (for kit A and B)
        pass_a_folk = verify_claim_pass_prob(pa, n_verify, claim_p0, rule="all_positive")
        pass_a_rate = verify_claim_pass_prob(pa, n_verify, claim_p0, rule="rate_ge_claim")
        pass_b_rate = verify_claim_pass_prob(pb, n_verify, claim_p0, rule="rate_ge_claim")
        # comparative
        if abs(pa - pb) < 1e-12:
            power = float(alpha)  # under H0 roughly
            n_star = float("inf")
        else:
            power = power_two_proportions(pa, pb, n_compare, alpha)
            n_star = float(sample_size_two_proportions(pa, pb, alpha, 0.80))
        miss = 1.0 - power
        zone = "below_LoD" if r < 0.999 else ("at_LoD" if r < 1.001 else "above_LoD")
        rows.append(
            {
                "r_c_over_LoD_ref": r,
                "zone": zone,
                "p_A": pa,
                "p_B": pb,
                "delta_p": abs(pa - pb),
                "P_pass_A_all_positive_n": pass_a_folk,
                "P_pass_A_rate_ge_claim": pass_a_rate,
                "P_pass_B_rate_ge_claim": pass_b_rate,
                "compare_n": n_compare,
                "compare_power": power,
                "compare_miss_beta": miss,
                "n_star_80_for_this_delta": None if not np.isfinite(n_star) else int(np.ceil(n_star)),
            }
        )

    narrative = {
        "below_LoD": (
            "True p < claim. Correct methods often fail rate≥claim verification; "
            "all-positive folklore pass rates drop. Δp between kits may be large or "
            "small depending on curve separation — must not treat failure as ‘bad LoD claim’ "
            "if c was unintentionally below LoD."
        ),
        "at_LoD": (
            "Intended point for γ-claims (p≈γ for a correctly set LoD). "
            "Comparative Δp reflects true kit differences near the claim."
        ),
        "above_LoD": (
            "True p→1 for competent kits: verification ‘easy pass’ (high P(all positive)). "
            "Δp shrinks toward 0 (saturation): miss probability for detecting kit differences "
            "rises even if LoDs truly differ — dangerous false equivalence."
        ),
    }

    return {
        "claim_p0": claim_p0,
        "n_verify": n_verify,
        "n_compare": n_compare,
        "kit_a": asdict(kit_a),
        "kit_b": asdict(kit_b),
        "rows": rows,
        "zone_narrative": narrative,
        "algorithm_id": "CONC-REL-LOD-EVAL-v1",
        "must_evaluate": True,
    }


def run_concentration_relative_study(
    *,
    n_verify: int = 20,
    n_compare: int = 20,
) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = evaluate_concentration_grid(n_verify=n_verify, n_compare=n_compare)
    # headlines at key levels
    by_r = {row["r_c_over_LoD_ref"]: row for row in payload["rows"]}
    payload["headlines"] = {
        "at_r0.5_below": by_r.get(0.5),
        "at_r1.0_lod": by_r.get(1.0),
        "at_r2.0_above": by_r.get(2.0),
    }
    path = OUT_DIR / "concentration_relative_lod.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    out = run_concentration_relative_study()
    for key in ("at_r0.5_below", "at_r1.0_lod", "at_r2.0_above"):
        row = out["headlines"][key]
        print(
            key,
            "pA/pB=",
            round(row["p_A"], 3),
            round(row["p_B"], 3),
            "passA_rate=",
            round(row["P_pass_A_rate_ge_claim"], 3),
            "miss_compare=",
            round(row["compare_miss_beta"], 3),
            "n*=",
            row["n_star_80_for_this_delta"],
        )
