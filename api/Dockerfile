# Stage 1: Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Enable bytecode compilation and use copy mode for linking
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files first for layer caching
COPY uv.lock pyproject.toml ./

# Install dependencies into /app/.venv without installing the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies (curl for healthcheck, libgl for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Ensure the virtual environment is used
ENV PATH="/app/.venv/bin:$PATH"

# Create directories and download YOLOv8 model
RUN mkdir -p /app/models /app/output && \
    wget -q -O /app/models/yolov8n.pt \
    https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Copy application code
COPY api/ .

# Cloud Run sets the PORT env var
ENV PORT=8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
