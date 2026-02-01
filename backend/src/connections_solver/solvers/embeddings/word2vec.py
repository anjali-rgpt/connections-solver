"""Word2Vec embedding provider"""

import numpy as np
import logging
import threading
from typing import List, Dict, Any, Optional

from .base import EmbeddingProvider

logger = logging.getLogger(__name__)

# Module-level cache for Word2Vec models to avoid loading 1.6GB model per instance
_GLOBAL_MODEL_CACHE: Dict[str, Any] = {}
_CACHE_LOCK = threading.Lock()


class Word2VecEmbeddingProvider(EmbeddingProvider):
    """Word2Vec embedding provider using pre-trained model

    This provider uses the pre-trained Word2Vec model from gensim.
    Word2Vec was trained on a corpus of text to determine co-occurrence patterns of words.
    Words with similar meanings will occur in similar contexts, and therefore will have similar embeddings.

    The provider uses a module-level cache to avoid loading the 1.6GB model multiple times.
    First instance loads the model (~10s), subsequent instances reuse the cached model (instant).

    Args:
        model_name: Name of the pre-trained model from gensim (default: "word2vec-google-news-300")
        use_cache: Whether to use the global model cache (default: True)

    Examples:
        >>> # First instance loads model (slow)
        >>> provider1 = Word2VecEmbeddingProvider()
        >>> # Second instance reuses cached model (fast)
        >>> provider2 = Word2VecEmbeddingProvider()
        >>>
        >>> # Clear cache to free memory
        >>> Word2VecEmbeddingProvider.clear_cache()
    """

    def __init__(self, model_name: str = "word2vec-google-news-300", use_cache: bool = True):
        self.model_name = model_name
        self.use_cache = use_cache
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load pre-trained Word2Vec model from gensim

        Uses global cache if use_cache=True to avoid reloading the 1.6GB model.
        Thread-safe using double-checked locking pattern to avoid holding lock
        during the expensive load operation.
        """
        try:
            import gensim.downloader as api

            # Double-checked locking pattern for cache
            if self.use_cache:
                # First check: acquire lock and check cache
                with _CACHE_LOCK:
                    if self.model_name in _GLOBAL_MODEL_CACHE:
                        logger.info(f"Reusing cached Word2Vec model: {self.model_name}")
                        self.model = _GLOBAL_MODEL_CACHE[self.model_name]
                        return

                # Cache miss - load model WITHOUT holding lock (expensive operation)
                logger.info(f"Loading pre-trained Word2Vec model from gensim: {self.model_name}")
                model = api.load(self.model_name)
                logger.info(f"Pre-trained Word2Vec model loaded successfully: {self.model_name}")

                # Second check: acquire lock again and verify cache before storing
                with _CACHE_LOCK:
                    if self.model_name in _GLOBAL_MODEL_CACHE:
                        # Another thread loaded it while we were loading
                        # Discard our copy and use the cached one
                        logger.info(f"Another thread cached the model, using cached version: {self.model_name}")
                        self.model = _GLOBAL_MODEL_CACHE[self.model_name]
                    else:
                        # We're first - store our loaded model in cache
                        _GLOBAL_MODEL_CACHE[self.model_name] = model
                        self.model = model
                        logger.info(f"Cached Word2Vec model: {self.model_name}")
            else:
                # Caching disabled - just load the model
                logger.info(f"Loading pre-trained Word2Vec model from gensim: {self.model_name}")
                model = api.load(self.model_name)
                logger.info(f"Pre-trained Word2Vec model loaded successfully: {self.model_name}")
                self.model = model

        except ImportError:
            logger.error("Gensim is not installed. Please install it using `pip install gensim`")
            raise ImportError("Gensim is not installed. Please install it using `pip install gensim`")

        except Exception as e:
            logger.error(f"Error loading pre-trained Word2Vec model: {e}")
            raise e

    def embed(self, words: List[str]) -> np.ndarray:
        """Convert a list of words into a matrix of embeddings

        Multi-word phrases are handled by replacing spaces with underscores,
        which is the format used by the Google News Word2Vec model.

        Args:
            words: List[str] - List of words or phrases to embed

        Returns:
            np.ndarray - Matrix of embeddings of shape(len(words), embedding_dim)

        Examples:
            >>> provider.embed(["NEW YORK", "hot dog", "bass"])
            # Looks up: "new_york", "hot_dog", "bass"
        """
        
        # Normalize: strip whitespace, lowercase, replace spaces with underscores
        normalized_words = [word.strip().lower().replace(' ', '_') for word in words]

        embeddings = []
        embedding_dim = self.get_embedding_dims()

        for original_word, normalized_word in zip(words, normalized_words):
            try:
                embedding = self.model[normalized_word]
            except KeyError:
                # If normalized form not found, try original lowercase without underscore
                try:
                    embedding = self.model[normalized_word.replace('_', '')]
                except KeyError:
                    # If still not found, use zero vector as placeholder
                    logger.warning(
                        f"Word '{original_word}' (normalized: '{normalized_word}') "
                        f"not found in vocabulary. Using zero vector as placeholder."
                    )
                    embedding = np.zeros(embedding_dim)
            embeddings.append(embedding)

        return np.array(embeddings)

    def get_name(self) -> str:
        """Return the name of the embedding provider"""
        return "Word2Vec"

    def get_embedding_dims(self) -> int:
        """Return the number of dimensions of the embeddings"""
        if self.model is None:
            raise ValueError("Model not loaded. Cannot determine embedding dimensions.")
        return self.model.vector_size

    @staticmethod
    def clear_cache(model_name: Optional[str] = None):
        """Clear the global model cache to free memory

        Args:
            model_name: Specific model to remove from cache. If None, clears entire cache.

        Examples:
            >>> # Clear specific model
            >>> Word2VecEmbeddingProvider.clear_cache("word2vec-google-news-300")
            >>>
            >>> # Clear all cached models
            >>> Word2VecEmbeddingProvider.clear_cache()
        """
        with _CACHE_LOCK:
            if model_name:
                if model_name in _GLOBAL_MODEL_CACHE:
                    del _GLOBAL_MODEL_CACHE[model_name]
                    logger.info(f"Cleared cached model: {model_name}")
            else:
                _GLOBAL_MODEL_CACHE.clear()
                logger.info("Cleared all cached Word2Vec models")

