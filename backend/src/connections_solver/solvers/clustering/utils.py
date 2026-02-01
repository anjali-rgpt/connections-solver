"""Utilities for enforcing Connections game constraints."""

import numpy as np
from typing import List
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment


def enforce_equal_clusters_optimal(
    embeddings: np.ndarray,
    labels: np.ndarray,
    centers: np.ndarray,
    distance_metric: str = 'cosine'
) -> np.ndarray:
    """Optimally reassign words to create exactly 4 words per cluster.

    Uses the Hungarian algorithm (linear_sum_assignment) to find the optimal
    assignment that minimizes total distance from words to cluster centers
    while ensuring exactly 4 words per cluster.

    Algorithm:
        1. Build cost matrix: cost[word_i][cluster_j] = distance(word_i, center_j)
        2. Each cluster needs exactly 4 words, so duplicate each cluster 4 times
        3. Use Hungarian algorithm to find minimum-cost perfect matching
        4. Map assignments back to cluster labels

    Complexity: O(n³) where n=16 words. Fast enough for real-time use (~1ms).

    Args:
        embeddings: Word embeddings matrix (16, dim)
        labels: Initial cluster assignments (16,) - not used but kept for API compatibility
        centers: Cluster centroids (4, dim)
        distance_metric: 'cosine' or 'euclidean'

    Returns:
        Optimal cluster labels (16,) with exactly 4 words per cluster

    Example:
        >>> embeddings = np.random.rand(16, 300)
        >>> centers = np.random.rand(4, 300)
        >>> labels = np.zeros(16)  # Initial labels (not used)
        >>> optimal_labels = enforce_equal_clusters_optimal(embeddings, labels, centers)
        >>> np.bincount(optimal_labels)
        array([4, 4, 4, 4])  # Exactly 4 words per cluster
    """
    n_clusters = 4
    words_per_cluster = 4

    # Build cost matrix: distance from each word to each cluster center
    # Shape: (16 words, 4 clusters)
    cost_matrix = cdist(embeddings, centers, metric=distance_metric)

    # Duplicate each cluster column 4 times to enforce "exactly 4 words per cluster"
    # Shape: (16 words, 16 slots) where slots 0-3 are cluster 0, 4-7 are cluster 1, etc.
    expanded_costs = np.repeat(cost_matrix, words_per_cluster, axis=1)

    # Hungarian algorithm finds optimal one-to-one assignment minimizing total cost
    # row_indices: which word (0-15)
    # col_indices: which slot (0-15)
    row_indices, col_indices = linear_sum_assignment(expanded_costs)

    # Map slot indices back to cluster labels
    # Slot 0-3 → cluster 0, slot 4-7 → cluster 1, etc.
    optimal_labels = col_indices // words_per_cluster

    # Verify result (should always be true with Hungarian algorithm)
    cluster_sizes = np.bincount(optimal_labels, minlength=n_clusters)
    if not np.all(cluster_sizes == words_per_cluster):
        # Fallback to greedy if somehow failed (shouldn't happen)
        return enforce_equal_clusters(embeddings, labels, centers, distance_metric)

    return optimal_labels


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
    
    Edge cases:
        - Zero vectors (words not in vocabulary): Returns low confidence (0.1)
        - NaN/inf values: Returns low confidence (0.1)
    """
    # Check for zero vectors (words not found in vocabulary)
    # If center is all zeros or has very low magnitude, assign low confidence
    center_magnitude = np.linalg.norm(center)
    if center_magnitude < 1e-6:
        return 0.1  # Low confidence for zero-vector clusters
    
    # Calculate distances
    distances = cdist(cluster_embeddings, center[np.newaxis, :], metric=distance_metric).ravel()
    
    # Check for invalid distances (nan/inf)
    if np.any(~np.isfinite(distances)):
        return 0.1  # Low confidence for invalid embeddings
    
    avg_distance = distances.mean()
    
    # Check if mean is valid
    if not np.isfinite(avg_distance):
        return 0.1

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

    # Final safety check and clipping
    result = float(np.clip(confidence, 0.0, 1.0))
    return result if np.isfinite(result) else 0.1


def refine_clusters_iterative(
    embeddings: np.ndarray,
    labels: np.ndarray,
    distance_metric: str = 'cosine',
    max_iterations: int = 3
) -> np.ndarray:
    """Iteratively refine cluster assignments by swapping words between clusters.

    After initial clustering, this post-processing step tries swapping pairs of words
    from different clusters to see if it improves overall cluster cohesion (reduces
    total within-cluster distance).

    Algorithm:
        1. Compute initial total within-cluster distance
        2. For each iteration:
           a. Try swapping each pair of words from different clusters
           b. If swap reduces total distance, keep it
           c. If no swaps improve, stop early
        3. Return refined labels

    Why this works:
        - Initial clustering algorithms may make suboptimal assignments at boundaries
        - Local search can find better configurations
        - Greedy swapping is simple and fast

    Complexity: O(iterations * n² * d) where n=16 words, d=embedding dim
        With max_iterations=3: ~3 * 120 comparisons * distance calculations
        Fast enough for real-time use (~10-20ms)

    Args:
        embeddings: Word embeddings matrix (16, dim)
        labels: Initial cluster assignments (16,)
        distance_metric: 'cosine' or 'euclidean'
        max_iterations: Maximum refinement iterations (default: 3)
            - 3 iterations provides good balance of accuracy vs speed
            - Diminishing returns after 3 iterations in practice

    Returns:
        Refined cluster labels (16,) with same cluster sizes as input

    Example:
        >>> labels = np.array([0,0,0,0, 1,1,1,1, 2,2,2,2, 3,3,3,3])
        >>> refined = refine_clusters_iterative(embeddings, labels)
        >>> # Words may have been swapped to improve cohesion
    """
    labels = labels.copy()  # Don't modify original
    n_words = len(labels)

    # Compute initial total within-cluster distance (lower is better)
    best_cost = _compute_total_within_cluster_distance(embeddings, labels, distance_metric)

    for iteration in range(max_iterations):
        improved = False

        # Try swapping each pair of words from different clusters
        for i in range(n_words):
            for j in range(i + 1, n_words):
                # Only consider words in different clusters
                if labels[i] == labels[j]:
                    continue

                # Swap
                labels[i], labels[j] = labels[j], labels[i]

                # Compute new cost
                new_cost = _compute_total_within_cluster_distance(embeddings, labels, distance_metric)

                if new_cost < best_cost:
                    # Keep swap - it improved cohesion
                    best_cost = new_cost
                    improved = True
                else:
                    # Revert swap - it made things worse
                    labels[i], labels[j] = labels[j], labels[i]

        # Early stopping: if no swaps improved, we've reached local optimum
        if not improved:
            break

    return labels


def _compute_total_within_cluster_distance(
    embeddings: np.ndarray,
    labels: np.ndarray,
    distance_metric: str = 'cosine'
) -> float:
    """Compute total within-cluster distance (sum of distances to cluster centers).

    Helper function for iterative refinement. Lower values indicate tighter,
    more cohesive clusters.

    Args:
        embeddings: Word embeddings matrix (16, dim)
        labels: Cluster assignments (16,)
        distance_metric: 'cosine' or 'euclidean'

    Returns:
        Total distance as a float
    """
    total_distance = 0.0
    n_clusters = len(np.unique(labels))

    for cluster_id in range(n_clusters):
        # Get words in this cluster
        mask = labels == cluster_id
        if not np.any(mask):
            continue  # Empty cluster

        cluster_embeddings = embeddings[mask]

        # Compute cluster center
        center = cluster_embeddings.mean(axis=0)

        # Sum distances from words to center
        distances = cdist(cluster_embeddings, center[np.newaxis, :], metric=distance_metric).ravel()
        total_distance += distances.sum()

    return total_distance
