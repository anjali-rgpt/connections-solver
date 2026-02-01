"""SQLAlchemy table schemas for persistent storage."""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses CHAR(36) to store UUIDs as strings in a format compatible with SQLite.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load the appropriate type for the dialect."""
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        """Convert UUID to string for storage."""
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        """Convert string back to UUID when loading."""
        if value is None:
            return value
        return value  # Return as string to match Pydantic UUID behavior


Base = declarative_base()


class PuzzleTable(Base):
    """SQLAlchemy table for storing puzzles.

    Attributes:
        puzzle_id: Primary key, unique identifier
        words: JSON array of 16 words
        solution: JSON object containing the solution with categories
        puzzle_metadata: Optional JSON object with puzzle metadata
        created_at: Timestamp when puzzle was created
    """

    __tablename__ = "puzzles"

    puzzle_id = Column(GUID, primary_key=True, default=lambda: str(uuid4()))
    words = Column(JSON, nullable=False)
    solution = Column(JSON, nullable=False)
    puzzle_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SolverResultTable(Base):
    """SQLAlchemy table for storing solver results.

    Attributes:
        solve_id: Primary key, unique identifier
        puzzle_id: Foreign key to puzzles table
        solver_type: Name of the solver used
        predicted_categories: JSON array of predicted category objects
        execution_time_ms: Time taken to solve in milliseconds
        solver_config: Optional JSON object with solver configuration
        solved_at: Timestamp when puzzle was solved
    """

    __tablename__ = "solver_results"

    solve_id = Column(GUID, primary_key=True, default=lambda: str(uuid4()))
    puzzle_id = Column(GUID, nullable=False)
    solver_type = Column(String, nullable=False)
    predicted_categories = Column(JSON, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    solver_config = Column(JSON, nullable=True)
    solved_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class EvaluationTable(Base):
    """SQLAlchemy table for storing evaluations.

    Attributes:
        evaluation_id: Primary key, unique identifier
        solve_id: Foreign key to solver_results table
        puzzle_id: Foreign key to puzzles table
        metrics: JSON object containing evaluation metrics
        evaluated_at: Timestamp when evaluation was performed
    """

    __tablename__ = "evaluations"

    evaluation_id = Column(GUID, primary_key=True, default=lambda: str(uuid4()))
    solve_id = Column(GUID, nullable=False)
    puzzle_id = Column(GUID, nullable=False)
    metrics = Column(JSON, nullable=False)
    evaluated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
