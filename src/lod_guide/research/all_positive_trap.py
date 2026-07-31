"""
All-positive trap: observing n/n hits does NOT imply a reliable LoD.

If X ~ Binomial(n, p) and we observe X = n (100% detection in the study),

    P(X = n | p) = p^n.

Thus even a mediocre true p can easily produce a perfect empirical hit rate
when n is small (5 or 10). Conversely, a one-sided Clopper–Pearson lower
bound after n/n successes is strictly less than 1:

    p_L = alpha^(1/n)   for the exact lower (1-alpha) bound when X=n
    (equivalently beta quantile form).

This module tabulates misleading probabilities and lower bounds for
Clinical Chemistry–grade scrutiny of folklore small-n “100% detection” claims.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.stats import beta

from lod_guide.theory.exact import clopper_pearson_interval, wilson_interval

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research"


@dataclass(frozen=True)
class AllPositiveProb:
    n: int
    true_p: float
    prob_all_positive: float  # p^n


@dataclass(frozen=True)
class AllPositiveInference:
    n: int
    successes: int  # = n
    alpha: float
    cp_low: float
    cp_high: float
    wilson_low: float
    wilson_high: float
    exact_lower_closed_form: float  # alpha**(1/n)
    claim_p0: float
    rejects_claim_one_sided: bool  # whether CP lower > claim? usually False
    compatible_with_claim: bool  # claim_p0 >= cp_low (claim not ruled out)


def prob_all_positive(p: float, n: int) -> float:
    """P(X=n) for X~Bin(n,p) = p^n."""
    if not (0.0 <= p <= 1.0) or n < 1:
        raise ValueError("need p in [0,1], n>=1")
    return float(p**n)


def exact_lower_bound_after_all_success(
    n: int,
    alpha: float = 0.05,
    *,
    two_sided: bool = False,
) -> float:
    """
    Exact lower confidence bound when X=n.

    - one-sided level (1-alpha): p_L = alpha ** (1/n)
    - two-sided Clopper–Pearson level (1-alpha): p_L = (alpha/2) ** (1/n)
    """
    a = alpha / 2 if two_sided else alpha
    return float(a ** (1.0 / n))


def inference_after_all_positive(
    n: int,
    *,
    alpha: float = 0.05,
    claim_p0: float = 0.95,
) -> AllPositiveInference:
    cp = clopper_pearson_interval(n, n, alpha=alpha)
    w = wilson_interval(n, n, alpha=alpha)
    p_l_one = exact_lower_bound_after_all_success(n, alpha=alpha, two_sided=False)
    p_l_two = exact_lower_bound_after_all_success(n, alpha=alpha, two_sided=True)
    compatible = claim_p0 >= cp[0] - 1e-15
    rejects = cp[0] > claim_p0 + 1e-15
    return AllPositiveInference(
        n=n,
        successes=n,
        alpha=alpha,
        cp_low=cp[0],
        cp_high=cp[1],
        wilson_low=w[0],
        wilson_high=w[1],
        exact_lower_closed_form=p_l_two,  # matches two-sided CP
        claim_p0=claim_p0,
        rejects_claim_one_sided=rejects,
        compatible_with_claim=compatible,
    )


# keep one-sided helper visible in study highlights via run_all_positive_trap_study


def misleading_probability_table(
    ns: tuple[int, ...] = (5, 10, 20, 60),
    true_ps: tuple[float, ...] = (0.50, 0.70, 0.80, 0.85, 0.90, 0.95, 0.99),
) -> list[AllPositiveProb]:
    rows = []
    for n in ns:
        for p in true_ps:
            rows.append(AllPositiveProb(n, p, prob_all_positive(p, n)))
    return rows


def probability_true_p_below_claim_given_all_positive_uniform(
    n: int,
    claim_p0: float = 0.95,
    *,
    prior_low: float = 0.0,
    prior_high: float = 1.0,
) -> dict:
    """
    Bayesian exhibit with Uniform(prior_low, prior_high) prior truncated:
    posterior of p after X=n is Beta(n+1, 1) truncated to [prior_low, prior_high]
    for Uniform(0,1) prior (conjugate).

    Under Uniform(0,1): posterior = Beta(n+1, 1), density (n+1) p^n on (0,1).
    P(p < claim_p0 | X=n) = claim_p0**(n+1).

    Interpretation: even after seeing all positives, probability that true p
    is still below the claimed LoD hit rate claim_p0.
    """
    if prior_low != 0.0 or prior_high != 1.0:
        # numerical integrate on truncated uniform
        grid = np.linspace(prior_low, prior_high, 20_001)
        # likelihood p^n; prior flat
        w = grid**n
        w = w / w.sum()
        prob = float(w[grid < claim_p0].sum())
        mean = float((grid * w).sum())
    else:
        prob = float(claim_p0 ** (n + 1))
        # posterior mean of Beta(n+1,1) = (n+1)/(n+2)
        mean = float((n + 1) / (n + 2))
    return {
        "n": n,
        "claim_p0": claim_p0,
        "prior": f"Uniform({prior_low},{prior_high})",
        "posterior": "Beta(n+1, 1) if Uniform(0,1)",
        "P_true_p_below_claim_given_all_positive": prob,
        "posterior_mean_p": mean,
        "closed_form_note": "For Uniform(0,1): P(p<p0|X=n)=p0**(n+1)",
    }


def run_all_positive_trap_study(
    *,
    alpha: float = 0.05,
    claim_p0: float = 0.95,
) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    probs = misleading_probability_table()
    inferences = [
        inference_after_all_positive(n, alpha=alpha, claim_p0=claim_p0)
        for n in (5, 10, 20, 60)
    ]
    bayes = [
        probability_true_p_below_claim_given_all_positive_uniform(n, claim_p0)
        for n in (5, 10, 20, 60)
    ]

    # Key “dead-end” messages for n=5 and n=10
    highlights = {
        "P_all_pos_given_p070_n5": prob_all_positive(0.70, 5),
        "P_all_pos_given_p080_n5": prob_all_positive(0.80, 5),
        "P_all_pos_given_p090_n5": prob_all_positive(0.90, 5),
        "P_all_pos_given_p070_n10": prob_all_positive(0.70, 10),
        "P_all_pos_given_p080_n10": prob_all_positive(0.80, 10),
        "P_all_pos_given_p090_n10": prob_all_positive(0.90, 10),
        "CP_lower_n5_onesided": exact_lower_bound_after_all_success(5, alpha, two_sided=False),
        "CP_lower_n10_onesided": exact_lower_bound_after_all_success(10, alpha, two_sided=False),
        "CP_lower_n20_onesided": exact_lower_bound_after_all_success(20, alpha, two_sided=False),
        "CP_lower_n5_twosided": exact_lower_bound_after_all_success(5, alpha, two_sided=True),
        "CP_lower_n10_twosided": exact_lower_bound_after_all_success(10, alpha, two_sided=True),
        "CP_lower_n20_twosided": exact_lower_bound_after_all_success(20, alpha, two_sided=True),
        "bayes_P_p_below_095_given_5of5": bayes[0]["P_true_p_below_claim_given_all_positive"],
        "bayes_P_p_below_095_given_10of10": bayes[1]["P_true_p_below_claim_given_all_positive"],
    }

    payload = {
        "alpha": alpha,
        "claim_p0": claim_p0,
        "formulae": {
            "likelihood_all_positive": "P(X=n|p)=p^n",
            "one_sided_lower_X_eq_n": "p_L = alpha**(1/n)",
            "two_sided_CP_lower_X_eq_n": "p_L = (alpha/2)**(1/n)",
            "uniform_prior_posterior_prob": "P(p < p0 | X=n) = p0**(n+1)",
            "uniform_prior_posterior_mean": "E[p|X=n]=(n+1)/(n+2)",
        },
        "highlights": highlights,
        "probability_table": [asdict(r) for r in probs],
        "inference_after_nn": [asdict(r) for r in inferences],
        "bayesian_uniform": bayes,
    }
    path = OUT_DIR / "all_positive_trap.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


# --- Proposition certificates ---

def prop_all_positive_closed_forms() -> dict:
    """Verify (alpha/2)**(1/n) matches two-sided Clopper–Pearson lower at X=n."""
    ok = True
    details = {}
    for n in (5, 10, 20):
        a = 0.05
        closed = exact_lower_bound_after_all_success(n, a, two_sided=True)
        cp = clopper_pearson_interval(n, n, a)[0]
        match = abs(closed - cp) < 1e-10
        ok = ok and match
        details[f"n={n}"] = {
            "closed_twosided": closed,
            "closed_onesided": exact_lower_bound_after_all_success(n, a, two_sided=False),
            "cp_low": cp,
            "match": match,
        }
    return {"passed": ok, "details": details}


if __name__ == "__main__":
    out = run_all_positive_trap_study()
    print(json.dumps(out["formulae"], indent=2))
    print(json.dumps(out["highlights"], indent=2))
    print("certificate", prop_all_positive_closed_forms())
