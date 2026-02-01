"""Clustering-based solver for Connections puzzles."""

import time
import numpy as np
from typing import List, Optional, Dict, Any
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist

from .base import BaseSolver
from .registry import register_solver
from ..core.models import PredictedCategory, Puzzle, SolverResult
from .embeddings import Word2VecEmbeddingProvider
from .clustering import cluster as apply_clustering
from .clustering.analyze import analyze
from .clustering.utils import enforce_equal_clusters, calculate_confidence


@register_solver("cluster")
class ClusterSolver(BaseSolver):
    """Clusters words by semantic similarity using Word2Vec embeddings.

    This solver uses a multi-step approach to group 16 words into 4 categories:

    Algorithm Flow:
        1. **Embedding**: Convert 16 words to 300-dimensional Word2Vec vectors
        2. **Analysis**: Analyze embedding space characteristics (distance distribution,
           separation, dimensionality) to recommend optimal clustering algorithm
        3. **Clustering**: Apply K-Means, Agglomerative, or DBSCAN based on analysis
        4. **Enforcement**: Ensure exactly 4 words per cluster via greedy reassignment
        5. **Scoring**: Calculate confidence scores based on cluster cohesion
        6. **Metadata**: Generate explainability data (algorithm choice, quality metrics,
           2D visualization)

    Model Caching:
        The Word2Vec model (1.6GB) is cached globally using a singleton pattern.
        First ClusterSolver instance loads the model (~10s), subsequent instances
        reuse the cached model (instant). Use Word2VecEmbeddingProvider.clear_cache()
        to free memory when done.

    Configuration:
        - `algorithm` (optional): Override auto-selection with "kmeans", "agglomerative",
          or "dbscan"

    Metadata Generated:
        - Algorithm selection reasoning and metrics
        - Cluster quality scores (confidence per cluster)
        - 2D visualization coordinates (t-SNE projection)
        - Outlier detection (words far from cluster centers)

    Examples:
        >>> # Auto-select algorithm (recommended)
        >>> solver = ClusterSolver()
        >>> result = solver.solve_puzzle(puzzle)
        >>> print(result.solver_metadata["algorithm_selection"]["chosen"])
        'kmeans'
        >>>
        >>> # Force specific algorithm
        >>> solver = ClusterSolver(config={"algorithm": "agglomerative"})
        >>> result = solver.solve_puzzle(puzzle)
        >>>
        >>> # Clear model cache to free memory
        >>> from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider
        >>> Word2VecEmbeddingProvider.clear_cache()
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ClusterSolver.

        Args:
            config: Configuration dict with optional 'algorithm' key
                   to override auto-detection ('kmeans', 'agglomerative', 'dbscan')
        """
        super().__init__(config)
        self.embedder = None  # Lazy-loaded on first solve() call
        self.n_clusters = 4  # Always 4 categories in Connections
        self.distance_metric = 'cosine'  # Cosine works better than Euclidean for word embeddings
        self.algorithm_override = self.config.get('algorithm')
    
    def _get_embedder(self) -> Word2VecEmbeddingProvider:
        """Get or create the embedder (lazy loading).
        
        The Word2Vec model (1.6GB) is only loaded when first needed,
        not during __init__. This prevents timeouts when listing solvers.
        """
        if self.embedder is None:
            self.embedder = Word2VecEmbeddingProvider()
        return self.embedder

    def solve(self, words: List[str]) -> List[PredictedCategory]:
        """Solve puzzle by clustering words.

        Args:
            words: List of 16 words to cluster

        Returns:
            List of 4 PredictedCategory objects with 4 words each
        """
        # 1. Generate embeddings (lazy-load embedder on first use)
        embedder = self._get_embedder()
        raw_embeddings = embedder.embed(words)
        
        # 2. Dimensionality reduction with PCA
        # For 16 words, we don't need 300 dimensions - reduce to improve performance
        # Keep enough dims to preserve ~95% variance, cap at 50 dimensions
        original_dims = raw_embeddings.shape[1]
        
        if original_dims > 16:  # Only reduce if dims > n_samples
            pca = PCA(n_components=min(50, len(words) - 1))  # Keep up to 50 dims or n-1
            embeddings = pca.fit_transform(raw_embeddings)
            reduced_dims = embeddings.shape[1]
            variance_kept = pca.explained_variance_ratio_.sum()
        else:
            embeddings = raw_embeddings
            reduced_dims = original_dims
            variance_kept = 1.0

        # 3. Determine which algorithm to use
        if self.algorithm_override:
            algorithm = self.algorithm_override
            # Still run analyze to get metrics, but ignore recommendation
            _, analysis_metrics = analyze(embeddings, words, true_categories=None, verbose=False)
            reason = f"Algorithm manually specified in config"
        else:
            # Run analysis to get recommendation and metrics
            algorithm, analysis_metrics = analyze(embeddings, words, true_categories=None, verbose=False)
            # Determine reason based on algorithm
            if algorithm == 'agglomerative':
                reason = "Overlapping clusters benefit from hierarchical clustering"
            elif algorithm == 'dbscan':
                reason = "Varying density detected"
            else:
                reason = "Default choice for word embeddings"

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
        confidence_scores = []
        for cluster_id in range(self.n_clusters):
            # Get words in this cluster
            mask = adjusted_labels == cluster_id
            cluster_words = [w for i, w in enumerate(words) if mask[i]]
            cluster_embeds = embeddings[mask]

            # Calculate confidence
            confidence = calculate_confidence(
                cluster_embeds, centers[cluster_id], self.distance_metric
            )
            confidence_scores.append(confidence)

            categories.append(PredictedCategory(
                words=cluster_words,
                confidence=confidence
            ))

        # Sort by confidence (highest first) for better user experience
        categories.sort(key=lambda c: c.confidence, reverse=True)

        # 6. Generate metadata for explainability
        self._last_solve_metadata = self._generate_metadata(
            algorithm=algorithm,
            reason=reason,
            analysis_metrics=analysis_metrics,
            embeddings=raw_embeddings,  # Use raw embeddings for visualization
            reduced_embeddings=embeddings,  # Use reduced for cluster quality
            words=words,
            labels=adjusted_labels,
            centers=centers,
            confidence_scores=confidence_scores,
            pca_info={
                'original_dims': original_dims,
                'reduced_dims': reduced_dims,
                'variance_kept': variance_kept
            }
        )

        return categories

    def solve_puzzle(self, puzzle: Puzzle) -> SolverResult:
        """Solve a puzzle and return result with metadata.

        Overrides base class to attach solver_metadata for explainability.

        Args:
            puzzle: Puzzle object to solve

        Returns:
            SolverResult with predicted categories, timing, and metadata
        """
        start_time = time.time()
        predicted_categories = self.solve(puzzle.words)
        execution_time_ms = (time.time() - start_time) * 1000

        result = SolverResult(
            puzzle_id=puzzle.puzzle_id,
            solver_type=self.get_name(),
            predicted_categories=predicted_categories,
            execution_time_ms=execution_time_ms,
            solver_config=self.config,
        )

        # Attach metadata if available from solve()
        if hasattr(self, '_last_solve_metadata'):
            result.solver_metadata = self._last_solve_metadata
            delattr(self, '_last_solve_metadata')

        return result

    def _sanitize_for_json(self, obj: Any) -> Any:
        """Recursively sanitize data structure to be JSON-compliant.
        
        Converts nan, inf, -inf to None or safe defaults.
        
        Args:
            obj: Any Python object (dict, list, float, etc.)
            
        Returns:
            JSON-compliant version of the object
        """
        if isinstance(obj, dict):
            return {key: self._sanitize_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._sanitize_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            if np.isnan(obj) or np.isinf(obj):
                return None  # or could use 0.0 or a string like "NaN"
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return self._sanitize_for_json(obj.tolist())
        else:
            return obj

    def _generate_metadata(
        self,
        algorithm: str,
        reason: str,
        analysis_metrics: Dict[str, Any],
        embeddings: np.ndarray,
        reduced_embeddings: np.ndarray,
        words: List[str],
        labels: np.ndarray,
        centers: np.ndarray,
        confidence_scores: List[float],
        pca_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive metadata for explainability.

        Args:
            algorithm: Chosen clustering algorithm
            reason: Human-readable explanation for algorithm choice
            analysis_metrics: Metrics from analyze() function
            embeddings: Raw word embeddings array (for visualization)
            reduced_embeddings: PCA-reduced embeddings (for cluster quality)
            words: List of words
            labels: Cluster assignments
            centers: Cluster centers
            confidence_scores: Confidence per cluster
            pca_info: PCA dimensionality reduction info

        Returns:
            Metadata dictionary with algorithm_selection, cluster_quality, and visualization
        """
        # Extract distance metrics from analysis
        distance_metrics = {
            "euclidean_mean": analysis_metrics["euclidean_mean"],
            "euclidean_std": analysis_metrics["euclidean_std"],
            "cosine_mean": analysis_metrics["cosine_mean"],
            "cosine_std": analysis_metrics["cosine_std"],
        }

        # Generate 2D visualization coordinates (use raw embeddings for better vis)
        visualization_data = self._generate_visualization(embeddings, words, labels)

        # Detect outliers (use reduced embeddings that were used for clustering)
        outliers = self._detect_outliers(reduced_embeddings, labels, centers)

        # Build metadata structure
        metadata = {
            "algorithm_selection": {
                "chosen": algorithm,
                "reason": reason,
                "metrics": {
                    "distance_cv": analysis_metrics["distance_cv"],
                    "pca_variance_2d": analysis_metrics["pca_variance_2d"],
                }
            },
            "cluster_quality": {
                "avg_confidence": float(np.mean(confidence_scores)),
                "confidence_per_cluster": [float(c) for c in confidence_scores],
                "distance_metrics": distance_metrics
            },
            "dimensionality_reduction": {
                "original_dims": pca_info['original_dims'],
                "reduced_dims": pca_info['reduced_dims'],
                "variance_kept": float(pca_info['variance_kept'])
            },
            "visualization": {
                "method": "tsne",
                "coordinates_2d": visualization_data,
                "outliers": outliers
            }
        }

        # Add separation_ratio if available
        if "separation_ratio" in analysis_metrics:
            metadata["algorithm_selection"]["metrics"]["separation_ratio"] = analysis_metrics["separation_ratio"]

        # Sanitize all values to ensure JSON compliance
        return self._sanitize_for_json(metadata)

    def _generate_visualization(
        self,
        embeddings: np.ndarray,
        words: List[str],
        labels: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Generate 2D visualization coordinates using t-SNE.

        Args:
            embeddings: Word embeddings array
            words: List of words
            labels: Cluster assignments

        Returns:
            List of dictionaries with word, x, y, cluster
        """
        # Use t-SNE to reduce to 2D
        tsne = TSNE(n_components=2, random_state=42, perplexity=5)
        coords_2d = tsne.fit_transform(embeddings)

        # Build coordinate list
        visualization = []
        for i, word in enumerate(words):
            visualization.append({
                "word": word,
                "x": float(coords_2d[i, 0]),
                "y": float(coords_2d[i, 1]),
                "cluster": int(labels[i])
            })

        return visualization

    def _detect_outliers(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray,
        centers: np.ndarray,
        threshold_percentile: float = 75
    ) -> List[int]:
        """Detect outlier words that are far from their cluster centers.

        Args:
            embeddings: Word embeddings array
            labels: Cluster assignments
            centers: Cluster centers
            threshold_percentile: Percentile threshold for outlier detection

        Returns:
            List of word indices that are outliers
        """
        outliers = []
        distances = []

        # Calculate distance of each word to its cluster center
        for i in range(len(embeddings)):
            cluster_id = labels[i]
            distance = cdist(
                [embeddings[i]],
                [centers[cluster_id]],
                metric=self.distance_metric
            )[0][0]
            distances.append(distance)

        # Find outliers using percentile threshold
        threshold = np.percentile(distances, threshold_percentile)
        for i, dist in enumerate(distances):
            if dist > threshold:
                outliers.append(i)

        return outliers

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