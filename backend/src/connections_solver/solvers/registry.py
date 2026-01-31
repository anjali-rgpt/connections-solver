"""Solver registry for managing available solver implementations."""

from typing import Dict, Type, Optional, Any

from .base import BaseSolver
from ..core.exceptions import SolverNotFoundError


class SolverRegistry:
    """Registry for managing and instantiating solver implementations.

    This class maintains a mapping of solver names to solver classes
    and provides methods to register and retrieve solvers.
    """

    _solvers: Dict[str, Type[BaseSolver]] = {}

    @classmethod
    def register(cls, name: str, solver_class: Type[BaseSolver]) -> None:
        """Register a solver implementation.

        Args:
            name: Unique name for the solver
            solver_class: The solver class to register
        """
        cls._solvers[name] = solver_class

    @classmethod
    def get_solver(
        cls, name: str, config: Optional[Dict[str, Any]] = None
    ) -> BaseSolver:
        """Get a solver instance by name.

        Args:
            name: Name of the solver to retrieve
            config: Optional configuration for the solver

        Returns:
            An instance of the requested solver

        Raises:
            SolverNotFoundError: If the solver name is not registered
        """
        if name not in cls._solvers:
            raise SolverNotFoundError(f"Solver '{name}' is not registered")
        return cls._solvers[name](config)

    @classmethod
    def list_solvers(cls) -> Dict[str, Type[BaseSolver]]:
        """List all registered solvers.

        Returns:
            Dictionary mapping solver names to solver classes
        """
        return cls._solvers.copy()

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a solver is registered.

        Args:
            name: Name of the solver to check

        Returns:
            True if the solver is registered, False otherwise
        """
        return name in cls._solvers


def register_solver(name: str):
    """Decorator for easy solver registration.

    Usage:
        @register_solver("my_solver")
        class MySolver(BaseSolver):
            ...

    Args:
        name: Unique name for the solver

    Returns:
        Decorator function
    """

    def decorator(solver_class: Type[BaseSolver]) -> Type[BaseSolver]:
        SolverRegistry.register(name, solver_class)
        return solver_class

    return decorator
