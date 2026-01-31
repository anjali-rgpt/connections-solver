"""API routes for puzzle solving."""

from fastapi import APIRouter, Depends, HTTPException, status

from connections_solver.core.models import SolverResult
from connections_solver.core.exceptions import (
    PuzzleNotFoundError,
    SolverNotFoundError,
)
from connections_solver.storage.base import BaseStorage
from connections_solver.solvers.registry import SolverRegistry
from connections_solver.api.dependencies import get_storage
from connections_solver.api.models.requests import SolveRequest
from connections_solver.api.models.responses import (
    SolverListResponse,
    SolverInfoResponse,
)

# Import solvers to ensure they are registered
from connections_solver.solvers import random_solver  # noqa: F401 # pylint: disable=unused-import

router = APIRouter(tags=["solver"])


@router.post("/solve", response_model=SolverResult)
def solve_puzzle(
    request: SolveRequest,
    storage: BaseStorage = Depends(get_storage),
) -> SolverResult:
    """Solve a puzzle using the specified solver.

    Args:
        request: Solve request with puzzle ID and solver type
        storage: Storage dependency

    Returns:
        Solver result with predictions and execution time

    Raises:
        HTTPException: If puzzle not found (404) or solver not found (404)
    """
    # Get the puzzle
    puzzle = storage.get_puzzle(request.puzzle_id)
    if puzzle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle {request.puzzle_id} not found",
        )

    # Get the solver
    try:
        solver = SolverRegistry.get_solver(
            request.solver_type, request.solver_config
        )
    except SolverNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    # Solve the puzzle
    result = solver.solve_puzzle(puzzle)

    # Store the result
    stored_result = storage.store_solve(result)

    return stored_result


@router.get("/solvers", response_model=SolverListResponse)
def list_solvers() -> SolverListResponse:
    """List all available solvers.

    Returns:
        List of solver information including names, descriptions, and config schemas
    """
    solvers = SolverRegistry.list_solvers()

    solver_infos = []
    for name, solver_class in solvers.items():
        # Create a temporary instance to get metadata
        instance = solver_class()
        solver_infos.append(
            SolverInfoResponse(
                name=instance.get_name(),
                description=instance.get_description(),
                config_schema=instance.get_config_schema(),
            )
        )

    return SolverListResponse(solvers=solver_infos)
