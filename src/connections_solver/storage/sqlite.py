"""SQLite storage implementation using SQLAlchemy."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from ..core.models import Puzzle, SolverResult, Evaluation
from .base import BaseStorage
from .schemas import Base, PuzzleTable, SolverResultTable, EvaluationTable


class SQLiteStorage(BaseStorage):
    """SQLite storage implementation using SQLAlchemy.

    This implementation provides persistent storage using SQLite.
    Data survives application restarts.
    Suitable for production use with moderate scale.

    Attributes:
        db_path: Path to the SQLite database file
    """

    def __init__(self, db_path: str = "data/connections.db") -> None:
        """Initialize SQLite storage.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create engine and session factory
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.session_factory = sessionmaker(bind=self.engine)

        # Create all tables if they don't exist
        Base.metadata.create_all(self.engine)

    def _get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy session
        """
        return self.session_factory()

    def store_puzzle(self, puzzle: Puzzle) -> Puzzle:
        """Store a puzzle in SQLite.

        Args:
            puzzle: The puzzle to store

        Returns:
            The stored puzzle
        """
        session = self._get_session()
        try:
            puzzle_table = PuzzleTable(
                puzzle_id=str(puzzle.puzzle_id),
                words=puzzle.words,
                solution=puzzle.solution.model_dump(),
                puzzle_metadata=puzzle.metadata,
                created_at=puzzle.created_at,
            )
            session.add(puzzle_table)
            session.commit()
            return puzzle
        finally:
            session.close()

    def get_puzzle(self, puzzle_id: UUID) -> Optional[Puzzle]:
        """Retrieve a puzzle by its ID.

        Args:
            puzzle_id: The unique identifier of the puzzle

        Returns:
            The puzzle if found, None otherwise
        """
        session = self._get_session()
        try:
            puzzle_table = session.query(PuzzleTable).filter(
                PuzzleTable.puzzle_id == str(puzzle_id)
            ).first()

            if not puzzle_table:
                return None

            return Puzzle(
                puzzle_id=puzzle_table.puzzle_id,
                words=puzzle_table.words,
                solution=puzzle_table.solution,
                metadata=puzzle_table.puzzle_metadata,
                created_at=puzzle_table.created_at,
            )
        finally:
            session.close()

    def list_puzzles(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[List[Puzzle], int]:
        """List puzzles with pagination.

        Args:
            limit: Maximum number of puzzles to return
            offset: Number of puzzles to skip

        Returns:
            Tuple of (list of puzzles, total count)
        """
        session = self._get_session()
        try:
            # Get total count
            total = session.query(PuzzleTable).count()

            # Get paginated results, sorted by created_at descending
            puzzle_tables = (
                session.query(PuzzleTable)
                .order_by(desc(PuzzleTable.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )

            puzzles = [
                Puzzle(
                    puzzle_id=p.puzzle_id,
                    words=p.words,
                    solution=p.solution,
                    metadata=p.puzzle_metadata,
                    created_at=p.created_at,
                )
                for p in puzzle_tables
            ]

            return puzzles, total
        finally:
            session.close()

    def store_solve(self, solve: SolverResult) -> SolverResult:
        """Store a solver result in SQLite.

        Args:
            solve: The solver result to store

        Returns:
            The stored solver result
        """
        session = self._get_session()
        try:
            solve_table = SolverResultTable(
                solve_id=str(solve.solve_id),
                puzzle_id=str(solve.puzzle_id),
                solver_type=solve.solver_type,
                predicted_categories=[
                    cat.model_dump() for cat in solve.predicted_categories
                ],
                execution_time_ms=solve.execution_time_ms,
                solver_config=solve.solver_config,
                solved_at=solve.solved_at,
            )
            session.add(solve_table)
            session.commit()
            return solve
        finally:
            session.close()

    def get_solve(self, solve_id: UUID) -> Optional[SolverResult]:
        """Retrieve a solver result by its ID.

        Args:
            solve_id: The unique identifier of the solver result

        Returns:
            The solver result if found, None otherwise
        """
        session = self._get_session()
        try:
            solve_table = session.query(SolverResultTable).filter(
                SolverResultTable.solve_id == str(solve_id)
            ).first()

            if not solve_table:
                return None

            return SolverResult(
                solve_id=solve_table.solve_id,
                puzzle_id=solve_table.puzzle_id,
                solver_type=solve_table.solver_type,
                predicted_categories=solve_table.predicted_categories,
                execution_time_ms=solve_table.execution_time_ms,
                solver_config=solve_table.solver_config,
                solved_at=solve_table.solved_at,
            )
        finally:
            session.close()

    def store_evaluation(self, evaluation: Evaluation) -> Evaluation:
        """Store an evaluation result in SQLite.

        Args:
            evaluation: The evaluation to store

        Returns:
            The stored evaluation
        """
        session = self._get_session()
        try:
            eval_table = EvaluationTable(
                evaluation_id=str(evaluation.evaluation_id),
                solve_id=str(evaluation.solve_id),
                puzzle_id=str(evaluation.puzzle_id),
                metrics=evaluation.metrics.model_dump(),
                evaluated_at=evaluation.evaluated_at,
            )
            session.add(eval_table)
            session.commit()
            return evaluation
        finally:
            session.close()

    def get_evaluation(self, evaluation_id: UUID) -> Optional[Evaluation]:
        """Retrieve an evaluation by its ID.

        Args:
            evaluation_id: The unique identifier of the evaluation

        Returns:
            The evaluation if found, None otherwise
        """
        session = self._get_session()
        try:
            eval_table = session.query(EvaluationTable).filter(
                EvaluationTable.evaluation_id == str(evaluation_id)
            ).first()

            if not eval_table:
                return None

            return Evaluation(
                evaluation_id=eval_table.evaluation_id,
                solve_id=eval_table.solve_id,
                puzzle_id=eval_table.puzzle_id,
                metrics=eval_table.metrics,
                evaluated_at=eval_table.evaluated_at,
            )
        finally:
            session.close()

    def list_evaluations(
        self,
        solver_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Evaluation], int]:
        """List evaluations with optional filtering and pagination.

        Args:
            solver_type: Optional filter by solver type
            limit: Maximum number of evaluations to return
            offset: Number of evaluations to skip

        Returns:
            Tuple of (list of evaluations, total count)
        """
        session = self._get_session()
        try:
            # Build base query
            query = session.query(EvaluationTable)

            # Apply solver_type filter if specified
            if solver_type:
                # Join with solver_results to filter by solver_type
                query = query.join(
                    SolverResultTable,
                    EvaluationTable.solve_id == SolverResultTable.solve_id
                ).filter(SolverResultTable.solver_type == solver_type)

            # Get total count before pagination
            total = query.count()

            # Apply ordering and pagination
            eval_tables = (
                query.order_by(desc(EvaluationTable.evaluated_at))
                .limit(limit)
                .offset(offset)
                .all()
            )

            evaluations = [
                Evaluation(
                    evaluation_id=e.evaluation_id,
                    solve_id=e.solve_id,
                    puzzle_id=e.puzzle_id,
                    metrics=e.metrics,
                    evaluated_at=e.evaluated_at,
                )
                for e in eval_tables
            ]

            return evaluations, total
        finally:
            session.close()
