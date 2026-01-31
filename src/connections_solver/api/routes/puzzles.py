"""API routes for puzzle management."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from connections_solver.core.models import Puzzle
from connections_solver.core.exceptions import PuzzleNotFoundError
from connections_solver.logging_config import get_logger
from connections_solver.storage.base import BaseStorage
from connections_solver.api.dependencies import get_storage
from connections_solver.api.models.requests import CreatePuzzleRequest
from connections_solver.api.models.responses import PuzzleListResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/puzzles", tags=["puzzles"])


@router.post("", response_model=Puzzle, status_code=status.HTTP_201_CREATED)
def create_puzzle(
    request: CreatePuzzleRequest,
    storage: BaseStorage = Depends(get_storage),
) -> Puzzle:
    """Create a new puzzle with solution.

    Args:
        request: Puzzle creation request
        storage: Storage dependency

    Returns:
        Created puzzle with assigned ID

    Raises:
        HTTPException: If puzzle data is invalid
    """
    puzzle = Puzzle(
        words=request.words,
        solution=request.solution,
        metadata=request.metadata,
    )

    stored_puzzle = storage.store_puzzle(puzzle)
    logger.info(f"Puzzle created: puzzle_id={stored_puzzle.puzzle_id}")
    return stored_puzzle


@router.get("/{puzzle_id}", response_model=Puzzle)
def get_puzzle(
    puzzle_id: UUID,
    storage: BaseStorage = Depends(get_storage),
) -> Puzzle:
    """Retrieve a puzzle by ID.

    Args:
        puzzle_id: Unique identifier of the puzzle
        storage: Storage dependency

    Returns:
        The requested puzzle

    Raises:
        HTTPException: If puzzle is not found (404)
    """
    puzzle = storage.get_puzzle(puzzle_id)

    if puzzle is None:
        logger.warning(f"Puzzle not found: {puzzle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle {puzzle_id} not found",
        )

    logger.info(f"Puzzle retrieved: puzzle_id={puzzle_id}")
    return puzzle


@router.get("", response_model=PuzzleListResponse)
def list_puzzles(
    limit: int = 20,
    offset: int = 0,
    storage: BaseStorage = Depends(get_storage),
) -> PuzzleListResponse:
    """List all puzzles with pagination.

    Args:
        limit: Maximum number of puzzles to return (default: 20)
        offset: Number of puzzles to skip (default: 0)
        storage: Storage dependency

    Returns:
        List of puzzles with pagination metadata
    """
    puzzles, total = storage.list_puzzles(limit=limit, offset=offset)

    return PuzzleListResponse(
        puzzles=puzzles,
        total=total,
        limit=limit,
        offset=offset,
    )
