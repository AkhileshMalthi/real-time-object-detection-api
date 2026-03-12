# Stage 1: Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p /app/models /app/output && \
    wget -q -O /app/models/yolov8n.pt \
    https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

COPY api/ .

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
