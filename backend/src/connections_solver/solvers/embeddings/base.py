"""Base class for embeddings creators"""

import numpy as np
from abc import ABC, abstractmethod
from typing import List, Any

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    @abstractmethod
    def embed(self, words: List[str]) -> np.ndarray:
        """Converts a list of words into a matrix of embeddings of shape(len(words), embedding_dim)
        
        Args:
            words: List[str] - List of words to embed

        Returns:
            np.ndarray - Matrix of embeddings of shape(len(words), embedding_dim)
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the embedding provider"""
        pass

    @abstractmethod
    def get_embedding_dims(self) -> int:
        """Return the number of dimensions of the embeddings"""
        pass

