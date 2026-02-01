"""Embeddings module for converting words to vector representations"""

from .base import EmbeddingProvider
from .word2vec import Word2VecEmbeddingProvider

__all__ = ["EmbeddingProvider", "Word2VecEmbeddingProvider"]
