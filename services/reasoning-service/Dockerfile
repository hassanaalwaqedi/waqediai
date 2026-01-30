# syntax=docker/dockerfile:1

# =============================================================================
# WaqediAI Reasoning Service Dockerfile
# =============================================================================

FROM python:3.11-slim AS base

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 waqedi \
    && useradd --uid 1000 --gid waqedi --shell /bin/bash --create-home waqedi

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=waqedi:waqedi app/ ./app/

# Switch to non-root user
USER waqedi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8007/health').raise_for_status()"

EXPOSE 8007

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
