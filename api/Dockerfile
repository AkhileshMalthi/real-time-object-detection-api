# Use uv for fast dependency installation
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install runtime dependencies (curl for healthcheck, libgl for opencv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install with uv (much faster than pip)
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Create directories for models and output
RUN mkdir -p /app/models /app/output

# Download YOLOv8 model
RUN wget -q -O /app/models/yolov8n.pt \
    https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Copy application code
COPY . .

# Cloud Run sets the PORT env var (default 8080)
ENV PORT=8000
EXPOSE 8000

# Use shell form to allow variable expansion
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
