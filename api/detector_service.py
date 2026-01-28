"""
Object detection service using YOLOv8.
Handles model inference, result processing, and image annotation.
"""

import base64
from collections import Counter
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Boxes, Results

# Support both package imports (for testing) and direct imports (for Docker)
try:
    from .models import Detection, DetectionResponse
except ImportError:
    from models import Detection, DetectionResponse


class DetectorService:
    """Service for performing object detection with YOLOv8."""

    def __init__(self, model_path: str, output_dir: Path):
        self.model = YOLO(model_path)
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect(
        self, image: Image.Image, confidence_threshold: float = 0.25, save_annotated: bool = True
    ) -> DetectionResponse:
        """Perform object detection on an image."""
        img_array = np.array(image)

        # Perform inference
        results: list[Results] = self.model(img_array, conf=confidence_threshold)
        result: Results = results[0]

        # Process detections
        detections = self._extract_detections(result.boxes)

        # Create summary
        labels = [d.label for d in detections]
        summary = dict(Counter(labels))

        # Get annotated image as base64
        annotated_b64 = self._get_annotated_base64(result)

        # Save to disk if requested
        if save_annotated:
            self._save_annotated_image(result)

        return DetectionResponse(
            detections=detections, summary=summary, annotated_image=annotated_b64
        )

    def _extract_detections(self, boxes: Boxes) -> list[Detection]:
        """Extract detection objects from YOLO boxes."""
        detections = []

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            score = float(box.conf[0])
            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            detections.append(
                Detection(
                    box=[int(x1), int(y1), int(x2), int(y2)], label=label, score=round(score, 2)
                )
            )

        return detections

    def _get_annotated_base64(self, result: Results) -> str:
        """Get annotated image as base64 string."""
        annotated_img = result.plot()
        # Convert BGR to RGB
        annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(annotated_rgb)

        buffer = BytesIO()
        pil_img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _save_annotated_image(self, result: Results) -> None:
        """Save annotated image to disk."""
        annotated_img = result.plot()
        output_path = self.output_dir / "last_annotated.jpg"
        cv2.imwrite(str(output_path), annotated_img)
