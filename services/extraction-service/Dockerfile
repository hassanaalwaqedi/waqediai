# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 waqedi && useradd --uid 1000 --gid waqedi --create-home waqedi

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY --chown=waqedi:waqedi src/ ./src/

USER waqedi

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8003/health').raise_for_status()"

EXPOSE 8003

CMD ["uvicorn", "extraction_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
