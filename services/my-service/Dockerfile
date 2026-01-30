# syntax=docker/dockerfile:1

# =============================================================================
# WaqediAI Service Dockerfile
# Multi-stage build for production-ready Python services
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# -----------------------------------------------------------------------------
# Stage 2: Production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Security: Run as non-root user
RUN groupadd --gid 1000 waqedi \
    && useradd --uid 1000 --gid waqedi --shell /bin/bash --create-home waqedi

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=waqedi:waqedi src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER waqedi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "service_name.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------------------------------
# Stage 3: Development image (optional, for local dev)
# -----------------------------------------------------------------------------
FROM production as development

USER root

# Install dev dependencies
RUN pip install --no-cache-dir pytest pytest-cov httpx black ruff mypy

USER waqedi

CMD ["uvicorn", "service_name.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
