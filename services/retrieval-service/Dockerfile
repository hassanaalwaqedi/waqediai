# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN groupadd --gid 1000 waqedi \
    && useradd --uid 1000 --gid waqedi --shell /bin/bash --create-home waqedi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=waqedi:waqedi app/ ./app/

USER waqedi

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8006/health').raise_for_status()"

EXPOSE 8006

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"]
