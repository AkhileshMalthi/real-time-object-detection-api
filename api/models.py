import io

from fastapi import Form
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field


class ImageValidationError(ValueError):
    """Custom exception for image validation errors."""

    pass


class DetectionRequest(BaseModel):
    """
    Input model for object detection.
    Encapsulates input validation logic.
    """

    confidence_threshold: float = Field(0.25, ge=0.0, le=1.0)

    @classmethod
    def from_form(
        cls, confidence_threshold: float = Form(0.25, ge=0.0, le=1.0)
    ) -> "DetectionRequest":
        """
        Helper to create DetectionRequest from form data.
        """
        return cls(confidence_threshold=confidence_threshold)

    @staticmethod
    def validate_image(image_bytes: bytes) -> Image.Image:
        """
        Validate that the provided bytes are a valid, non-corrupted image.

        Args:
            image_bytes: Raw bytes of the uploaded file.

        Returns:
            PIL.Image.Image: The opened image object.

        Raises:
            ImageValidationError: If image is invalid or corrupted.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))

            # Catches truncated/corrupted files
            img.verify()

            # Re-open because verify() consumes the file pointer/closes the image
            img = Image.open(io.BytesIO(image_bytes))
            return img

        except (UnidentifiedImageError, ValueError, TypeError) as e:
            raise ImageValidationError(
                f"Invalid image file: {str(e)}. Please upload a valid image (JPEG, PNG, etc.)."
            ) from e

        except Exception as e:
            raise ImageValidationError(f"Error processing image: {str(e)}") from e


class Detection(BaseModel):
    box: list[int]  # [x1, y1, x2, y2]
    label: str
    score: float


class DetectionResponse(BaseModel):
    detections: list[Detection]
    summary: dict[str, int]
    annotated_image: str | None = None  # Base64 encoded image
