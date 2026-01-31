"""FastAPI dependencies for dependency injection."""

from functools import lru_cache

from ..storage.base import BaseStorage
from ..storage.memory import MemoryStorage
from ..config import settings


@lru_cache()
def get_storage() -> BaseStorage:
    """Get the storage instance (cached singleton).

    Returns:
        Storage instance based on configuration

    Note:
        For bare minimum implementation, only memory storage is supported.
        The lru_cache decorator ensures singleton behavior per process.
    """
    if settings.storage_type == "memory":
        return MemoryStorage()
    return MemoryStorage()  # Default fallback
