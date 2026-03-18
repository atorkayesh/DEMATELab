# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:55:33 2026

@author: Ali
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .constants import DEFAULT_FUZZY_LINGUISTIC_MAP, ThresholdMethod


@dataclass(slots=True)
class FuzzyExpertInput:
    name: str
    weight: float
    matrix: np.ndarray


@dataclass(slots=True)
class FuzzyDematelResult:
    factors: list[str]
    expert_weights: list[float]
    fuzzy_direct_matrix: np.ndarray
    fuzzy_normalized_matrix: np.ndarray
    fuzzy_total_matrix: np.ndarray
    fuzzy_r: np.ndarray
    fuzzy_c: np.ndarray
    fuzzy_prominence: np.ndarray
    fuzzy_relation: np.ndarray
    r: np.ndarray
    c: np.ndarray
    prominence: np.ndarray
    relation: np.ndarray
    cause_group: list[str]
    effect_group: list[str]
    threshold_method: str | None = None
    threshold_value: float | None = None


def linguistic_to_fuzzy_matrix(
    matrix: Sequence[Sequence[str]],
    mapping: dict[str, tuple[float, float, float]] | None = None,
) -> np.ndarray:
    scale_map = mapping or DEFAULT_FUZZY_LINGUISTIC_MAP

    try:
        fuzzy = np.array(
            [[scale_map[str(cell).strip()] for cell in row] for row in matrix],
            dtype=float,
        )
    except KeyError as exc:
        raise ValueError(
            f"Unknown linguistic value found: {exc}. "
            f"Allowed values are: {list(scale_map.keys())}"
        ) from exc

    if fuzzy.ndim != 3 or fuzzy.shape[0] != fuzzy.shape[1] or fuzzy.shape[2] != 3:
        raise ValueError("Fuzzy linguistic matrix must have shape (n, n, 3).")

    return fuzzy


def defuzzify_triangular_values(values: np.ndarray) -> np.ndarray:
    if values.ndim == 1 and values.shape[0] == 3:
        l, m, u = values
        return np.array(l + ((u - l) + (m - l)) / 3, dtype=float)

    if values.ndim == 2 and values.shape[1] == 3:
        l = values[:, 0]
        m = values[:, 1]
        u = values[:, 2]
        return l + ((u - l) + (m - l)) / 3

    if values.ndim == 3 and values.shape[2] == 3:
        l = values[:, :, 0]
        m = values[:, :, 1]
        u = values[:, :, 2]
        return l + ((u - l) + (m - l)) / 3

    raise ValueError("Input must be triangular fuzzy values with last dimension size 3.")


def _fuzzy_add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Triangular fuzzy addition:
    (l1, m1, u1) + (l2, m2, u2) = (l1+l2, m1+m2, u1+u2)
    """
    result = np.zeros_like(a, dtype=float)
    result[:, 0] = a[:, 0] + b[:, 0]
    result[:, 1] = a[:, 1] + b[:, 1]
    result[:, 2] = a[:, 2] + b[:, 2]
    return result


def _fuzzy_subtract(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Triangular fuzzy subtraction:
    (l1, m1, u1) - (l2, m2, u2) = (l1-u2, m1-m2, u1-l2)
    """
    result = np.zeros_like(a, dtype=float)
    result[:, 0] = a[:, 0] - b[:, 2]
    result[:, 1] = a[:, 1] - b[:, 1]
    result[:, 2] = a[:, 2] - b[:, 0]
    return result


