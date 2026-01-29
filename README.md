# Real-Time Object Detection API

A containerized REST API and web UI for real-time object detection using YOLOv8 and FastAPI.

https://github.com/user-attachments/assets/b6563d6d-4ce8-4d7c-8f90-1dcbf976be2c

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-ultralytics-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## Features

- **Fast Inference** - YOLOv8n model with async non-blocking API
- **Object Detection** - Bounding boxes, labels, confidence scores
- **Summary Stats** - Count of detected objects by class
- **Annotated Images** - Auto-saved with drawn bounding boxes
- **Web UI** - Streamlit interface for easy interaction
- **Containerized** - Docker Compose for simple deployment

## Quick Start
### Using Docker (Recommended)

```bash
# Clone and start
git clone <repo-url>
cd real-time-object-detection-api

# Copy environment file
cp .env.example .env

# Build and run
docker-compose up --build -d

# Check status
docker-compose ps
```

**Access:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Web UI: http://localhost:8501

### Local Development

```bash
# Install dependencies
uv sync

# Download model
bash scripts/download_model.sh

# Run API
uv run uvicorn api.main:app --reload

# Run tests
uv run pytest -m "not e2e"
```

## API Endpoints

### Health Check
```bash
GET /health
```
```json
{"status": "ok"}
```

### Object Detection
```bash
POST /detect
Content-Type: multipart/form-data

# Parameters:
# - image: Image file (required)
# - confidence_threshold: float 0-1 (default: 0.25)
```

```bash
# Example
curl -X POST -F "image=@sample/image01.png" \
  -F "confidence_threshold=0.5" \
  http://localhost:8000/detect
```

**Response:**
```json
{
  "detections": [
    {
      "box": [150, 200, 250, 400],
      "label": "person",
      "score": 0.92
    }
  ],
  "summary": {
    "person": 1
  }
}
```

## Project Structure

```
├── api/                    # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── detector_service.py # YOLO inference logic
│   ├── models.py           # Pydantic schemas
│   ├── config.py           # Environment config
│   ├── Dockerfile          # API container
│   └── requirements.txt
├── ui/                     # Streamlit frontend
│   ├── app.py              # Web interface
│   ├── Dockerfile          # UI container
│   └── requirements.txt
├── tests/                  # Test suite
├── scripts/
│   └── download_model.sh   # Model download script
├── models/                 # YOLO model files
├── output/                 # Annotated images
├── docker-compose.yml      # Container orchestration
└── .env.example            # Environment template
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | 8000 | API server port |
| `UI_PORT` | 8501 | Streamlit UI port |
| `MODEL_PATH` | /app/models/yolov8n.pt | YOLO model path |
| `OUTPUT_DIR` | /app/output | Annotated images directory |
| `CONFIDENCE_THRESHOLD_DEFAULT` | 0.25 | Default detection threshold |

## Testing

```bash
# Fast tests (mocked model)
uv run pytest -m "not e2e"

# Full E2E tests (real model)
uv run pytest -m e2e

# With coverage
uv run pytest --cov=api --cov-report=html
```

## Development

```bash
# Install dev dependencies
uv sync

# Run pre-commit hooks
uv run pre-commit run --all-files

# Lint
uv run ruff check api/ ui/ tests/

# Format
uv run ruff format api/ ui/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) for details.
