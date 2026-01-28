from pydantic import BaseModel


class Detection(BaseModel):
    box: list[int]  # [x1, y1, x2, y2]
    label: str
    score: float


class DetectionResponse(BaseModel):
    detections: list[Detection]
    summary: dict[str, int]
    annotated_image: str | None = None  # Base64 encoded image
