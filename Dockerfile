# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install UV
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY data/ ./data/

# Install dependencies using UV (system-wide in container)
RUN uv pip install --system .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.connections_solver.main:app", "--host", "0.0.0.0", "--port", "8000"]
