"""DBSCAN clustering for Connections puzzles."""

import numpy as np
from sklearn.cluster import DBSCAN
from typing import Tuple


def cluster(embeddings: np.ndarray, n_clusters: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """Apply DBSCAN clustering.

    Best for: Varying density clusters, presence of noise/outliers.
    Note: DBSCAN doesn't guarantee n_clusters, so this may fall back to K-Means.

    Args:
        embeddings: Word embeddings (16, dim)
        n_clusters: Number of clusters (always 4 for Connections)

    Returns:
        labels: Cluster assignments (16,)
        centers: Cluster centroids (4, dim)

    Parameters:
        eps=0.5: Maximum distance between two samples to be in same neighborhood.
                 For cosine distance in [0, 2], 0.5 means words within 25% dissimilarity
                 are considered neighbors. This is a moderate threshold.
                 Smaller eps = tighter clusters (may create more clusters or noise).
                 Larger eps = looser clusters (may merge categories).
        
        min_samples=2: Minimum points to form a dense region (core point).
                       With 4 words per category, min_samples=2 means at least 2 words
                       must be nearby to start a cluster. This is lenient to avoid
                       marking words as noise.
        
        metric='cosine': Cosine distance works better for high-dim embeddings than
                        Euclidean. Focuses on direction rather than magnitude.
    
    Fallback: If DBSCAN doesn't find exactly 4 clusters (due to noise points or
              different number of clusters), falls back to K-Means which guarantees
              4 clusters.
    """
    dbscan = DBSCAN(
        eps=0.5,  # Max distance for neighborhood (moderate threshold for cosine)
        min_samples=2,  # At least 2 points to form a cluster (lenient)
        metric='cosine'  # Cosine distance for high-dim word embeddings
    )
    labels = dbscan.fit_predict(embeddings)

    # Handle case where DBSCAN finds != 4 clusters
    unique_labels = set(labels)
    if -1 in unique_labels:  # -1 indicates noise points
        unique_labels.remove(-1)

    # If we got exactly 4 clusters, great
    if len(unique_labels) == n_clusters:
        # Calculate centroids using vectorized operations
        centers = np.zeros((n_clusters, embeddings.shape[1]))
        for i in sorted(unique_labels):
            mask = labels == i
            centers[i] = embeddings[mask].mean(axis=0)
        return labels, centers
    else:
        # Fall back to K-Means if DBSCAN doesn't find 4 clusters
        # Import locally to avoid circular imports
        from .kmeans import cluster as kmeans_cluster
        return kmeans_cluster(embeddings, n_clusters)
