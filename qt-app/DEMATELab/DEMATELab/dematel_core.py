# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:32:58 2026

@author: Ali
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .constants import DEFAULT_LINGUISTIC_MAP, ThresholdMethod
from .mmde_service import compute_mmde_threshold


@dataclass(slots=True)
class ExpertInput:
    name: str
    weight: float
    matrix: np.ndarray


@dataclass(slots=True)
class DematelResult:
    factors: list[str]
    expert_weights: list[float]
    direct_matrix: np.ndarray
    normalized_matrix: np.ndarray
    total_matrix: np.ndarray
    r: np.ndarray
    c: np.ndarray
    prominence: np.ndarray
    relation: np.ndarray
    cause_group: list[str]
    effect_group: list[str]
    threshold_method: str | None = None
    threshold_value: float | None = None


def linguistic_to_numeric_matrix(
    matrix: Sequence[Sequence[str]],
    mapping: dict[str, float] | None = None,
) -> np.ndarray:
    scale_map = mapping or DEFAULT_LINGUISTIC_MAP

    try:
        numeric = np.array(
            [[scale_map[str(cell).strip()] for cell in row] for row in matrix],
            dtype=float,
        )
    except KeyError as exc:
        raise ValueError(
            f"Unknown linguistic value found: {exc}. "
            f"Allowed values are: {list(scale_map.keys())}"
        ) from exc

    if numeric.ndim != 2 or numeric.shape[0] != numeric.shape[1]:
        raise ValueError("Linguistic matrix must be square.")

    return numeric


class DematelEngine:
    def __init__(self, factors: Sequence[str], experts: Sequence[ExpertInput]) -> None:
        self.factors = [str(f).strip() for f in factors]
        self.experts = list(experts)
        self._validate()

    def _validate(self) -> None:
        if not self.factors:
            raise ValueError("Factors list cannot be empty.")

        n = len(self.factors)

        if not self.experts:
            raise ValueError("At least one expert must be provided.")

        weights = [expert.weight for expert in self.experts]

        if any(w < 0 or w > 1 for w in weights):
            raise ValueError("Each expert weight must be between 0 and 1.")

        if not np.isclose(sum(weights), 1.0, atol=1e-8):
            raise ValueError("Expert weights must sum to 1.")

        for expert in self.experts:
            if expert.matrix.shape != (n, n):
                raise ValueError(
                    f"Matrix for expert '{expert.name}' must have shape ({n}, {n})."
                )

    @property
    def expert_weights(self) -> list[float]:
        return [expert.weight for expert in self.experts]

    def build_weighted_direct_matrix(self) -> np.ndarray:
        n = len(self.factors)
        weighted_matrix = np.zeros((n, n), dtype=float)

        for expert in self.experts:
            weighted_matrix += expert.weight * expert.matrix

        return weighted_matrix

    @staticmethod
    def normalize_matrix(direct_matrix: np.ndarray) -> np.ndarray:
        row_sums = direct_matrix.sum(axis=1)
        col_sums = direct_matrix.sum(axis=0)
        scale = max(row_sums.max(), col_sums.max())

        if np.isclose(scale, 0.0):
            raise ValueError("All matrix cells are set to \"No influence\". Please assign at least one causal relationship before running the analysis.")

        return direct_matrix / scale

    @staticmethod
    def total_relation_matrix(normalized_matrix: np.ndarray) -> np.ndarray:
        n = normalized_matrix.shape[0]
        identity = np.eye(n)

        try:
            inverse_term = np.linalg.inv(identity - normalized_matrix)
        except np.linalg.LinAlgError as exc:
            raise ValueError("Failed to invert (I - X). Check the input matrices.") from exc

        return normalized_matrix @ inverse_term

    @staticmethod
    def prominence_and_relation(
        total_matrix: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        r = total_matrix.sum(axis=1)
        c = total_matrix.sum(axis=0)
        prominence = r + c
        relation = r - c
        return r, c, prominence, relation

    @staticmethod
    def split_cause_effect(
        factors: Sequence[str],
        relation: np.ndarray,
    ) -> tuple[list[str], list[str]]:
        cause_group = [factor for factor, value in zip(factors, relation) if value >= 0]
        effect_group = [factor for factor, value in zip(factors, relation) if value < 0]
        return cause_group, effect_group

    def compute_threshold(
        self,
        total_matrix: np.ndarray,
        method: ThresholdMethod,
    ) -> float:
        values = total_matrix.flatten()

        if values.size == 0:
            raise ValueError("Threshold calculation requires matrix values.")

        if method == ThresholdMethod.AVERAGE:
            return float(np.mean(values))

        if method == ThresholdMethod.FIRST_QUARTILE:
            return float(np.quantile(values, 0.25))

        if method == ThresholdMethod.MEDIAN:
            return float(np.median(values))

        if method == ThresholdMethod.THIRD_QUARTILE:
            return float(np.quantile(values, 0.75))

        if method == ThresholdMethod.MMDE:
            return float(compute_mmde_threshold(total_matrix).threshold)

        raise ValueError(f"Unsupported threshold method: {method}")

    def solve(self, threshold_method: ThresholdMethod | None = None) -> DematelResult:
        direct_matrix = self.build_weighted_direct_matrix()
        normalized_matrix = self.normalize_matrix(direct_matrix)
        total_matrix = self.total_relation_matrix(normalized_matrix)
        r, c, prominence, relation = self.prominence_and_relation(total_matrix)
        cause_group, effect_group = self.split_cause_effect(self.factors, relation)

        threshold_value = None
        threshold_name = None

        if threshold_method is not None:
            threshold_value = self.compute_threshold(total_matrix, threshold_method)
            threshold_name = threshold_method.value

        return DematelResult(
            factors=self.factors,
            expert_weights=self.expert_weights,
            direct_matrix=direct_matrix,
            normalized_matrix=normalized_matrix,
            total_matrix=total_matrix,
            r=r,
            c=c,
            prominence=prominence,
            relation=relation,
            cause_group=cause_group,
            effect_group=effect_group,
            threshold_method=threshold_name,
            threshold_value=threshold_value,
        )
