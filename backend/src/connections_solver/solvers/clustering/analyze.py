"""Analyze Word2Vec embedding space for Connections puzzles."""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from typing import List, Tuple, Optional, Dict, Any


def analyze(
    embeddings: np.ndarray,
    words: List[str],
    true_categories: Optional[List[List[str]]] = None,
    verbose: bool = False
) -> Tuple[str, Dict[str, Any]]:
    """Analyze embedding space and recommend clustering algorithm.

    This function performs comprehensive analysis of word embeddings to determine
    which clustering algorithm is best suited for the data. It examines distance
    distributions, cluster separation, and dimensionality characteristics.

    Decision Logic:
        1. **DBSCAN**: Chosen if distance CV > 0.4 (high variance in distances)
           - Indicates varying density clusters
           - Some word pairs very close, others very far
        2. **Agglomerative**: Chosen if separation_ratio < 1.2 (when ground truth available)
           - Between-cluster distance < 1.2x within-cluster distance
           - Indicates overlapping or poorly separated clusters
        3. **K-Means**: Default choice for spherical, well-separated clusters

    Thresholds:
        - Distance CV threshold (0.4): Based on empirical testing with Word2Vec embeddings
        - Separation ratio threshold (1.2): Balances precision vs recall for cluster separation
        - PCA variance: Informational only, not used for algorithm selection

    Args:
        embeddings: Word embeddings matrix of shape (16, embedding_dim)
        words: List of 16 words corresponding to embeddings
        true_categories: Optional ground truth categories for separation analysis.
                        Each category is a list of words. Only used for analysis,
                        not required for algorithm selection.
        verbose: If True, prints detailed analysis to console. Default: False.

    Returns:
        Tuple containing:
            - algorithm (str): Recommended algorithm name - 'kmeans', 'agglomerative', or 'dbscan'
            - metrics (Dict[str, Any]): Analysis metrics including:
                - distance_cv (float): Coefficient of variation in cosine distances
                - pca_variance_2d (float): Variance explained by top 2 PCs (0-1)
                - euclidean_mean (float): Mean Euclidean distance between word pairs
                - euclidean_std (float): Std dev of Euclidean distances
                - cosine_mean (float): Mean cosine distance between word pairs
                - cosine_std (float): Std dev of cosine distances
                - separation_ratio (float, optional): Ratio of between/within cluster distances
                  (only present if true_categories provided)

    Examples:
        >>> from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider
        >>> embedder = Word2VecEmbeddingProvider()
        >>> words = ["salmon", "trout", "bass", "tuna", ...]
        >>> embeddings = embedder.embed(words)
        >>>
        >>> # Without ground truth (normal usage)
        >>> algorithm, metrics = analyze(embeddings, words)
        >>> print(f"Recommended: {algorithm}, CV: {metrics['distance_cv']:.3f}")
        Recommended: kmeans, CV: 0.325
        >>>
        >>> # With ground truth (for debugging/analysis)
        >>> categories = [["salmon", "trout", "bass", "tuna"], ...]
        >>> algorithm, metrics = analyze(embeddings, words, categories, verbose=True)
        === Distance Metrics ===
        Euclidean - mean: 2.450, std: 0.870
        Cosine    - mean: 0.320, std: 0.110
        ...
    """
    if verbose:
        print("\n" + "=" * 60)
        print("EMBEDDING SPACE ANALYSIS")
        print("=" * 60)

    # 1. Distance analysis
    if verbose:
        print("\n=== Distance Metrics ===")
    euclidean_dists = pdist(embeddings, metric='euclidean')
    cosine_dists = pdist(embeddings, metric='cosine')

    if verbose:
        print(f"Euclidean - mean: {euclidean_dists.mean():.3f}, std: {euclidean_dists.std():.3f}")
        print(f"Cosine    - mean: {cosine_dists.mean():.3f}, std: {cosine_dists.std():.3f}")

    # 2. Category separation (if ground truth provided)
    separation_ratio = None
    if true_categories:
        within_dists, between_dists = calculate_separation(
            embeddings, words, true_categories
        )
        separation_ratio = np.mean(between_dists) / np.mean(within_dists)

        if verbose:
            print(f"\n=== Category Separation ===")
            print(f"Within-category distance:  {np.mean(within_dists):.3f} ± {np.std(within_dists):.3f}")
            print(f"Between-category distance: {np.mean(between_dists):.3f} ± {np.std(between_dists):.3f}")
            print(f"Separation ratio: {separation_ratio:.2f}")
            print(f"Interpretation: {'Good separation' if separation_ratio > 1.2 else 'Overlapping clusters'}")

    # 3. Dimensionality analysis
    if verbose:
        print(f"\n=== Dimensionality ===")
        print(f"Original dims: {embeddings.shape[1]}")

    pca = PCA()
    pca.fit(embeddings)
    cumsum = pca.explained_variance_ratio_.cumsum()
    pca_variance_2d = float(cumsum[1])

    if verbose:
        print(f"Variance in top 2 PCs:  {cumsum[1]:.1%}")
        print(f"Variance in top 5 PCs:  {cumsum[4]:.1%}")
        print(f"Variance in top 10 PCs: {cumsum[9]:.1%}")

    # 4. Cluster characteristic analysis
    if verbose:
        print(f"\n=== Cluster Characteristics ===")

    # Measure density variation using std of pairwise distances
    dist_std = cosine_dists.std()
    dist_cv = dist_std / cosine_dists.mean()  # Coefficient of variation

    if verbose:
        print(f"Distance coefficient of variation: {dist_cv:.3f}")
        # CV > 0.3: Moderate threshold for density variation
        # Below 0.3 = uniform spacing; above = some clusters tighter than others
        print(f"Interpretation: {'Varying density' if dist_cv > 0.3 else 'Uniform density'}")

    # Measure cluster compactness
    if true_categories and verbose:
        avg_within = np.mean(within_dists)
        print(f"Average within-cluster distance: {avg_within:.3f}")
        # 0.3 threshold: For cosine distance in [0, 2], 0.3 = ~15% dissimilarity
        # Words in same category should be very similar (low distance)
        print(f"Interpretation: {'Tight clusters' if avg_within < 0.3 else 'Loose clusters'}")

    # 5. Algorithm recommendation
    if verbose:
        print(f"\n=== Recommendation ===")

    # Decision logic:
    # - K-Means: Good for spherical, well-separated, uniform density
    # - Agglomerative: Good for hierarchical structure, non-spherical
    # - DBSCAN: Good for varying density, noise

    # Start with K-Means as default (simple and effective)
    algorithm = 'kmeans'
    reason = "Default choice for word embeddings"

    # Override if we have evidence for other algorithms
    if true_categories and separation_ratio is not None and separation_ratio < 1.2:
        # separation_ratio < 1.2: Between-cluster distance < 1.2x within-cluster distance
        # This indicates overlapping/poorly separated clusters
        # Agglomerative works better for non-spherical, overlapping clusters
        algorithm = 'agglomerative'
        reason = "Overlapping clusters benefit from hierarchical clustering"
    elif dist_cv > 0.4:
        # dist_cv > 0.4: Coefficient of variation (std/mean) > 0.4
        # High CV indicates some word pairs are very close, others very far
        # This suggests varying density clusters, which DBSCAN handles well
        algorithm = 'dbscan'
        reason = "Varying density detected"

    if verbose:
        print(f"Recommended algorithm: {algorithm.upper()}")
        print(f"Reason: {reason}")
        print("=" * 60 + "\n")

    # Build metrics dictionary
    metrics = {
        "distance_cv": float(dist_cv),
        "pca_variance_2d": pca_variance_2d,
        "euclidean_mean": float(euclidean_dists.mean()),
        "euclidean_std": float(euclidean_dists.std()),
        "cosine_mean": float(cosine_dists.mean()),
        "cosine_std": float(cosine_dists.std()),
    }

    if separation_ratio is not None:
        metrics["separation_ratio"] = float(separation_ratio)

    return algorithm, metrics


