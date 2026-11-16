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
from matplotlib.colors import BoundaryNorm, ListedColormap
from sklearn.cluster import KMeans

from .constants import CLUSTER_NAMES, ClusteringMethod, NO_INFLUENCE_LABEL


_CLUSTER_COLOR_MAP = ListedColormap(
    [
        "#d9d9d9",  # No influence
        "#d9f0d3",  # Low
        "#addd8e",  # Low-to-Medium
        "#fdae61",  # Medium-to-High
        "#d73027",  # High
    ]
)

_CLUSTER_BOUNDARIES = BoundaryNorm(np.arange(-0.5, 5.5, 1), _CLUSTER_COLOR_MAP.N)


@dataclass(slots=True)
class ClusteringResult:
    total_matrix: np.ndarray
    labels_numeric: np.ndarray
    labels_named: np.ndarray
    cluster_centers: np.ndarray
    cluster_rank_map: dict[int, str]
    factor_names: list[str] | None = None

    @property
    def label_matrix(self) -> np.ndarray:
        return self.labels_named


def _normalize_method(method: str | ClusteringMethod) -> str:
    return method.value if hasattr(method, "value") else str(method).strip().lower().replace(" ", "_")


def _validate_total_matrix(total_matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(total_matrix, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("total_matrix must be a square matrix.")

    if matrix.shape[0] == 0:
        raise ValueError("total_matrix cannot be empty.")

    return matrix


def _fit_clustering(
    cell_values: np.ndarray,
    method: str | ClusteringMethod = ClusteringMethod.KMEANS,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    method_name = _normalize_method(method)

    if method_name != ClusteringMethod.KMEANS.value:
        raise ValueError(f"Unsupported clustering method: {method_name}. Only 'kmeans' is supported.")

    samples = np.asarray(cell_values, dtype=float).reshape(-1, 1)

    if samples.shape[0] < 4:
        raise ValueError("At least 4 off-diagonal matrix values are required for 4-group clustering.")

    model = KMeans(n_clusters=4, random_state=random_state, n_init="auto")
    labels_numeric = model.fit_predict(samples)

    return labels_numeric, model.cluster_centers_.ravel()


def _rank_clusters_by_intensity(cluster_centers: np.ndarray) -> dict[int, str]:
    ordered_cluster_ids = np.argsort(np.asarray(cluster_centers, dtype=float))

    return {
        int(cluster_id): CLUSTER_NAMES[rank]
        for rank, cluster_id in enumerate(ordered_cluster_ids)
    }


def _build_label_matrices(
    matrix: np.ndarray,
    diagonal_mask: np.ndarray,
    labels_numeric_flat: np.ndarray,
    cluster_rank_map: dict[int, str],
) -> tuple[np.ndarray, np.ndarray]:
    numeric_labels = np.full(matrix.shape, -1, dtype=int)
    numeric_labels[diagonal_mask] = labels_numeric_flat

    named_labels = np.full(matrix.shape, NO_INFLUENCE_LABEL, dtype=object)
    named_labels[diagonal_mask] = [cluster_rank_map[int(label)] for label in labels_numeric_flat]

    return numeric_labels, named_labels


def cluster_total_matrix(
    total_matrix: np.ndarray,
    factor_names: list[str] | None = None,
    method: str | ClusteringMethod = ClusteringMethod.KMEANS,
    random_state: int = 42,
) -> ClusteringResult:
    matrix = _validate_total_matrix(total_matrix)

    if factor_names is not None and len(factor_names) != matrix.shape[0]:
        raise ValueError("factor_names length must match total_matrix size.")

    diagonal_mask = ~np.eye(matrix.shape[0], dtype=bool)
    cell_values = matrix[diagonal_mask]

    labels_numeric_flat, cluster_centers = _fit_clustering(
        cell_values=cell_values,
        method=method,
        random_state=random_state,
    )

    cluster_rank_map = _rank_clusters_by_intensity(cluster_centers)
    labels_numeric, labels_named = _build_label_matrices(
        matrix=matrix,
        diagonal_mask=diagonal_mask,
        labels_numeric_flat=labels_numeric_flat,
        cluster_rank_map=cluster_rank_map,
    )

    return ClusteringResult(
        total_matrix=matrix,
        labels_numeric=labels_numeric,
        labels_named=labels_named,
        cluster_centers=np.asarray(cluster_centers, dtype=float),
        cluster_rank_map=cluster_rank_map,
        factor_names=list(factor_names) if factor_names is not None else None,
    )


def _axis_labels(result: ClusteringResult) -> list[str]:
    if result.factor_names is not None:
        return [str(name) for name in result.factor_names]

    return [str(index + 1) for index in range(result.total_matrix.shape[0])]


def _display_codes(numeric_labels: np.ndarray) -> np.ndarray:
    return np.where(numeric_labels < 0, 0, numeric_labels + 1)


def plot_clustered_heatmap(
    clustering_result: ClusteringResult,
    save_path: str | Path | None = None,
    show: bool = True,
    figsize: tuple[float, float] = (10, 8),
    dpi: int = 400,
):
    matrix = _display_codes(clustering_result.labels_numeric)
    labels = _axis_labels(clustering_result)

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(matrix, cmap=_CLUSTER_COLOR_MAP, norm=_CLUSTER_BOUNDARIES, aspect="auto")

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=90)
    ax.set_yticklabels(labels)

    ax.set_title("Clustered Total Relation Matrix Heatmap")
    ax.set_xlabel("Factors")
    ax.set_ylabel("Factors")

    cbar = plt.colorbar(im, ax=ax, ticks=np.arange(5))
    cbar.set_ticklabels([NO_INFLUENCE_LABEL, *CLUSTER_NAMES])
    cbar.set_label("Cluster Label")

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
    flat_labels = np.asarray(clustering_result.labels_named, dtype=object).ravel()
    groups = [NO_INFLUENCE_LABEL, *CLUSTER_NAMES]
    counts = [int(np.sum(flat_labels == group_name)) for group_name in groups]

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(groups, counts, color=["#d9d9d9", "#d9f0d3", "#addd8e", "#fdae61", "#d73027"])

    ax.set_title("Cluster Membership Counts")
    ax.set_ylabel("Number of Cells")
    ax.tick_params(axis="x", rotation=25)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(count),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")

    if show:
        plt.show()

    return fig, ax
