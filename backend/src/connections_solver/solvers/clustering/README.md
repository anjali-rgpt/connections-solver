# Clustering Module Documentation

## Overview

The clustering module provides adaptive clustering algorithms for semantic word grouping in the Connections puzzle solver. It automatically selects the best clustering algorithm based on data characteristics and generates comprehensive metadata for explainability.

## Components

### 1. Clustering Algorithms (`__init__.py`)

Three clustering algorithms are available:

#### K-Means
- **Best for**: Well-separated, spherical clusters with uniform density
- **Characteristics**: Fast, efficient, assumes clusters have similar sizes
- **When chosen**: Default algorithm when no special conditions are detected

#### Agglomerative Hierarchical Clustering
- **Best for**: Non-spherical, overlapping clusters
- **Characteristics**: Builds hierarchy bottom-up, handles irregular cluster shapes
- **When chosen**: Separation ratio < 1.2 (clusters overlap significantly)

#### DBSCAN (Density-Based Spatial Clustering)
- **Best for**: Varying density clusters, noise detection
- **Characteristics**: Finds arbitrarily shaped clusters, identifies outliers
- **When chosen**: Distance CV > 0.4 (high variance in pairwise distances)

### 2. Algorithm Selection (`analyze.py`)

The `analyze()` function automatically selects the best algorithm based on embedding space analysis.

#### Key Metrics

**Distance Coefficient of Variation (CV)**
- Formula: `std(distances) / mean(distances)`
- Interpretation:
  - < 0.3: Uniform spacing (K-Means suitable)
  - > 0.4: Varying density (DBSCAN recommended)
- Thresholds based on empirical testing with word embeddings

**Separation Ratio**
- Formula: `mean(between_cluster_distance) / mean(within_cluster_distance)`
- Available only when ground truth categories are provided
- Interpretation:
  - > 1.2: Good separation (K-Means works well)
  - < 1.2: Overlapping clusters (Agglomerative recommended)

**PCA Variance (2D)**
- Percentage of variance explained by top 2 principal components
- Indicates how well data projects to 2D for visualization
- Higher values mean better 2D representations

#### Usage

```python
from connections_solver.solvers.clustering.analyze import analyze

# Without ground truth (normal usage)
algorithm, metrics = analyze(embeddings, words, verbose=False)

# With ground truth (for analysis/debugging)
algorithm, metrics = analyze(embeddings, words, true_categories=categories, verbose=True)

# Returns:
# - algorithm: 'kmeans', 'agglomerative', or 'dbscan'
# - metrics: dict with distance_cv, pca_variance_2d, separation_ratio (optional)
```

#### Return Value

```python
{
    "distance_cv": 0.35,              # Coefficient of variation
    "pca_variance_2d": 0.68,          # 68% variance in 2D
    "euclidean_mean": 2.45,           # Average Euclidean distance
    "euclidean_std": 0.87,            # Std dev of Euclidean distances
    "cosine_mean": 0.32,              # Average cosine distance
    "cosine_std": 0.11,               # Std dev of cosine distances
    "separation_ratio": 1.5           # Optional, only if ground truth provided
}
```

### 3. Cluster Utilities (`utils.py`)

#### `enforce_equal_clusters()`

Ensures exactly 4 words per cluster by reassigning words greedily:
- Words in oversized clusters are moved to undersized clusters
- Reassignment minimizes distance to new cluster center
- Maintains cluster cohesion while satisfying constraints

#### `calculate_confidence()`

Computes confidence score (0-1) for a cluster:
- Based on average distance from words to cluster center
- Uses inverse exponential scaling: `exp(-mean_distance)`
- Lower distance → higher confidence
- Normalized to [0, 1] range

### 4. Model Caching (`embeddings/word2vec.py`)

The Word2Vec model is **1.6GB** and slow to load (~10 seconds). The module implements singleton pattern caching to avoid redundant loads.

#### Caching Behavior

```python
from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider

# First instance loads model (slow)
provider1 = Word2VecEmbeddingProvider()  # ~10 seconds

# Second instance reuses cache (instant)
provider2 = Word2VecEmbeddingProvider()  # <0.1 seconds

# Disable caching if needed
provider3 = Word2VecEmbeddingProvider(use_cache=False)  # Loads fresh model
```

#### Clearing Cache

```python
# Clear specific model
Word2VecEmbeddingProvider.clear_cache("word2vec-google-news-300")

# Clear all cached models
Word2VecEmbeddingProvider.clear_cache()
```

**When to clear cache:**
- Testing: Clear between tests to ensure isolation
- Memory constraints: Free 1.6GB when model no longer needed
- Model updates: After upgrading gensim or changing model

#### Implementation Details

- **Thread-safe**: Uses `threading.Lock` to prevent race conditions
- **Module-level cache**: Single cache shared across all instances
- **Automatic caching**: Enabled by default (`use_cache=True`)

## Solver Metadata Structure

The ClusterSolver generates comprehensive metadata for explainability:

