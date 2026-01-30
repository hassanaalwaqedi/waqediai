# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN groupadd --gid 1000 waqedi && useradd --uid 1000 --gid waqedi --create-home waqedi

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY --chown=waqedi:waqedi src/ ./src/

USER waqedi

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8004/health').raise_for_status()"

EXPOSE 8004

CMD ["uvicorn", "language_service.main:app", "--host", "0.0.0.0", "--port", "8004"]
