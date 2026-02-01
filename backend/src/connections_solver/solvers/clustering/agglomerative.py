"""Agglomerative (hierarchical) clustering for Connections puzzles."""

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from typing import Tuple


def cluster(embeddings: np.ndarray, n_clusters: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """Apply Agglomerative clustering.

    Best for: Hierarchical structure, non-spherical clusters.

    Args:
        embeddings: Word embeddings (16, dim)
        n_clusters: Number of clusters (always 4 for Connections)

    Returns:
        labels: Cluster assignments (16,)
        centers: Cluster centroids (4, dim)

    Parameters:
        linkage='ward': Minimizes variance when merging clusters.
                        Ward linkage works well with Euclidean distances.
                        Alternatives: 'average' (mean of pairwise distances),
                                     'complete' (max pairwise distance),
                                     'single' (min pairwise distance).
                        Ward is chosen because it creates balanced, compact clusters.
    """
    agg = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage='ward'  # Minimize within-cluster variance when merging
    )
    labels = agg.fit_predict(embeddings)

    # Calculate centroids manually using vectorized operations (Agglomerative doesn't provide them)
    centers = np.zeros((n_clusters, embeddings.shape[1]))
    for i in range(n_clusters):
        mask = labels == i
        centers[i] = embeddings[mask].mean(axis=0)

    return labels, centers
