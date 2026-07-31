"""
S1 — Classify assay result type and route to the admissible single-trial family.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResultType(str, Enum):
    BINARY = "binary"
    CONTINUOUS = "continuous"
    COUNT = "count"
    MULTICLASS = "multiclass"


RESULT_TYPE_MODELS: dict[ResultType, str] = {
    ResultType.BINARY: "Bernoulli / logistic (concentration → detection probability)",
    ResultType.CONTINUOUS: "Location-scale or distributional (normal / lognormal / gamma)",
    ResultType.COUNT: "Poisson / negative binomial",
    ResultType.MULTICLASS: "Categorical; success event must be defined first",
}


@dataclass(frozen=True)
class ResultTypeSpec:
    result_type: ResultType
    n_classes: int | None = None  # for multiclass
    success_definition: str | None = None  # e.g. correct_class, detect_target

    def validate(self) -> None:
        if self.result_type == ResultType.MULTICLASS:
            if self.n_classes is None or self.n_classes < 2:
                raise ValueError("multiclass requires n_classes >= 2")
            if not self.success_definition:
                raise ValueError(
                    "multiclass requires success_definition "
                    "(correct_class | detect_target | any_non_null)"
                )


def classify_result_type(
    result_type: ResultType | str,
    *,
    n_classes: int | None = None,
    success_definition: str | None = None,
) -> ResultTypeSpec:
    """S1 entry point."""
    rt = ResultType(result_type) if isinstance(result_type, str) else result_type
    spec = ResultTypeSpec(
        result_type=rt,
        n_classes=n_classes,
        success_definition=success_definition,
    )
    spec.validate()
    return spec
