# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:40:14 2026

@author: Ali
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Sequence

import numpy as np


@dataclass(slots=True)
class MMDEResult:
    threshold: float
    best_dispatch_prefix: tuple[int, ...]
    best_receiver_prefix: tuple[int, ...]
    best_dispatch_nodes: list[int]
    best_receiver_nodes: list[int]
    selected_pairs: list[tuple[int, int, float]]
    dispatch_scores: list[float]
    receiver_scores: list[float]


def _entropy(probabilities: Sequence[float]) -> float:
    return -sum(p * log(p) for p in probabilities if p > 0)


def _max_entropy_from_unique_count(unique_count: int) -> float:
    if unique_count <= 0:
        return 0.0
    uniform_probability = 1.0 / unique_count
    return -unique_count * (uniform_probability * log(uniform_probability))


def _prefixes(values: list[int]) -> list[tuple[int, ...]]:
    return [tuple(values[:k]) for k in range(1, len(values) + 1)]


def _probabilities_of_prefix(prefix: Sequence[int]) -> list[float]:
    unique_values = set(prefix)
    length = len(prefix)
    return [prefix.count(value) / length for value in unique_values]


def _mean_deentropy(prefix: Sequence[int]) -> float:
    unique_count = len(set(prefix))
    if unique_count == 0:
        return 0.0

    probabilities = _probabilities_of_prefix(prefix)
    entropy_value = _entropy(probabilities)
    max_entropy_value = _max_entropy_from_unique_count(unique_count)
    deentropy_value = max_entropy_value - entropy_value

    return deentropy_value / unique_count


def _sorted_edges_desc(matrix: np.ndarray) -> list[tuple[float, int, int]]:
    n = matrix.shape[0]
    edges: list[tuple[float, int, int]] = []

    for i in range(n):
        for j in range(n):
            edges.append((float(matrix[i, j]), i + 1, j + 1))

    edges.sort(key=lambda x: x[0], reverse=True)
    return edges


def _score_prefixes(node_sequence: list[int]) -> tuple[list[tuple[int, ...]], list[float], tuple[int, ...]]:
    prefixes = _prefixes(node_sequence)
    scores = [_mean_deentropy(prefix) for prefix in prefixes]
    best_prefix = prefixes[int(np.argmax(scores))]
    return prefixes, scores, best_prefix


def _extract_selected_pairs(
    matrix: np.ndarray,
    dispatch_nodes_1based: Sequence[int],
    receiver_nodes_1based: Sequence[int],
) -> list[tuple[int, int, float]]:
    pairs: list[tuple[int, int, float]] = []

    for d in dispatch_nodes_1based:
        for r in receiver_nodes_1based:
            value = float(matrix[d - 1, r - 1])
            pairs.append((d, r, value))

    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs


def compute_mmde_threshold(total_matrix: np.ndarray) -> MMDEResult:
    matrix = np.asarray(total_matrix, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("MMDE requires a square matrix.")

    sorted_edges = _sorted_edges_desc(matrix)

    dispatch_sequence = [edge[1] for edge in sorted_edges]
    receiver_sequence = [edge[2] for edge in sorted_edges]

    _, dispatch_scores, best_dispatch_prefix = _score_prefixes(dispatch_sequence)
    _, receiver_scores, best_receiver_prefix = _score_prefixes(receiver_sequence)

    best_dispatch_nodes = sorted(set(best_dispatch_prefix))
    best_receiver_nodes = sorted(set(best_receiver_prefix))

    selected_pairs = _extract_selected_pairs(
        matrix=matrix,
        dispatch_nodes_1based=best_dispatch_nodes,
        receiver_nodes_1based=best_receiver_nodes,
    )

    if not selected_pairs:
        raise ValueError("MMDE could not identify any pair values.")

    threshold = min(value for _, _, value in selected_pairs)

    return MMDEResult(
        threshold=float(threshold),
        best_dispatch_prefix=best_dispatch_prefix,
        best_receiver_prefix=best_receiver_prefix,
        best_dispatch_nodes=best_dispatch_nodes,
        best_receiver_nodes=best_receiver_nodes,
        selected_pairs=selected_pairs,
        dispatch_scores=dispatch_scores,
        receiver_scores=receiver_scores,
    )