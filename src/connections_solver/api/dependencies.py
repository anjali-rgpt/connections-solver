"""FastAPI dependencies for dependency injection."""

from functools import lru_cache

from connections_solver.storage.base import BaseStorage
from connections_solver.storage.memory import MemoryStorage
from connections_solver.config import settings


# Global storage instance (singleton for in-memory storage)
_storage_instance: BaseStorage = None  # type: ignore


@lru_cache()
def get_storage() -> BaseStorage:
    """Get the storage instance (singleton pattern).

    Returns:
        Storage instance based on configuration

    Note:
        For bare minimum implementation, only memory storage is supported.
    """
    global _storage_instance  # pylint: disable=global-statement

    if _storage_instance is None:
        if settings.storage_type == "memory":
            _storage_instance = MemoryStorage()
        else:
            # Default to memory storage
            _storage_instance = MemoryStorage()

    return _storage_instance
