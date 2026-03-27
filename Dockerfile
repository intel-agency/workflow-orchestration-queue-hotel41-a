# OS-APOW Application Dockerfile
# Multi-stage build for the Python application

# Build stage
FROM python:3.12-slim AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Production stage
FROM python:3.12-slim AS production

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY src/ ./src/
COPY pyproject.toml ./

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Default command (can be overridden)
# For sentinel: docker run ... sentinel
# For notifier: docker run ... notifier
CMD ["python", "-m", "src.orchestrator_sentinel"]
