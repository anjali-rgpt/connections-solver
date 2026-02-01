"""Word2Vec embedding provider"""

import numpy as np
import logging
from typing import List
from gensim.models import Word2Vec

from .base import EmbeddingProvider

logger = logging.getLogger(__name__)


class Word2VecEmbeddingProvider(EmbeddingProvider):
    """Word2Vec embedding provider using pre-trained model

    This provider uses the pre-trained Word2Vec model from gensim. 
    Word2Vec was trained on a corpus of text to determine co-occurrence patterns of words. 
    Words with similar meanings will occur in similar contexts, and therefore will have similar embeddings.
    """

    def __init__(self, model_name: str = "word2vec-google-news-300"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load pre-trained Word2Vec model from gensim"""
        try:
            import gensim.downloader as api

            logger.info(f"Loading pre-trained Word2Vec model from gensim: {self.model_name}")
            self.model = api.load(self.model_name)
            logger.info(f"Pre-trained Word2Vec model loaded successfully: {self.model_name}")

        except ImportError:
            logger.error("Gensim is not installed. Please install it using `pip install gensim`")
            raise ImportError("Gensim is not installed. Please install it using `pip install gensim`")

        except Exception as e:
            logger.error(f"Error loading pre-trained Word2Vec model: {e}")
            raise e

    def embed(self, words: List[str]) -> np.ndarray:
        """Convert a list of words into a matrix of embeddings

        Args:
            words: List[str] - List of words to embed

        Returns:
            np.ndarray - Matrix of embeddings of shape(len(words), embedding_dim)
        """
        
        words = [word.strip().lower() for word in words]

        embeddings = []

        for word in words:
            try:
                embedding = self.model[word]
            except KeyError:
                # If word is not found in vocabulary, use zero vector as placeholder

                logger.warning(f"Word '{word}' not found in vocabulary. Using zero vector as placeholder.")
                embedding = np.zeros(self.get_embedding_dims())
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

