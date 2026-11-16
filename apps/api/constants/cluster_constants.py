"""Clustering settings and cluster heatmap colours (`clustering_service.py`, `results_viewer_widget.py:1091`)."""

from typing import List

CLUSTER_NAMES: List[str] = ["Low", "Low-to-Medium", "Medium-to-High", "High"]

CLUSTER_SETTINGS = {
    "N_CLUSTERS": 4,
    "RANDOM_STATE": 42,
    "N_INIT": "auto",
    "MIN_VALUES": 4,
    "DIAGONAL_CODE": -1,
}

# Display colours: "No influence" (diagonal) first, then the clusters from Low to High.
CLUSTER_COLORS: List[str] = ["#d9d9d9", "#d9f0d3", "#addd8e", "#fdae61", "#d73027"]
