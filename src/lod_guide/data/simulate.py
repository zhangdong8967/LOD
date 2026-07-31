"""
Diverse simulated near-LoD datasets for algorithm stress-testing.

Design principles (referee defense):
  1. Every scenario has an explicit data-generating process (DGP) in meta.
  2. Binary / multiclass scenarios emit actual Bernoulli / categorical draws,
     not only parameter stubs.
  3. Seeds are fixed and recorded; JSON includes sha256 of payload for audit.
  4. Simulations are *mechanism / stress* evidence (tier S), never claimed as
     substitutes for multi-assay real raw data (tiers A–C in evidence_manifest).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SIM_DIR = ROOT / "data" / "simulated"


@dataclass
class SimulatedDataset:
    dataset_id: str
    result_type: str  # binary | continuous | count | multiclass
    description: str
    challenge_tags: list[str]
    values: np.ndarray | None = None
    strata: np.ndarray | None = None
    low_level: np.ndarray | None = None
    meta: dict | None = None

    def to_payload(self) -> dict:
        return {
            "dataset_id": self.dataset_id,
            "result_type": self.result_type,
            "description": self.description,
            "challenge_tags": self.challenge_tags,
            "values": None if self.values is None else self.values.tolist(),
            "strata": None if self.strata is None else self.strata.tolist(),
            "low_level": None if self.low_level is None else self.low_level.tolist(),
            "meta": self.meta or {},
        }

    def to_disk(self, directory: Path | None = None) -> Path:
        directory = directory or SIM_DIR
        directory.mkdir(parents=True, exist_ok=True)
        payload = self.to_payload()
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload["meta"] = dict(payload.get("meta") or {})
        payload["meta"]["sha256_payload"] = hashlib.sha256(raw).hexdigest()
        payload["meta"]["evidence_tier"] = "S_simulation_stress"
        out = directory / f"{self.dataset_id}.json"
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out


def sim_normal_blanks(seed: int = 0) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    values = rng.normal(0.05, 0.02, size=60)
    return SimulatedDataset(
        "sim_normal_blanks",
        "continuous",
        "Homoscedastic Gaussian blanks (folklore-friendly baseline).",
        ["baseline_normal"],
        values=values,
        strata=np.repeat(np.arange(3), 20),
        low_level=rng.normal(0.15, 0.03, size=60),
        meta={
            "seed": seed,
            "dgp": "values ~ N(0.05, 0.02^2); low ~ N(0.15, 0.03^2); 3 strata x 20",
            "true_mean": 0.05,
            "true_sd": 0.02,
        },
    )


def sim_skewed_hetero_blanks(seed: int = 1) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    parts, strata = [], []
    scales = [0.3, 0.6, 1.2, 2.0]
    for i, scale in enumerate(scales):
        parts.append(rng.lognormal(mean=-0.5, sigma=scale, size=40))
        strata.append(np.full(40, i))
    values = np.concatenate(parts)
    return SimulatedDataset(
        "sim_skewed_hetero_blanks",
        "continuous",
        "Lognormal blanks with strong batch scale heterogeneity.",
        ["skew", "heterogeneity", "challenges_C2_C3"],
        values=values,
        strata=np.concatenate(strata),
        low_level=rng.lognormal(0.5, 0.8, size=80),
        meta={
            "seed": seed,
            "dgp": "batch i: Lognormal(mu=-0.5, sigma=s_i), s=(0.3,0.6,1.2,2.0), n=40 each",
            "batches": 4,
            "scales": scales,
        },
    )


def sim_censored_floor(seed: int = 2) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    raw = rng.normal(0.0, 1.0, size=100)
    values = np.clip(raw, 0.0, None)
    return SimulatedDataset(
        "sim_censored_floor",
        "continuous",
        "Gaussian latent signal with hard left-censoring at zero.",
        ["censoring", "challenges_C2"],
        values=values,
        strata=np.repeat(np.arange(5), 20),
        meta={
            "seed": seed,
            "dgp": "latent ~ N(0,1); observed = max(latent, 0)",
            "floor": 0.0,
            "latent": "N(0,1)",
            "censor_rate_expected": float(np.mean(raw <= 0)),
        },
    )


def sim_binary_reagents_90_vs_80(seed: int = 3, n_per_arm: int = 200) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    p_a, p_b = 0.90, 0.80
    ya = rng.binomial(1, p_a, size=n_per_arm)
    yb = rng.binomial(1, p_b, size=n_per_arm)
    values = np.concatenate([ya, yb]).astype(float)
    strata = np.array([0] * n_per_arm + [1] * n_per_arm)
    return SimulatedDataset(
        "sim_binary_reagents_90_vs_80",
        "binary",
        "Two reagents with true detection rates 0.90 vs 0.80 near claimed LoD.",
        ["discrimination", "challenges_C1_C4"],
        values=values,
        strata=strata,
        meta={
            "seed": seed,
            "dgp": f"Y_A ~ Bern({p_a}), Y_B ~ Bern({p_b}), n={n_per_arm}/arm independent",
            "p_a": p_a,
            "p_b": p_b,
            "n_per_arm": n_per_arm,
            "folklore_n": 20,
            "observed_rate_a": float(ya.mean()),
            "observed_rate_b": float(yb.mean()),
        },
    )


def sim_binary_low_p(seed: int = 4, n: int = 100) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    p = 0.10
    y = rng.binomial(1, p, size=n).astype(float)
    return SimulatedDataset(
        "sim_binary_low_p_lod",
        "binary",
        "True single-trial p=0.10 at low concentration (true LoD regime).",
        ["low_detection_probability", "challenges_C1"],
        values=y,
        strata=np.zeros(n, dtype=int),
        meta={
            "seed": seed,
            "dgp": f"Y ~ Bern({p}), n={n}",
            "p": p,
            "p0_claim": 0.95,
            "n": n,
            "observed_rate": float(y.mean()),
        },
    )


def sim_poisson_counts(seed: int = 5) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    lambdas = [0.3, 1.0, 2.5]
    values = np.concatenate([rng.poisson(lam, size=40) for lam in lambdas]).astype(float)
    strata = np.repeat(np.arange(3), 40)
    return SimulatedDataset(
        "sim_poisson_count_hetero",
        "count",
        "Poisson counts with day-dependent lambda (blood-cell-like low counts).",
        ["count", "heterogeneity"],
        values=values,
        strata=strata,
        meta={
            "seed": seed,
            "dgp": "day d: X ~ Poisson(lambda_d), lambda=(0.3,1.0,2.5), n=40/day",
            "lambdas": lambdas,
        },
    )


def sim_multiclass_blood_type(seed: int = 6, n: int = 200) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    probs = np.array([0.98, 0.007, 0.007, 0.006])
    true_class = 0
    draws = rng.choice(4, size=n, p=probs)
    success = (draws == true_class).astype(float)
    return SimulatedDataset(
        "sim_multiclass_blood_type",
        "multiclass",
        "ABO typing with 98% correct class probability (success = correct_class).",
        ["multiclass"],
        values=success,
        strata=draws.astype(int),
        meta={
            "seed": seed,
            "dgp": f"class ~ Categorical({probs.tolist()}); success=(class=={true_class})",
            "probs": probs.tolist(),
            "true_class": true_class,
            "success_definition": "correct_class",
            "n_classes": 4,
            "p_success": float(probs[true_class]),
            "n": n,
            "observed_success_rate": float(success.mean()),
        },
    )


def sim_bimodal_weak_positive(seed: int = 7) -> SimulatedDataset:
    rng = np.random.default_rng(seed)
    neg = rng.normal(0.1, 0.05, size=70)
    weak = rng.normal(0.8, 0.15, size=30)
    values = np.concatenate([neg, weak])
    return SimulatedDataset(
        "sim_bimodal_weak_positive",
        "continuous",
        "Mixture of negatives and weak positives near cutoff (bimodality).",
        ["mixture", "challenges_C2"],
        values=values,
        strata=np.array([0] * 70 + [1] * 30),
        meta={
            "seed": seed,
            "dgp": "0.7*N(0.1,0.05^2) + 0.3*N(0.8,0.15^2)",
            "mixture_weights": [0.7, 0.3],
        },
    )


ALL_SIMULATORS = [
    sim_normal_blanks,
    sim_skewed_hetero_blanks,
    sim_censored_floor,
    sim_binary_reagents_90_vs_80,
    sim_binary_low_p,
    sim_poisson_counts,
    sim_multiclass_blood_type,
    sim_bimodal_weak_positive,
]


def generate_all_simulated(seed_base: int = 0) -> list[SimulatedDataset]:
    datasets = []
    for i, fn in enumerate(ALL_SIMULATORS):
        ds = fn(seed=seed_base + i)
        ds.to_disk()
        datasets.append(ds)
    # write DGP catalogue
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    catalog = {
        "evidence_tier": "S_simulation_stress",
        "disclaimer": (
            "These DGPs are mechanism/stress tests with known truth. "
            "They do not replace multi-assay real raw LoD deposits."
        ),
        "datasets": [
            {
                "dataset_id": d.dataset_id,
                "result_type": d.result_type,
                "dgp": (d.meta or {}).get("dgp"),
                "seed": (d.meta or {}).get("seed"),
                "sha256_payload": (d.meta or {}).get("sha256_payload"),
            }
            for d in datasets
        ],
    }
    # refresh sha after to_disk updated meta
    refreshed = []
    for d in datasets:
        p = SIM_DIR / f"{d.dataset_id}.json"
        payload = json.loads(p.read_text(encoding="utf-8"))
        refreshed.append(
            {
                "dataset_id": d.dataset_id,
                "result_type": d.result_type,
                "dgp": (payload.get("meta") or {}).get("dgp"),
                "seed": (payload.get("meta") or {}).get("seed"),
                "sha256_payload": (payload.get("meta") or {}).get("sha256_payload"),
            }
        )
    catalog["datasets"] = refreshed
    (SIM_DIR / "dgp_catalogue.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return datasets


if __name__ == "__main__":
    for ds in generate_all_simulated():
        print(ds.dataset_id, ds.result_type, (ds.meta or {}).get("dgp", "")[:60])