class FuzzyDematelEngine:
    def __init__(self, factors: Sequence[str], experts: Sequence[FuzzyExpertInput]) -> None:
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
            if expert.matrix.shape != (n, n, 3):
                raise ValueError(
                    f"Matrix for expert '{expert.name}' must have shape ({n}, {n}, 3)."
                )

            lower = expert.matrix[:, :, 0]
            middle = expert.matrix[:, :, 1]
            upper = expert.matrix[:, :, 2]

            if np.any(lower > middle) or np.any(middle > upper):
                raise ValueError(
                    f"Fuzzy matrix for expert '{expert.name}' must satisfy l <= m <= u."
                )

    @property
    def expert_weights(self) -> list[float]:
        return [expert.weight for expert in self.experts]

    def build_weighted_fuzzy_direct_matrix(self) -> np.ndarray:
        n = len(self.factors)
        weighted_matrix = np.zeros((n, n, 3), dtype=float)

        for expert in self.experts:
            weighted_matrix += expert.weight * expert.matrix

        np.fill_diagonal(weighted_matrix[:, :, 0], 0.0)
        np.fill_diagonal(weighted_matrix[:, :, 1], 0.0)
        np.fill_diagonal(weighted_matrix[:, :, 2], 0.0)

        return weighted_matrix

    @staticmethod
    def normalize_fuzzy_matrix(fuzzy_direct_matrix: np.ndarray) -> np.ndarray:
        upper_matrix = fuzzy_direct_matrix[:, :, 2]
        row_sums = upper_matrix.sum(axis=1)
        col_sums = upper_matrix.sum(axis=0)
        scale = max(row_sums.max(), col_sums.max())

        if np.isclose(scale, 0.0):
            raise ValueError("Normalization failed because the fuzzy direct matrix is all zeros.")

        return fuzzy_direct_matrix / scale

    @staticmethod
    def total_fuzzy_relation_matrix(fuzzy_normalized_matrix: np.ndarray) -> np.ndarray:
        n = fuzzy_normalized_matrix.shape[0]
        identity = np.eye(n)

        xl = fuzzy_normalized_matrix[:, :, 0]
        xm = fuzzy_normalized_matrix[:, :, 1]
        xu = fuzzy_normalized_matrix[:, :, 2]

        try:
            tl = xl @ np.linalg.inv(identity - xl)
            tm = xm @ np.linalg.inv(identity - xm)
            tu = xu @ np.linalg.inv(identity - xu)
        except np.linalg.LinAlgError as exc:
            raise ValueError("Failed to invert (I - X) for fuzzy DEMATEL.") from exc

        total_matrix = np.zeros((n, n, 3), dtype=float)
        total_matrix[:, :, 0] = tl
        total_matrix[:, :, 1] = tm
        total_matrix[:, :, 2] = tu

        return total_matrix

    @staticmethod
    def fuzzy_prominence_and_relation(
        fuzzy_total_matrix: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        fuzzy_r = np.zeros((fuzzy_total_matrix.shape[0], 3), dtype=float)
        fuzzy_c = np.zeros((fuzzy_total_matrix.shape[0], 3), dtype=float)

        fuzzy_r[:, 0] = fuzzy_total_matrix[:, :, 0].sum(axis=1)
        fuzzy_r[:, 1] = fuzzy_total_matrix[:, :, 1].sum(axis=1)
        fuzzy_r[:, 2] = fuzzy_total_matrix[:, :, 2].sum(axis=1)

        fuzzy_c[:, 0] = fuzzy_total_matrix[:, :, 0].sum(axis=0)
        fuzzy_c[:, 1] = fuzzy_total_matrix[:, :, 1].sum(axis=0)
        fuzzy_c[:, 2] = fuzzy_total_matrix[:, :, 2].sum(axis=0)

        fuzzy_prominence = _fuzzy_add(fuzzy_r, fuzzy_c)
        fuzzy_relation = _fuzzy_subtract(fuzzy_r, fuzzy_c)

        return fuzzy_r, fuzzy_c, fuzzy_prominence, fuzzy_relation

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
        defuzzified_total_matrix: np.ndarray,
        method: ThresholdMethod,
    ) -> float:
        values = defuzzified_total_matrix.flatten()

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
            from .mmde_service import compute_mmde_threshold
            return float(compute_mmde_threshold(defuzzified_total_matrix).threshold)

        raise ValueError(f"Unsupported threshold method: {method}")

    def solve(self, threshold_method: ThresholdMethod | None = None) -> FuzzyDematelResult:
        fuzzy_direct_matrix = self.build_weighted_fuzzy_direct_matrix()
        fuzzy_normalized_matrix = self.normalize_fuzzy_matrix(fuzzy_direct_matrix)
        fuzzy_total_matrix = self.total_fuzzy_relation_matrix(fuzzy_normalized_matrix)

        fuzzy_r, fuzzy_c, fuzzy_prominence, fuzzy_relation = self.fuzzy_prominence_and_relation(
            fuzzy_total_matrix
        )

        r = defuzzify_triangular_values(fuzzy_r)
        c = defuzzify_triangular_values(fuzzy_c)
        prominence = defuzzify_triangular_values(fuzzy_prominence)
        relation = defuzzify_triangular_values(fuzzy_relation)

        cause_group, effect_group = self.split_cause_effect(self.factors, relation)

        defuzzified_total_matrix = defuzzify_triangular_values(fuzzy_total_matrix)

        threshold_value = None
        threshold_name = None

        if threshold_method is not None:
            threshold_value = self.compute_threshold(defuzzified_total_matrix, threshold_method)
            threshold_name = threshold_method.value

        return FuzzyDematelResult(
            factors=self.factors,
            expert_weights=self.expert_weights,
            fuzzy_direct_matrix=fuzzy_direct_matrix,
            fuzzy_normalized_matrix=fuzzy_normalized_matrix,
            fuzzy_total_matrix=fuzzy_total_matrix,
            fuzzy_r=fuzzy_r,
            fuzzy_c=fuzzy_c,
            fuzzy_prominence=fuzzy_prominence,
            fuzzy_relation=fuzzy_relation,
            r=r,
            c=c,
            prominence=prominence,
            relation=relation,
            cause_group=cause_group,
            effect_group=effect_group,
            threshold_method=threshold_name,
            threshold_value=threshold_value,
        )