```python
{
    "algorithm_selection": {
        "chosen": "kmeans" | "agglomerative" | "dbscan",
        "reason": "Human-readable explanation",
        "metrics": {
            "distance_cv": 0.35,
            "pca_variance_2d": 0.68,
            "separation_ratio": 1.5  # Optional
        }
    },
    "cluster_quality": {
        "avg_confidence": 0.82,
        "confidence_per_cluster": [0.85, 0.79, 0.88, 0.76],
        "distance_metrics": {
            "euclidean_mean": 2.45,
            "euclidean_std": 0.87,
            "cosine_mean": 0.32,
            "cosine_std": 0.11
        }
    },
    "visualization": {
        "method": "tsne",
        "coordinates_2d": [
            {"word": "salmon", "x": 1.2, "y": -0.8, "cluster": 0},
            # ... 15 more
        ],
        "outliers": [3, 7, 12]  # Indices of words far from cluster centers
    }
}
```

## Testing

### Mock Embeddings

Tests use deterministic hash-based embeddings to avoid downloading the 1.6GB model:

```python
import pytest
import numpy as np
from unittest.mock import patch

@pytest.fixture
def mock_word2vec_model():
    class MockModel:
        vector_size = 300
        def __getitem__(self, word):
            seed = hash(word.lower()) % (2**32)
            np.random.seed(seed)
            return np.random.randn(300)
    return MockModel()

@pytest.fixture
def cluster_solver_with_mock(mock_word2vec_model):
    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model
        solver = ClusterSolver()
        yield solver
```

### Running Tests

```bash
# Run cluster solver tests
pytest tests/test_cluster_solver.py -v

# Run with coverage
pytest tests/test_cluster_solver.py --cov=connections_solver.solvers

# Run specific test category
pytest tests/test_cluster_solver.py -k "metadata"
```

### Test Categories

1. **Output Contract Tests**: Verify 4 categories, 4 words each, valid confidence scores
2. **Configuration Tests**: Algorithm override, default selection, invalid config handling
3. **Metadata Tests**: Structure validation, algorithm selection, visualization data
4. **Integration Tests**: Solver registration, end-to-end solving
5. **Caching Tests**: Model reuse, cache clearing, no-cache option
6. **Edge Cases**: Unknown words, identical embeddings

## Configuration

### Solver Configuration

```python
# Auto-select algorithm (recommended)
solver = ClusterSolver()

# Force specific algorithm
solver = ClusterSolver(config={"algorithm": "kmeans"})
solver = ClusterSolver(config={"algorithm": "agglomerative"})
solver = ClusterSolver(config={"algorithm": "dbscan"})
```

### Advanced Configuration

```python
# Disable model caching
from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider
Word2VecEmbeddingProvider.clear_cache()
solver = ClusterSolver()
solver.embedder = Word2VecEmbeddingProvider(use_cache=False)

# Use different distance metric
solver = ClusterSolver()
solver.distance_metric = 'euclidean'  # Default is 'cosine'
```

## Performance Characteristics

### Time Complexity

- **First solve**: ~10s (model loading) + ~2s (clustering) = ~12s
- **Subsequent solves**: ~2s (model cached)
- **Per-word embedding**: O(1) dictionary lookup

### Memory Usage

- **Model**: 1.6GB (shared across instances with caching)
- **Embeddings**: 16 words × 300 dims × 8 bytes = ~38KB
- **Peak usage**: ~1.65GB (first instance), ~50MB (subsequent instances)

### Optimization Tips

1. **Enable caching** (default): Avoid reloading model
2. **Reuse solver instances**: Create once, solve multiple puzzles
3. **Parallel solvers**: Different solver types can run in parallel
4. **Clear cache** when done: Free 1.6GB if no longer needed

## Troubleshooting

### Model Download Issues

If model download fails or is slow:

```python
# Download manually beforehand
import gensim.downloader as api
api.load('word2vec-google-news-300')
```

### Memory Errors

If running out of memory:

```python
# Clear cache after each solve
from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider

solver = ClusterSolver()
result = solver.solve_puzzle(puzzle)
Word2VecEmbeddingProvider.clear_cache()  # Free 1.6GB
```

### Unknown Words

Words not in Word2Vec vocabulary receive zero vectors:
- Common with proper nouns, slang, new words
- May reduce clustering quality
- Check logs for warnings: `"Word 'xyz' not found in vocabulary"`

## References

- **Word2Vec**: Mikolov et al. (2013) - Efficient Estimation of Word Representations
- **t-SNE**: van der Maaten & Hinton (2008) - Visualizing High-Dimensional Data
- **K-Means**: Lloyd (1982) - Least squares quantization in PCM
- **DBSCAN**: Ester et al. (1996) - A density-based algorithm for discovering clusters
- **Agglomerative Clustering**: Ward (1963) - Hierarchical grouping to optimize objective function

## Contributing

When modifying the clustering module:

1. **Update tests**: Add test cases for new functionality
2. **Update metadata schema**: Document new fields in `core/models.py`
3. **Update frontend types**: Add TypeScript interfaces in `frontend/src/types/api.ts`
4. **Run full test suite**: `pytest tests/test_cluster_solver.py -v`
5. **Test with real puzzles**: Verify end-to-end workflow

## License

MIT License - See LICENSE file for details
