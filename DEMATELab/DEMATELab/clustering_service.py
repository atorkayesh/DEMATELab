# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 18:36:56 2026

@author: Ali
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from sklearn.cluster import AgglomerativeClustering, KMeans

from .constants import CLUSTER_NAMES, ClusteringMethod


@dataclass(slots=True)
class ClusteringResult:
    labels_numeric: np.ndarray
    labels_named: list[str]
    ordered_indices: np.ndarray
    ordered_matrix: np.ndarray
    ordered_factor_names: list[str]
    cluster_name_by_factor: dict[str, str]
    cluster_rank_map: dict[int, str]


def _fit_clustering(
    total_matrix: np.ndarray,
    method: str | ClusteringMethod,
    random_state: int = 42,
) -> np.ndarray:
    n_clusters = 4
    method = method.value if hasattr(method, "value") else str(method).strip().lower().replace(" ", "_")

    if total_matrix.ndim != 2 or total_matrix.shape[0] != total_matrix.shape[1]:
        raise ValueError("total_matrix must be a square matrix.")

    n_items = total_matrix.shape[0]
    if n_items < n_clusters:
        raise ValueError("At least 4 factors are required for 4-group clustering.")

    if method == ClusteringMethod.KMEANS.value:
        model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
        return model.fit_predict(total_matrix)

    if method == ClusteringMethod.HIERARCHICAL.value:
        model = AgglomerativeClustering(n_clusters=n_clusters)
        return model.fit_predict(total_matrix)

    raise ValueError(f"Unsupported clustering method: {method}")


def _rank_clusters_by_intensity(
    total_matrix: np.ndarray,
    labels_numeric: np.ndarray,
) -> dict[int, str]:
    unique_clusters = sorted(set(labels_numeric.tolist()))
    cluster_scores: list[tuple[int, float]] = []

    row_means = total_matrix.mean(axis=1)

    for cluster_id in unique_clusters:
        member_mask = labels_numeric == cluster_id
        score = float(row_means[member_mask].mean())
        cluster_scores.append((cluster_id, score))

    cluster_scores.sort(key=lambda x: x[1])

    return {
        cluster_id: CLUSTER_NAMES[rank]
        for rank, (cluster_id, _) in enumerate(cluster_scores)
    }


def cluster_total_matrix(
    total_matrix: np.ndarray,
    factor_names: list[str],
    method: str | ClusteringMethod,
    random_state: int = 42,
) -> ClusteringResult:
    matrix = np.asarray(total_matrix, dtype=float)

    if len(factor_names) != matrix.shape[0]:
        raise ValueError("factor_names length must match total_matrix size.")

    labels_numeric = _fit_clustering(
        total_matrix=matrix,
        method=method,
        random_state=random_state,
    )

    cluster_rank_map = _rank_clusters_by_intensity(matrix, labels_numeric)
    labels_named = [cluster_rank_map[label] for label in labels_numeric]

    order_value = {name: i for i, name in enumerate(CLUSTER_NAMES)}

    ordered_indices = np.array(
        sorted(
            range(len(factor_names)),
            key=lambda i: (order_value[labels_named[i]], factor_names[i].lower()),
        )
    )

    ordered_matrix = matrix[ordered_indices][:, ordered_indices]
    ordered_factor_names = [factor_names[i] for i in ordered_indices]

    cluster_name_by_factor = {
        factor_names[i]: labels_named[i]
        for i in range(len(factor_names))
    }

    return ClusteringResult(
        labels_numeric=labels_numeric,
        labels_named=labels_named,
        ordered_indices=ordered_indices,
        ordered_matrix=ordered_matrix,
        ordered_factor_names=ordered_factor_names,
        cluster_name_by_factor=cluster_name_by_factor,
        cluster_rank_map=cluster_rank_map,
    )


def plot_clustered_heatmap(
    clustering_result: ClusteringResult,
    save_path: str | Path | None = None,
    show: bool = True,
    figsize: tuple[float, float] = (10, 8),
    cmap: str = "YlOrRd",
    dpi: int = 400,
):
    matrix = clustering_result.ordered_matrix
    labels = clustering_result.ordered_factor_names

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=90)
    ax.set_yticklabels(labels)

    ax.set_title("Clustered Total Relation Matrix Heatmap")
    ax.set_xlabel("Factors")
    ax.set_ylabel("Factors")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Relation Strength")

    ordered_group_names = [
        clustering_result.cluster_name_by_factor[name]
        for name in labels
    ]

    boundaries = []
    for i in range(1, len(ordered_group_names)):
        if ordered_group_names[i] != ordered_group_names[i - 1]:
            boundaries.append(i - 0.5)

    for b in boundaries:
        ax.axhline(b, color="black", linewidth=1.2)
        ax.axvline(b, color="black", linewidth=1.2)

    plt.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")

    if show:
        plt.show()

    return fig, ax


def plot_cluster_membership_bar(
    clustering_result: ClusteringResult,
    save_path: str | Path | None = None,
    show: bool = True,
    figsize: tuple[float, float] = (10, 4),
    dpi: int = 300,
):
    ordered_names = clustering_result.ordered_factor_names
    ordered_groups = [
        clustering_result.cluster_name_by_factor[name]
        for name in ordered_names
    ]

    group_to_num = {name: i for i, name in enumerate(CLUSTER_NAMES)}
    values = [group_to_num[g] for g in ordered_groups]

    cmap = ListedColormap(["#d9f0d3", "#addd8e", "#fdae61", "#d73027"])

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(np.array([values]), aspect="auto", cmap=cmap)

    ax.set_xticks(np.arange(len(ordered_names)))
    ax.set_xticklabels(ordered_names, rotation=90)
    ax.set_yticks([])
    ax.set_title("Cluster Membership")

    for i, group_name in enumerate(ordered_groups):
        ax.text(i, 0, group_name, ha="center", va="center", fontsize=8)

    plt.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")

    if show:
        plt.show()

    return fig, ax