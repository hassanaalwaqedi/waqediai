# syntax=docker/dockerfile:1

# =============================================================================
# WaqediAI Ingestion Service Dockerfile
# =============================================================================

FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 waqedi \
    && useradd --uid 1000 --gid waqedi --shell /bin/bash --create-home waqedi

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=waqedi:waqedi src/ ./src/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER waqedi

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8002/health').raise_for_status()"

EXPOSE 8002

CMD ["uvicorn", "ingestion_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
