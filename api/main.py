import asyncio
import io

from fastapi import FastAPI, File, Form, UploadFile
from PIL import Image

# Support both package imports (for testing) and direct imports (for Docker)
try:  # noqa: I001
    from .config import MODEL_PATH, OUTPUT_DIR
    from .detector_service import DetectorService
    from .models import DetectionResponse
except ImportError:
    from config import MODEL_PATH, OUTPUT_DIR
    from detector_service import DetectorService

    from models import DetectionResponse

app = FastAPI(title="YOLOv8 Object Detection API")

# Initialize detector service on startup
detector = DetectorService(model_path=MODEL_PATH, output_dir=OUTPUT_DIR)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    image: UploadFile = File(...), confidence_threshold: float = Form(0.25)
) -> DetectionResponse:
    """
    Detect objects in an uploaded image.

    Runs detection in a thread pool to avoid blocking the event loop.

    Args:
        image: Image file to process
        confidence_threshold: Minimum confidence score for detections (0.0-1.0)

    Returns:
        Detection results with bounding boxes, labels, scores, and summary
    """
    # Read and parse uploaded image
    image_bytes = await image.read()
    img = Image.open(io.BytesIO(image_bytes))

    # Run detection in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, detector.detect, img, confidence_threshold)

    return result
