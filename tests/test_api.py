"""
Integration tests for API endpoints.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app


class TestDetectEndpoint:
    """Test suite for /detect endpoint."""

    @pytest.fixture
    def client(self):
        """
        Create FastAPI test client.
        """
        return TestClient(app)

    @pytest.fixture
    def mock_detector(self):
        """
        Mock the detector service to avoid loading real YOLO model.
        """
        with patch("api.main.detector") as mock:
            yield mock

    def test_health_endpoint(self, client):
        """
        Health check endpoint works.
        """
        # Execute: Send GET request
        response = client.get("/health")

        # Assert: Verify response
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_detect_endpoint_success(self, client, mock_detector, sample_image_bytes):
        """
        POST /detect returns successful response.
        """
        # Setup: Mock detector to return fake results
        from api.models import Detection, DetectionResponse

        mock_detector.detect.return_value = DetectionResponse(
            detections=[Detection(box=[100, 100, 200, 200], label="person", score=0.92)],
            summary={"person": 1},
        )

        # Execute: Send POST with file and form data
        response = client.post(
            "/detect",
            files={"image": ("test.jpg", sample_image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.25"},
        )

        # Assert: Verify HTTP response
        assert response.status_code == 200

        # Assert: Verify JSON structure
        json_data = response.json()
        assert "detections" in json_data
        assert "summary" in json_data
        assert len(json_data["detections"]) == 1

        # Assert: Verify detection details
        detection = json_data["detections"][0]
        assert detection["label"] == "person"
        assert detection["score"] == 0.92
        assert detection["box"] == [100, 100, 200, 200]

        # Assert: Verify summary
        assert json_data["summary"]["person"] == 1

    def test_detect_endpoint_multiple_objects(self, client, mock_detector, sample_image_bytes):
        """
        Handle multiple detections.
        """
        from api.models import Detection, DetectionResponse

        # Setup: Mock multiple detections
        mock_detector.detect.return_value = DetectionResponse(
            detections=[
                Detection(box=[150, 200, 250, 400], label="person", score=0.92),
                Detection(box=[300, 150, 450, 250], label="car", score=0.88),
            ],
            summary={"person": 1, "car": 1},
        )

        # Execute
        response = client.post(
            "/detect",
            files={"image": ("test.jpg", sample_image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.25"},
        )

        # Assert
        assert response.status_code == 200
        json_data = response.json()

        assert len(json_data["detections"]) == 2
        assert json_data["summary"] == {"person": 1, "car": 1}

        # Verify labels
        labels = [d["label"] for d in json_data["detections"]]
        assert "person" in labels
        assert "car" in labels

    def test_detect_endpoint_no_objects(self, client, mock_detector, sample_image_bytes):
        """
        Handle empty detections.
        """
        from api.models import DetectionResponse

        # Setup: Empty detections
        mock_detector.detect.return_value = DetectionResponse(detections=[], summary={})

        # Execute
        response = client.post(
            "/detect",
            files={"image": ("test.jpg", sample_image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.5"},
        )

        # Assert
        assert response.status_code == 200
        json_data = response.json()

        assert json_data["detections"] == []
        assert json_data["summary"] == {}

    def test_detect_endpoint_custom_confidence(self, client, mock_detector, sample_image_bytes):
        """
        Verify custom confidence threshold is used.
        """
        from api.models import DetectionResponse

        mock_detector.detect.return_value = DetectionResponse(detections=[], summary={})

        # Execute with custom threshold
        response = client.post(
            "/detect",
            files={"image": ("test.jpg", sample_image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.75"},
        )

        # Assert: Endpoint called detector with correct threshold
        assert response.status_code == 200
        mock_detector.detect.assert_called_once()

        # Check the confidence_threshold argument
        call_args = mock_detector.detect.call_args
        assert call_args.args[1] == 0.75  # Second arg is confidence_threshold

    def test_detect_endpoint_missing_image(self, client):
        """
        Verify proper error when image is missing.
        """
        # Execute: Send request without image
        response = client.post("/detect", data={"confidence_threshold": "0.25"})

        # Assert: Should return 422 (Unprocessable Entity)
        assert response.status_code == 422

    def test_detect_endpoint_default_confidence(self, client, mock_detector, sample_image_bytes):
        """
        Verify default confidence threshold.
        """
        from api.models import DetectionResponse

        mock_detector.detect.return_value = DetectionResponse(detections=[], summary={})

        # Execute: Don't provide confidence_threshold
        response = client.post(
            "/detect", files={"image": ("test.jpg", sample_image_bytes, "image/jpeg")}
        )

        # Assert: Should use default 0.25
        assert response.status_code == 200
        call_args = mock_detector.detect.call_args
        assert call_args.args[1] == 0.25


class TestOpenAPISchema:
    """Test OpenAPI documentation generation."""

    def test_openapi_schema_generated(self):
        """
        Verify OpenAPI schema is accessible.
        """
        client = TestClient(app)
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Verify basic schema structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Verify our endpoints are documented
        assert "/health" in schema["paths"]
        assert "/detect" in schema["paths"]
