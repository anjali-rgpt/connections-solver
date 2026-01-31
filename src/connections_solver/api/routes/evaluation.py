"""API routes for solver evaluation."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from connections_solver.core.models import Evaluation
from connections_solver.logging_config import get_logger
from connections_solver.storage.base import BaseStorage
from connections_solver.evaluation.comparator import compare_solver_result
from connections_solver.api.dependencies import get_storage
from connections_solver.api.models.requests import EvaluateRequest
from connections_solver.api.models.responses import EvaluationListResponse

logger = get_logger(__name__)

router = APIRouter(tags=["evaluation"])


@router.post("/evaluate", response_model=Evaluation)
def evaluate_solver_result(
    request: EvaluateRequest,
    storage: BaseStorage = Depends(get_storage),
) -> Evaluation:
    """Evaluate a solver result against ground truth.

    Args:
        request: Evaluation request with solve ID
        storage: Storage dependency

    Returns:
        Evaluation with comprehensive metrics

    Raises:
        HTTPException: If solve or puzzle not found (404)
    """
    logger.info(f"Evaluation request: solve_id={request.solve_id}")

    # Get the solver result
    solve = storage.get_solve(request.solve_id)
    if solve is None:
        logger.warning(f"Solve not found: {request.solve_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solve {request.solve_id} not found",
        )

    # Get the puzzle (for ground truth)
    puzzle = storage.get_puzzle(solve.puzzle_id)
    if puzzle is None:
        logger.warning(f"Puzzle not found: {solve.puzzle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle {solve.puzzle_id} not found",
        )

    # Compare solver result against ground truth
    metrics = compare_solver_result(solve, puzzle.solution)

    logger.info(
        f"Evaluation completed: exact_matches={metrics.exact_matches}, "
        f"word_accuracy={metrics.word_accuracy:.2f}"
    )

    # Create evaluation
    evaluation = Evaluation(
        solve_id=solve.solve_id,
        puzzle_id=puzzle.puzzle_id,
        metrics=metrics,
    )

    # Store evaluation
    stored_evaluation = storage.store_evaluation(evaluation)

    return stored_evaluation


@router.get("/evaluations", response_model=EvaluationListResponse)
def list_evaluations(
    solver_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    storage: BaseStorage = Depends(get_storage),
) -> EvaluationListResponse:
    """List evaluations with optional filtering.

    Args:
        solver_type: Optional filter by solver type
        limit: Maximum number of evaluations to return (default: 20)
        offset: Number of evaluations to skip (default: 0)
        storage: Storage dependency

    Returns:
        List of evaluations with pagination metadata
    """
    evaluations, total = storage.list_evaluations(
        solver_type=solver_type,
        limit=limit,
        offset=offset,
    )

    return EvaluationListResponse(
        evaluations=evaluations,
        total=total,
        limit=limit,
        offset=offset,
    )
