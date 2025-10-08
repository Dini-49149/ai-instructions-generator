# Multi-stage Dockerfile for AI Instructions Generator web application
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/

FROM base AS builder
RUN pip install --upgrade pip && \
    pip install --no-cache-dir build
RUN python -m build --wheel --outdir /tmp/dist

FROM base AS runtime
COPY --from=builder /tmp/dist /tmp/dist
RUN pip install --no-cache-dir /tmp/dist/*.whl
COPY ai_instructions_app /app/ai_instructions_app

EXPOSE 5000
CMD ["gunicorn", "ai_instructions_app.app:app", "-b", "0.0.0.0:5000"]
