"""K-Means clustering for Connections puzzles."""

import numpy as np
from sklearn.cluster import KMeans as SKLearnKMeans
from typing import Tuple


def cluster(embeddings: np.ndarray, n_clusters: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """Apply K-Means clustering.

    Best for: Spherical, well-separated clusters.

    Args:
        embeddings: Word embeddings (16, dim)
        n_clusters: Number of clusters (always 4 for Connections)

    Returns:
        labels: Cluster assignments (16,)
        centers: Cluster centroids (4, dim)

    Parameters:
        n_init=10: Number of times to run K-Means with different centroid seeds.
                   Sklearn default is 10. This helps avoid local minima.
                   Higher values = more robust but slower.
        random_state=42: Fixed seed for reproducibility in testing.
    """
    kmeans = SKLearnKMeans(
        n_clusters=n_clusters,
        n_init=10,  # Run 10 times with different seeds, return best result
        random_state=42  # Fixed seed for reproducible results
    )
    labels = kmeans.fit_predict(embeddings)
    centers = kmeans.cluster_centers_
    return labels, centers
