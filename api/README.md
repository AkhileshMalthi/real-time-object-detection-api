# Object Detection API

FastAPI backend for YOLOv8 object detection.

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{"status": "ok"}
```

### Object Detection

```http
POST /detect
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image` | file | Yes | Image file (JPG, JPEG, PNG) |
| `confidence_threshold` | float | No | Min confidence 0-1 (default: 0.25) |

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
  },
  "annotated_image": "base64_encoded_jpeg..."
}
```

**Side Effects:**
- Saves annotated image to `/app/output/last_annotated.jpg`

## Project Structure

```
api/
├── main.py             # FastAPI app and endpoints
├── detector_service.py # YOLO inference logic
├── models.py           # Pydantic schemas
├── config.py           # Environment config
├── Dockerfile          # Container definition
└── requirements.txt    # Production dependencies
```

## Running Locally

```bash
# From project root
uv run uvicorn api.main:app --reload --port 8000
```

## Docker

```bash
docker build -t detection-api .
docker run -p 8000:8000 -v ./output:/app/output detection-api
```
