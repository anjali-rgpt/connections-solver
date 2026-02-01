"""Utilities for enforcing Connections game constraints."""

import numpy as np
from typing import List
from scipy.spatial.distance import cdist


def enforce_equal_clusters(
    words: List[str],
    embeddings: np.ndarray,
    labels: np.ndarray,
    centers: np.ndarray,
    distance_metric: str = 'cosine'
) -> np.ndarray:
    """Reassign words to create exactly 4 words per cluster.

    Args:
        words: List of 16 words
        embeddings: Word embeddings (16, dim)
        labels: Initial cluster assignments (16,)
        centers: Cluster centroids (4, dim)
        distance_metric: 'cosine' or 'euclidean'

    Returns:
        Adjusted labels with exactly 4 words per cluster

    Algorithm:
        1. Count words per cluster
        2. While any cluster has != 4 words:
           a. Find over-full cluster (>4 words)
           b. Find word furthest from its cluster center
           c. Find under-full cluster closest to that word
           d. Reassign word to that cluster
        3. Repeat until balanced

    Rationale:
        - Simple greedy approach
        - Preserves clustering structure (only moves outliers)
        - Deterministic and explainable
        - Fast: O(n log n) for sorting
    """
    labels = labels.copy()  # Don't modify original
    n_clusters = 4
    target_size = 4

    # Calculate distances from each word to each cluster center once (optimization)
    distances = cdist(embeddings, centers, metric=distance_metric)

    # max_iterations=20: Safety limit to prevent infinite loops
    # With 16 words and 4 clusters, worst case is ~12 reassignments
    # (if one cluster has all 16 words, need 12 moves to balance)
    # 20 iterations provides comfortable margin
    max_iterations = 20
    for _ in range(max_iterations):
        # Count cluster sizes
        cluster_sizes = np.bincount(labels, minlength=n_clusters)

        # Check if balanced
        if np.all(cluster_sizes == target_size):
            break

        # Find over-full and under-full clusters
        overfull = np.where(cluster_sizes > target_size)[0]
        underfull = np.where(cluster_sizes < target_size)[0]

        if len(overfull) == 0 or len(underfull) == 0:
            break  # Shouldn't happen, but safety check

        # Pick first over-full cluster
        from_cluster = overfull[0]

        # Find words in this cluster using boolean mask (faster than where)
        mask = labels == from_cluster
        words_in_cluster = np.flatnonzero(mask)

        # Find furthest word from cluster center
        cluster_distances = distances[words_in_cluster, from_cluster]
        furthest_word_local_idx = np.argmax(cluster_distances)
        furthest_word_idx = words_in_cluster[furthest_word_local_idx]

        # Find nearest under-full cluster to this word
        word_to_clusters = distances[furthest_word_idx, underfull]
        nearest_underfull_idx = np.argmin(word_to_clusters)
        to_cluster = underfull[nearest_underfull_idx]

        # Reassign
        labels[furthest_word_idx] = to_cluster

    # Verify result
    final_sizes = np.bincount(labels, minlength=n_clusters)
    if not np.all(final_sizes == target_size):
        raise ValueError(f"Failed to balance clusters: {final_sizes}")

    return labels


def calculate_confidence(
    cluster_embeddings: np.ndarray,
    center: np.ndarray,
    distance_metric: str = 'cosine'
) -> float:
    """Calculate confidence score for a cluster.

    Args:
        cluster_embeddings: Embeddings in cluster (4, dim)
        center: Cluster centroid (dim,)
        distance_metric: Distance metric used

    Returns:
        Confidence in [0, 1], where 1 = perfect clustering

    Uses average similarity to cluster center. Higher similarity = tighter cluster = higher confidence.
    """
    # Optimize: avoid reshape by broadcasting
    distances = cdist(cluster_embeddings, center[np.newaxis, :], metric=distance_metric).ravel()
    avg_distance = distances.mean()

    # Convert distance to similarity score in [0, 1]
    # For cosine: distance is already in [0, 2], map to confidence
    if distance_metric == 'cosine':
        # Cosine distance range: [0, 2]
        # 0 = identical vectors (confidence=1.0)
        # 1 = orthogonal vectors (confidence=0.5)
        # 2 = opposite vectors (confidence=0.0)
        confidence = 1 - (avg_distance / 2.0)  # Map [0, 2] to [1, 0]
    else:
        # For Euclidean: use exponential decay
        # exp(-0) = 1.0 (zero distance = perfect confidence)
        # exp(-1) ≈ 0.37 (unit distance = moderate confidence)
        # exp(-∞) = 0.0 (infinite distance = no confidence)
        confidence = np.exp(-avg_distance)

    return float(np.clip(confidence, 0.0, 1.0))
