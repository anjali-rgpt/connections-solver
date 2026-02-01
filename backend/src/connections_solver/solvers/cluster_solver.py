"""Clustering-based solver for Connections puzzles."""

from typing import List, Optional, Dict, Any

from .base import BaseSolver
from .registry import register_solver
from ..core.models import PredictedCategory
from .embeddings import Word2VecEmbeddingProvider
from .clustering import cluster as apply_clustering
from .clustering.analyze import analyze
from .clustering.utils import enforce_equal_clusters, calculate_confidence


@register_solver("cluster")
class ClusterSolver(BaseSolver):
    """Clusters words by semantic similarity using Word2Vec embeddings.

    Algorithm:
        1. Convert 16 words to 300-dim Word2Vec embeddings
        2. Analyze embedding space to recommend clustering algorithm
        3. Apply recommended algorithm (K-Means, Agglomerative, or DBSCAN)
        4. Enforce exactly 4 words per cluster via greedy reassignment
        5. Calculate confidence scores based on cluster cohesion
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ClusterSolver.

        Args:
            config: Configuration dict with optional 'algorithm' key
                   to override auto-detection ('kmeans', 'agglomerative', 'dbscan')
        """
        super().__init__(config)
        self.embedder = Word2VecEmbeddingProvider()
        self.n_clusters = 4  # Always 4 categories in Connections
        self.distance_metric = 'cosine'  # Cosine works better than Euclidean for word embeddings
        self.algorithm_override = self.config.get('algorithm')

    def solve(self, words: List[str]) -> List[PredictedCategory]:
        """Solve puzzle by clustering words.

        Args:
            words: List of 16 words to cluster

        Returns:
            List of 4 PredictedCategory objects with 4 words each
        """
        # 1. Generate embeddings
        embeddings = self.embedder.embed(words)

        # 2. Determine which algorithm to use
        if self.algorithm_override:
            algorithm = self.algorithm_override
        else:
            # Run analysis to get recommendation
            # Pass None for true_categories since we don't have ground truth
            algorithm = analyze(embeddings, words, true_categories=None)

        # 3. Apply clustering
        labels, centers = apply_clustering(
            embeddings,
            algorithm=algorithm,
            n_clusters=self.n_clusters
        )

        # 4. Enforce 4-word constraint
        adjusted_labels = enforce_equal_clusters(
            words, embeddings, labels, centers, self.distance_metric
        )

        # 5. Build categories with confidence scores
        categories = []
        for cluster_id in range(self.n_clusters):
            # Get words in this cluster
            mask = adjusted_labels == cluster_id
            cluster_words = [w for i, w in enumerate(words) if mask[i]]
            cluster_embeds = embeddings[mask]

            # Calculate confidence
            confidence = calculate_confidence(
                cluster_embeds, centers[cluster_id], self.distance_metric
            )

            categories.append(PredictedCategory(
                words=cluster_words,
                confidence=confidence
            ))

        # Sort by confidence (highest first) for better user experience
        categories.sort(key=lambda c: c.confidence, reverse=True)

        return categories

    def get_name(self) -> str:
        return "Cluster Solver"

    def get_description(self) -> str:
        return "Groups words by semantic similarity using Word2Vec embeddings and clustering."

    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema for this solver.

        Returns:
            Dictionary describing config parameters
        """
        return {
            "algorithm": {
                "type": "string",
                "description": "Clustering algorithm to use (kmeans, agglomerative, dbscan). If not specified, automatically chooses based on data analysis.",
                "optional": True,
                "enum": ["kmeans", "agglomerative", "dbscan"]
            }
        }