def calculate_separation(
    embeddings: np.ndarray,
    words: List[str],
    categories: List[List[str]]
) -> Tuple[List[float], List[float]]:
    """Calculate within and between category distances.

    Args:
        embeddings: Word embeddings (16, dim)
        words: List of words
        categories: List of category word lists

    Returns:
        within_dists: List of within-category pairwise distances
        between_dists: List of between-category pairwise distances
    """
    within = []
    between = []

    # Create word to index mapping
    word_to_idx = {w: i for i, w in enumerate(words)}

    # Calculate all pairwise distances once for efficiency
    all_distances = squareform(pdist(embeddings, metric='cosine'))

    for cat_words in categories:
        # Get indices of words in this category
        cat_indices = [word_to_idx[w] for w in cat_words if w in word_to_idx]

        if len(cat_indices) < 2:
            continue

        # Within-category distances using pre-computed distance matrix
        for i, idx1 in enumerate(cat_indices):
            for idx2 in cat_indices[i+1:]:
                within.append(all_distances[idx1, idx2])

        # Between-category distances
        other_indices = [i for i in range(len(words)) if i not in cat_indices]
        for idx in cat_indices:
            for other_idx in other_indices:
                between.append(all_distances[idx, other_idx])

    return within, between


def visualize(
    embeddings: np.ndarray,
    words: List[str],
    categories: Optional[List[List[str]]] = None,
    output_path: str = "embeddings_viz.png"
) -> None:
    """Create t-SNE visualization of embeddings.

    Args:
        embeddings: Word embeddings (16, dim)
        words: List of words
        categories: Optional ground truth categories for coloring
        output_path: Path to save visualization

    Note: Requires matplotlib to be installed (dev dependency)
    """
    try:
        import matplotlib.pyplot as plt
        from sklearn.manifold import TSNE
    except ImportError:
        print("Skipping visualization: matplotlib not installed")
        print("Install with: pip install matplotlib")
        return

    # Reduce to 2D using t-SNE
    # perplexity=5: Balance between local and global structure
    # Rule of thumb: perplexity between 5 and 50, typically 5-15 for small datasets
    # With 16 words, perplexity=5 is appropriate (typical range is N/3 to N/2)
    # random_state=42: Fixed seed for reproducible visualizations
    tsne = TSNE(n_components=2, random_state=42, perplexity=5)
    coords_2d = tsne.fit_transform(embeddings)

    plt.figure(figsize=(12, 8))

    if categories:
        # Color by category
        colors = ['red', 'blue', 'green', 'orange']
        word_to_idx = {w: i for i, w in enumerate(words)}

        for i, cat_words in enumerate(categories):
            cat_indices = [word_to_idx[w] for w in cat_words if w in word_to_idx]

            if len(cat_indices) > 0:
                plt.scatter(
                    coords_2d[cat_indices, 0],
                    coords_2d[cat_indices, 1],
                    c=colors[i % len(colors)],
                    label=f"Category {i+1}",
                    s=200,
                    alpha=0.6
                )

                # Annotate words
                for idx in cat_indices:
                    plt.annotate(
                        words[idx],
                        (coords_2d[idx, 0], coords_2d[idx, 1]),
                        fontsize=10,
                        ha='center'
                    )
    else:
        # No categories - plot all words
        plt.scatter(coords_2d[:, 0], coords_2d[:, 1], s=200, alpha=0.6)
        for i, word in enumerate(words):
            plt.annotate(
                word,
                (coords_2d[i, 0], coords_2d[i, 1]),
                fontsize=10,
                ha='center'
            )

    plt.title("Word Embeddings - t-SNE Projection")
    if categories:
        plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Visualization saved to: {output_path}")


if __name__ == "__main__":
    """Run analysis on example puzzle."""
    from ...storage.memory import MemoryStorage
    from ..embeddings.word2vec import Word2VecEmbeddingProvider

    # Load puzzle from storage
    storage = MemoryStorage()
    puzzle = storage.get_puzzle("example")
    
    if puzzle:
        embedder = Word2VecEmbeddingProvider()
        embeddings = embedder.embed(puzzle.words)

        # Extract ground truth categories
        categories = [cat.words for cat in puzzle.categories]

        # Run analysis
        recommended_algorithm, metrics = analyze(embeddings, puzzle.words, categories, verbose=True)

        # Generate visualization
        visualize(embeddings, puzzle.words, categories)
    else:
        print("Error: Example puzzle not found in storage")
