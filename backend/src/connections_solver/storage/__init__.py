"""Storage implementations for persisting puzzles and results."""
from connections_solver.storage.base import BaseStorage
from connections_solver.storage.memory import MemoryStorage

__all__ = ["BaseStorage", "MemoryStorage"]
