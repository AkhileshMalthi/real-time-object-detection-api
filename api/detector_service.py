"""
Object detection service using YOLOv8.
Handles model inference, result processing, and image annotation.
"""

from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Boxes, Results

from .models import Detection, DetectionResponse


class DetectorService:
    """Service for performing object detection with YOLOv8."""

    def __init__(self, model_path: str, output_dir: Path):
        """
        Initialize the detector service.

        Args:
            model_path: Path to the YOLO model file
            output_dir: Directory to save annotated images
        """
        self.model = YOLO(model_path)
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect(
        self, image: Image.Image, confidence_threshold: float = 0.25, save_annotated: bool = True
    ) -> DetectionResponse:
        """
        Perform object detection on an image.

        Args:
            image: PIL Image to process
            confidence_threshold: Minimum confidence score for detections
            save_annotated: Whether to save annotated image to disk

        Returns:
            DetectionResponse with detections and summary
        """
        # Convert PIL Image to numpy array
        img_array = np.array(image)

        # Perform inference
        results: list[Results] = self.model(img_array, conf=confidence_threshold)
        result: Results = results[0]

        # Process detections
        detections = self._extract_detections(result.boxes)

        # Create summary
        labels = [d.label for d in detections]
        summary = dict(Counter(labels))

        # Save annotated image if requested
        if save_annotated:
            self._save_annotated_image(result)

        return DetectionResponse(detections=detections, summary=summary)

    def _extract_detections(self, boxes: Boxes) -> list[Detection]:
        """
        Extract detection objects from YOLO boxes.

        Args:
            boxes: YOLO Boxes object containing detection data

        Returns:
            List of Detection objects
        """
        detections = []

        for box in boxes:
            # Extract box coordinates (xyxy format)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Extract confidence score
            score = float(box.conf[0])

            # Extract class label
            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            # Create Detection object
            detections.append(
                Detection(
                    box=[int(x1), int(y1), int(x2), int(y2)], label=label, score=round(score, 2)
                )
            )

        return detections

    def _save_annotated_image(self, result: Results) -> None:
        """
        Save annotated image with bounding boxes and labels.

        Args:
            result: YOLO Results object
        """
        annotated_img = result.plot()
        output_path = self.output_dir / "last_annotated.jpg"
        cv2.imwrite(str(output_path), annotated_img)
