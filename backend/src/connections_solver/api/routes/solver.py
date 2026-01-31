"""API routes for puzzle solving."""

from fastapi import APIRouter, Depends, HTTPException, status

from ...core.models import SolverResult
from ...core.exceptions import (
    PuzzleNotFoundError,
    SolverNotFoundError,
)
from ...logging_config import get_logger
from ...storage.base import BaseStorage
from ...solvers.registry import SolverRegistry
from ..dependencies import get_storage
from ..models.requests import SolveRequest
from ..models.responses import (
    SolverListResponse,
    SolverInfoResponse,
)

logger = get_logger(__name__)

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
    logger.info(f"Solve request: puzzle_id={request.puzzle_id}, solver_type={request.solver_type}")

    # Get the puzzle
    puzzle = storage.get_puzzle(request.puzzle_id)
    if puzzle is None:
        logger.warning(f"Puzzle not found: {request.puzzle_id}")
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
        logger.warning(f"Solver not found: {request.solver_type}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    # Solve the puzzle
    result = solver.solve_puzzle(puzzle)
    logger.info(
        f"Solve completed: solve_id={result.solve_id}, "
        f"execution_time_ms={result.execution_time_ms:.2f}"
    )

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
