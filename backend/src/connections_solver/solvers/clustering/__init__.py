"""Clustering package for Connections puzzle solving.

This package provides:
- Data analysis to recommend clustering algorithms
- Multiple clustering algorithm implementations
- Routing to appropriate algorithm
- Utilities for post-processing
"""

from typing import Tuple
import numpy as np

from . import kmeans
from . import agglomerative
from . import dbscan


# Algorithm registry
ALGORITHMS = {
    'kmeans': kmeans.cluster,
    'agglomerative': agglomerative.cluster,
    'dbscan': dbscan.cluster,
}


def cluster(
    embeddings: np.ndarray,
    algorithm: str,
    n_clusters: int = 4
) -> Tuple[np.ndarray, np.ndarray]:
    """Route to appropriate clustering algorithm.

    Args:
        embeddings: Word embeddings (16, dim)
        algorithm: Algorithm name ('kmeans', 'agglomerative', 'dbscan')
        n_clusters: Number of clusters (default: 4)

    Returns:
        labels: Cluster assignments (16,)
        centers: Cluster centroids (4, dim)

    Raises:
        ValueError: If algorithm not recognized
    """
    if algorithm not in ALGORITHMS:
        raise ValueError(
            f"Unknown algorithm: {algorithm}. "
            f"Available: {list(ALGORITHMS.keys())}"
        )

    cluster_fn = ALGORITHMS[algorithm]
    return cluster_fn(embeddings, n_clusters)


__all__ = ['cluster', 'ALGORITHMS']
