# ruff: noqa: I001
import asyncio

from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse

# Support both package imports (for testing) and direct imports (for Docker)
try:  # noqa: I001
    from .config import MODEL_PATH, OUTPUT_DIR
    from .detector_service import DetectorService
    from .models import DetectionRequest, DetectionResponse, ImageValidationError
except ImportError:
    from config import MODEL_PATH, OUTPUT_DIR
    from detector_service import DetectorService

    from models import DetectionRequest, DetectionResponse, ImageValidationError

app = FastAPI(title="YOLOv8 Object Detection API")


@app.exception_handler(ImageValidationError)
async def image_validation_exception_handler(request: Request, exc: ImageValidationError):
    """Global handler for image validation errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# Initialize detector service on startup
detector = DetectorService(model_path=MODEL_PATH, output_dir=OUTPUT_DIR)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    image: UploadFile = File(...),
    request: DetectionRequest = Depends(DetectionRequest.from_form),
) -> DetectionResponse:
    """
    Detect objects in an uploaded image.

    Runs detection in a thread pool to avoid blocking the event loop.

    Args:
        image: Image file to process
        request: Detection parameters and validation logic

    Returns:
        Detection results with bounding boxes, labels, scores, and summary
    """
    image_bytes = await image.read()
    img = request.validate_image(image_bytes)

    # Run detection in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, detector.detect, img, request.confidence_threshold)

    return result
