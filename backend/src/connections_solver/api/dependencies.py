"""FastAPI dependencies for dependency injection."""

from functools import lru_cache

from ..storage.base import BaseStorage
from ..storage.memory import MemoryStorage
from ..storage.sqlite import SQLiteStorage
from ..config import settings


@lru_cache()
def get_storage() -> BaseStorage:
    """Get the storage instance (cached singleton).

    Returns:
        Storage instance based on configuration

    Note:
        The lru_cache decorator ensures singleton behavior per process.
        Supports both memory and SQLite storage backends.
    """
    if settings.storage_type == "sqlite":
        return SQLiteStorage(db_path=settings.database_path)
    return MemoryStorage()  # Default to memory storage
