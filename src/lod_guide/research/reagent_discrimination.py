"""
Reagent LoD discrimination evaluator (Goal E2).

Questions answered
------------------
1. For true hit rates (p_A, p_B) — e.g. 0.90 vs 0.80, or 0.90 vs 0.50 —
   how many replicates per reagent are required for power 1-β at level α?
2. At a folklore n (5, 10, 20, …), what is the probability of *missing*
   the difference (Type II error β̂ = 1 − power)? That false “no difference”
   conclusion is the clinical/regulatory hazard.
3. At what concentration *relative to a claimed LoD* do these p values arise,
   under a logistic detection-probability curve (concentration ↔ p map)?

This is a first-class evaluation algorithm for the lod_guide research programme.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.special import expit, logit
from scipy.stats import norm

from lod_guide.research.operating_characteristics import run_oc_cell
from lod_guide.s5_sample_size import (
    power_two_proportions,
    sample_size_two_proportions,
)

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research"


# ---------------------------------------------------------------------------
# Concentration ↔ detection probability (relative to LoD)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LogisticLoDCurve:
    """
    p(c) = expit( slope * (log10(c) - log10(c50)) )

    Define LoD_γ as the concentration with p(LoD_γ)=γ (often γ=0.95).
    Then relative level x = c / LoD_γ has a closed map to p.
    """

    slope: float = 2.0  # per log10 concentration decade
    gamma_lod: float = 0.95  # LoD definition: p(LoD)=gamma

    def lod_multiplier_for_p(self, p: float) -> float:
        """Return c / LoD_γ such that detection probability equals p."""
        if not (0.0 < p < 1.0):
            raise ValueError("p must be in (0,1)")
        # log10(c/c50) = logit(p)/slope
        # log10(LoD/c50) = logit(gamma)/slope
        # log10(c/LoD) = (logit(p)-logit(gamma))/slope
        return float(10 ** ((logit(p) - logit(self.gamma_lod)) / self.slope))

    def p_at_relative_lod(self, relative_c: float) -> float:
        """Detection probability at c = relative_c * LoD_γ."""
        if relative_c <= 0:
            return 0.0
        log_ratio = np.log10(relative_c) + logit(self.gamma_lod) / self.slope
        # log10(c/c50) = log10(relative) + log10(LoD/c50)
        return float(expit(self.slope * log_ratio))


# ---------------------------------------------------------------------------
# Discrimination evaluation
# ---------------------------------------------------------------------------

@dataclass
class DiscriminationScenario:
    p_a: float
    p_b: float
    label: str
    n_star_80: int
    n_star_90: int
    miss_prob_at_n: dict  # n -> beta (miss probability)
    power_at_n: dict
    relative_c_a: float  # c/LoD95 for reagent A rate
    relative_c_b: float
    exact_fisher_miss_n20: float = float("nan")
    # If both reagents tested at SAME concentration, interpret as two kits
    # with different p at that level; relative_c_* map each p to the c/LoD
    # of a *reference* logistic curve (illustrative).


def miss_probability(p_a: float, p_b: float, n: int, alpha: float = 0.05) -> float:
    """β = 1 − power = P(fail to reject H0 | true difference)."""
    return float(1.0 - power_two_proportions(p_a, p_b, n, alpha))


def evaluate_pair(
    p_a: float,
    p_b: float,
    *,
    label: str = "",
    alpha: float = 0.05,
    folklore_ns: tuple[int, ...] = (5, 10, 20, 30, 60, 100),
    curve: LogisticLoDCurve | None = None,
    n_sims_check: int = 0,
    seed: int = 0,
) -> DiscriminationScenario:
    if p_a < p_b:
        p_a, p_b = p_b, p_a
    curve = curve or LogisticLoDCurve()
    n80 = int(np.ceil(sample_size_two_proportions(p_a, p_b, alpha, 0.80)))
    n90 = int(np.ceil(sample_size_two_proportions(p_a, p_b, alpha, 0.90)))
    ns = sorted(set(folklore_ns + (n80, n90)))
    power_at = {n: power_two_proportions(p_a, p_b, n, alpha) for n in ns}
    miss_at = {n: 1.0 - power_at[n] for n in ns}

    # Exact Fisher miss at folklore n=20 (referee-facing; asymptotic remains for n*)
    from lod_guide.theory.exact_tests import exact_power_two_proportions

    exact_fisher_miss_n20 = float(1.0 - exact_power_two_proportions(p_a, p_b, 20, alpha, test="fisher"))

    return DiscriminationScenario(
        p_a=p_a,
        p_b=p_b,
        label=label or f"{p_a:.0%}_vs_{p_b:.0%}",
        n_star_80=n80,
        n_star_90=n90,
        miss_prob_at_n={int(k): float(v) for k, v in miss_at.items()},
        power_at_n={int(k): float(v) for k, v in power_at.items()},
        relative_c_a=curve.lod_multiplier_for_p(p_a),
        relative_c_b=curve.lod_multiplier_for_p(p_b),
        exact_fisher_miss_n20=exact_fisher_miss_n20,
    )


def evaluation_algorithm_spec() -> dict:
    """Documented steps of the reagent-discrimination evaluation algorithm."""
    return {
        "algorithm_id": "E2-DISCRIM-EVAL-v1",
        "steps": [
            "S0: Lock estimand θ=p_A(c*)-p_B(c*) at a declared concentration c*.",
            "S1: Confirm binary/hit-rate result type (or reduce continuous to hit via cutoff).",
            "Map: Optionally report c*/LoD_γ for each kit via logistic p(c) curve.",
            "S5a: Compute n*(α, 1-β, p_A, p_B) by Fleiss–Chow two-proportion formula.",
            "S5b: For each candidate n in {5,10,20,...,n*}, compute power and miss prob β=1-power.",
            "S5c: Monte Carlo cross-check Type II rate at folklore n and at n*.",
            "S6: Report: required n*, miss probabilities, relative LoD levels, SHA audit.",
            "Decision rule: Do NOT claim ‘no difference’ unless study was powered for the Δ of interest.",
        ],
        "false_conclusion": {
            "name": "Type II / missed discrimination",
            "definition": (
                "Conclude reagents are equivalent (fail to reject H0) when true "
                "p_A ≠ p_B. Probability ≈ β = 1 − power(n; p_A, p_B, α)."
            ),
            "must_evaluate": True,
        },
        "must_evaluate_in_this_research": True,
        "rationale": (
            "Comparative LoD claims without powered n are scientifically and "
            "regulatorily hazardous; evaluating miss probability is mandatory "
            "in lod_guide Goal E2 analyses."
        ),
    }


def continuous_p_grid(
    p_max_pct: int = 99,
    p_min_pct: int = 50,
    step_pct: int = 1,
) -> np.ndarray:
    """Integer percent grid from p_max down to p_min inclusive (e.g. 99,98,…,50)."""
    if step_pct < 1:
        raise ValueError("step_pct must be >= 1")
    if not (0 < p_min_pct < p_max_pct < 100):
        raise ValueError("need 0 < p_min_pct < p_max_pct < 100")
    return np.arange(p_max_pct, p_min_pct - 1, -step_pct, dtype=float) / 100.0


def evaluate_continuous_vs_reference(
    p_reference: float,
    *,
    p_max_pct: int = 99,
    p_min_pct: int = 50,
    step_pct: int = 1,
    alpha: float = 0.05,
    folklore_n: int = 20,
    curve: LogisticLoDCurve | None = None,
) -> dict:
    """
    For fixed reference hit rate p_reference, sweep competitor rates on the
    integer percent grid and return n*(80%), miss β at folklore n, and relative LoD.
    Only competitor rates strictly below p_reference are retained.
    """
    curve = curve or LogisticLoDCurve()
    grid = continuous_p_grid(p_max_pct=p_max_pct, p_min_pct=p_min_pct, step_pct=step_pct)
    rows = []
    for p_b in grid:
        if p_b >= p_reference - 1e-15:
            continue
        n80 = int(np.ceil(sample_size_two_proportions(p_reference, float(p_b), alpha, 0.80)))
        n90 = int(np.ceil(sample_size_two_proportions(p_reference, float(p_b), alpha, 0.90)))
        miss20 = miss_probability(p_reference, float(p_b), folklore_n, alpha)
        rows.append(
            {
                "p_reference": p_reference,
                "p_competitor": float(p_b),
                "p_competitor_pct": int(round(100 * p_b)),
                "delta": float(p_reference - p_b),
                "n_star_80": n80,
                "n_star_90": n90,
                "miss_prob_at_n20": miss20,
                "power_at_n20": float(1.0 - miss20),
                "relative_c_reference": curve.lod_multiplier_for_p(p_reference),
                "relative_c_competitor": curve.lod_multiplier_for_p(float(p_b)),
            }
        )
    return {
        "p_reference": p_reference,
        "p_reference_pct": int(round(100 * p_reference)),
        "folklore_n": folklore_n,
        "alpha": alpha,
        "n_points": len(rows),
        "rows": rows,
    }


def evaluate_relative_lod_continuum(
    *,
    p_max_pct: int = 99,
    p_min_pct: int = 50,
    step_pct: int = 1,
    curve: LogisticLoDCurve | None = None,
) -> list[dict]:
    """Map every integer percent hit rate on [p_min, p_max] to c/LoD_95."""
    curve = curve or LogisticLoDCurve()
    out = []
    for p in continuous_p_grid(p_max_pct=p_max_pct, p_min_pct=p_min_pct, step_pct=step_pct)[::-1]:
        # ascending 50→99 for plotting convenience in callers
        out.append(
            {
                "p": float(p),
                "p_pct": int(round(100 * p)),
                "relative_c_lod95": curve.lod_multiplier_for_p(float(p)),
            }
        )
    return out


def run_continuous_discrimination_study(
    *,
    references: tuple[float, ...] = (0.99, 0.95, 0.90),
    p_max_pct: int = 99,
    p_min_pct: int = 50,
    step_pct: int = 1,
    alpha: float = 0.05,
    slope: float = 2.0,
) -> dict:
    """
    Continuous E2 discrimination surface on integer percent rates 99→50.

    Deposits analytic n* and miss@n=20 for each reference vs every lower
    competitor percent, plus the relative-LoD continuum. Discrete vignette
    pairs (90vs80 etc.) remain in run_reagent_discrimination_study().
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    curve = LogisticLoDCurve(slope=slope, gamma_lod=0.95)
    by_ref = {}
    for pref in references:
        # Sweep competitors from min(p_max, floor(100*pref)-1) down to p_min
        pref_pct = int(round(100 * pref))
        block = evaluate_continuous_vs_reference(
            pref,
            p_max_pct=min(p_max_pct, pref_pct - 1),
            p_min_pct=p_min_pct,
            step_pct=step_pct,
            alpha=alpha,
            curve=curve,
        )
        by_ref[f"{pref_pct}pct"] = block

    rel = evaluate_relative_lod_continuum(
        p_max_pct=p_max_pct, p_min_pct=p_min_pct, step_pct=step_pct, curve=curve
    )

    # Compact arrays for plotting / Table export
    def _series(block: dict) -> dict:
        rows = block["rows"]
        return {
            "p_competitor_pct": [r["p_competitor_pct"] for r in rows],
            "n_star_80": [r["n_star_80"] for r in rows],
            "miss_prob_at_n20": [r["miss_prob_at_n20"] for r in rows],
            "delta": [r["delta"] for r in rows],
        }

    payload = {
        "study_id": "E2-DISCRIM-CONTINUOUS-v1",
        "purpose": (
            "Replace sparse vignette-only discrimination summaries with a full "
            "integer-percent continuum from 99% down to 50% hit rates."
        ),
        "grid": {
            "p_max_pct": p_max_pct,
            "p_min_pct": p_min_pct,
            "step_pct": step_pct,
            "references": list(references),
            "alpha": alpha,
            "power_target": 0.80,
            "folklore_n": 20,
            "logistic_slope_per_log10": slope,
        },
        "by_reference": by_ref,
        "series": {k: _series(v) for k, v in by_ref.items()},
        "relative_lod_continuum": rel,
        "headline": {
            "n_reference_curves": len(references),
            "n_competitor_points_per_99pct_curve": by_ref.get("99pct", {}).get("n_points"),
            "n_star_99_vs_98": next(
                (r["n_star_80"] for r in by_ref.get("99pct", {}).get("rows", []) if r["p_competitor_pct"] == 98),
                None,
            ),
            "n_star_99_vs_50": next(
                (r["n_star_80"] for r in by_ref.get("99pct", {}).get("rows", []) if r["p_competitor_pct"] == 50),
                None,
            ),
            "n_star_90_vs_80": next(
                (r["n_star_80"] for r in by_ref.get("90pct", {}).get("rows", []) if r["p_competitor_pct"] == 80),
                None,
            ),
            "miss20_90_vs_80": next(
                (r["miss_prob_at_n20"] for r in by_ref.get("90pct", {}).get("rows", []) if r["p_competitor_pct"] == 80),
                None,
            ),
            "relative_c_at_50pct": next((r["relative_c_lod95"] for r in rel if r["p_pct"] == 50), None),
            "relative_c_at_99pct": next((r["relative_c_lod95"] for r in rel if r["p_pct"] == 99), None),
        },
        "claim_boundary": (
            "Analytic Fleiss–Chow n* and asymptotic miss β on a dense percent grid. "
            "Exact Fisher/Boschloo confirmation remains required at chosen operating points; "
            "relative LoD uses an illustrative logistic slope."
        ),
    }
    path = OUT_DIR / "reagent_discrimination_continuous.json"
    # Store without duplicating huge nested rows twice — keep by_reference rows
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def run_reagent_discrimination_study(
    *,
    pairs: list[tuple[float, float, str]] | None = None,
    alpha: float = 0.05,
    slope: float = 2.0,
    n_sims_check: int = 5000,
    seed: int = 7,
) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if pairs is None:
        pairs = [
            (0.90, 0.80, "90%_vs_80%"),
            (0.90, 0.50, "90%_vs_50%"),
            (0.95, 0.80, "95%_vs_80%"),
            (0.95, 0.50, "95%_vs_50%"),
            (0.80, 0.50, "80%_vs_50%"),
        ]
    curve = LogisticLoDCurve(slope=slope, gamma_lod=0.95)
    scenarios = []
    mc_checks = {}
    for p_a, p_b, label in pairs:
        sc = evaluate_pair(
            p_a,
            p_b,
            label=label,
            alpha=alpha,
            curve=curve,
            n_sims_check=0,
        )
        scenarios.append(asdict(sc))
        # MC miss probs at n=5,10,20,n*
        mc_checks[label] = {}
        for n in (5, 10, 20, sc.n_star_80):
            row = run_oc_cell(
                max(p_a, p_b),
                min(p_a, p_b),
                n,
                n_sims=n_sims_check,
                seed=seed + n + int(1000 * p_a),
                setting=f"{label}_n{n}",
            )
            mc_checks[label][f"n={n}"] = {
                "empirical_power": row.reject_rate,
                "empirical_miss_prob_beta": 1.0 - row.reject_rate,
                "analytic_miss_prob_beta": miss_probability(p_a, p_b, n, alpha),
            }

    # Same-concentration interpretation: if both kits tested at LoD_95 of a
    # reference method (p=0.95), a worse kit with p=0.80 is "easier" to
    # distinguish than 0.90 vs 0.80 at a lower relative level — report both.
    same_c_note = {
        "interpretation": (
            "relative_c_a and relative_c_b are the concentrations (as multiples "
            "of LoD_95 on a reference logistic curve with given slope) at which "
            "a SINGLE method would show those hit rates. If two reagents are "
            "compared at ONE shared concentration c*, use the (p_A,p_B) at that "
            "c* directly; the relative_c values help communicate how far below/"
            "near claimed LoD that operating point sits."
        ),
        "slope_per_log10": slope,
        "lod_definition": "p(LoD_95)=0.95",
    }

    payload = {
        "algorithm": evaluation_algorithm_spec(),
        "alpha": alpha,
        "logistic_curve": same_c_note,
        "scenarios": scenarios,
        "monte_carlo_miss_checks": mc_checks,
        "headline": {
            "90_vs_80_n_star_80power": next(
                s["n_star_80"] for s in scenarios if s["label"] == "90%_vs_80%"
            ),
            "90_vs_80_miss_at_n20": next(
                s["miss_prob_at_n"][20] for s in scenarios if s["label"] == "90%_vs_80%"
            ),
            "90_vs_50_n_star_80power": next(
                s["n_star_80"] for s in scenarios if s["label"] == "90%_vs_50%"
            ),
            "90_vs_50_miss_at_n20": next(
                s["miss_prob_at_n"][20] for s in scenarios if s["label"] == "90%_vs_50%"
            ),
            "90_vs_50_miss_at_n5": next(
                s["miss_prob_at_n"][5] for s in scenarios if s["label"] == "90%_vs_50%"
            ),
            "90_vs_80_exact_fisher_miss_n20": next(
                s["exact_fisher_miss_n20"] for s in scenarios if s["label"] == "90%_vs_80%"
            ),
            "90_vs_50_exact_fisher_miss_n20": next(
                s["exact_fisher_miss_n20"] for s in scenarios if s["label"] == "90%_vs_50%"
            ),
        },
    }
    # JSON requires string keys in nested dicts — normalize miss/power maps
    for s in payload["scenarios"]:
        s["miss_prob_at_n"] = {str(k): v for k, v in s["miss_prob_at_n"].items()}
        s["power_at_n"] = {str(k): v for k, v in s["power_at_n"].items()}
    path = OUT_DIR / "reagent_discrimination_eval.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # Always deposit the dense 99→50 continuum alongside vignette pairs
    continuous = run_continuous_discrimination_study(alpha=alpha, slope=slope)
    payload["continuous_path"] = continuous.get("path")
    payload["continuous_headline"] = continuous.get("headline")
    return payload


if __name__ == "__main__":
    out = run_reagent_discrimination_study()
    print(json.dumps(out["algorithm"], indent=2)[:500])
    print("--- headlines ---")
    print(json.dumps(out["headline"], indent=2))
    for s in out["scenarios"]:
        if s["label"] in {"90%_vs_80%", "90%_vs_50%"}:
            print(
                s["label"],
                "n*80=",
                s["n_star_80"],
                "miss@5=",
                round(s["miss_prob_at_n"]["5"], 3),
                "miss@10=",
                round(s["miss_prob_at_n"]["10"], 3),
                "miss@20=",
                round(s["miss_prob_at_n"]["20"], 3),
                "c/LoD95 for p_a,p_b=",
                round(s["relative_c_a"], 3),
                round(s["relative_c_b"], 3),
            )
