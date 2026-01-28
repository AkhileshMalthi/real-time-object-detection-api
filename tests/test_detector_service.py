"""
Unit tests for DetectorService.
"""

from unittest.mock import Mock, patch

import pytest

from api.detector_service import DetectorService
from api.models import DetectionResponse


class TestDetectorService:
    """Test suite for DetectorService class."""

    @pytest.fixture
    def mock_model(self):
        """
        Create a fake YOLO model for testing.
        """
        with patch("api.detector_service.YOLO") as mock_yolo:
            # Setup fake model
            mock_instance = Mock()
            mock_yolo.return_value = mock_instance

            # Mock model.names (class ID -> label mapping)
            mock_instance.names = {0: "person", 1: "car", 2: "dog"}

            yield mock_instance

    @pytest.fixture
    def detector_service(self, mock_model, temp_output_dir):
        """
        Create DetectorService with mocked model.
        """
        return DetectorService(
            model_path="fake_model.pt",  # Path doesn't matter - model is mocked
            output_dir=temp_output_dir,
        )

    def test_service_initialization(self, detector_service, temp_output_dir):
        """
        Service initializes correctly.
        """
        assert detector_service.output_dir == temp_output_dir
        assert detector_service.output_dir.exists()
        assert detector_service.model is not None

    def test_detect_returns_detection_response(self, detector_service, sample_image, mock_model):
        """
        Detect method returns proper response structure.
        """
        # Setup: Create fake YOLO results
        mock_result = Mock()
        mock_box = Mock()

        # Fake detection: person at [100, 100, 200, 200] with 0.95 confidence
        # Note: xyxy[0] needs .tolist() method, so use Mock with return_value
        mock_xyxy = Mock()
        mock_xyxy.tolist.return_value = [100, 100, 200, 200]
        mock_box.xyxy = [mock_xyxy]
        mock_box.conf = [0.95]
        mock_box.cls = [0]  # class_id 0 = 'person' from mock_instance.names

        mock_result.boxes = [mock_box]
        mock_result.plot = Mock(return_value=None)

        mock_model.return_value = [mock_result]

        # Execute: Run detection
        response = detector_service.detect(sample_image, confidence_threshold=0.25)

        # Assert: Verify response structure
        assert isinstance(response, DetectionResponse)
        assert len(response.detections) == 1
        assert response.detections[0].label == "person"
        assert response.detections[0].score == 0.95
        assert response.detections[0].box == [100, 100, 200, 200]
        assert response.summary == {"person": 1}

    def test_detect_multiple_objects(self, detector_service, sample_image, mock_model):
        """
        Detect handles multiple objects correctly.
        """
        # Setup: 2 persons and 1 car
        mock_result = Mock()

        mock_box1 = Mock()
        mock_xyxy1 = Mock()
        mock_xyxy1.tolist.return_value = [100, 100, 200, 200]
        mock_box1.xyxy = [mock_xyxy1]
        mock_box1.conf = [0.92]
        mock_box1.cls = [0]  # person

        mock_box2 = Mock()
        mock_xyxy2 = Mock()
        mock_xyxy2.tolist.return_value = [300, 150, 450, 250]
        mock_box2.xyxy = [mock_xyxy2]
        mock_box2.conf = [0.88]
        mock_box2.cls = [1]  # car

        mock_box3 = Mock()
        mock_xyxy3 = Mock()
        mock_xyxy3.tolist.return_value = [500, 300, 600, 400]
        mock_box3.xyxy = [mock_xyxy3]
        mock_box3.conf = [0.85]
        mock_box3.cls = [0]  # person

        mock_result.boxes = [mock_box1, mock_box2, mock_box3]
        mock_result.plot = Mock(return_value=None)
        mock_model.return_value = [mock_result]

        # Execute
        response = detector_service.detect(sample_image)

        # Assert
        assert len(response.detections) == 3
        assert response.summary == {"person": 2, "car": 1}

        # Verify labels
        labels = [d.label for d in response.detections]
        assert labels.count("person") == 2
        assert labels.count("car") == 1

    def test_detect_no_objects(self, detector_service, sample_image, mock_model):
        """
        Handle empty detections (no objects found).
        """
        # Setup: Empty detection
        mock_result = Mock()
        mock_result.boxes = []  # No detections
        mock_result.plot = Mock(return_value=None)
        mock_model.return_value = [mock_result]

        # Execute
        response = detector_service.detect(sample_image)

        # Assert
        assert len(response.detections) == 0
        assert response.summary == {}

    @patch("api.detector_service.cv2.imwrite")
    def test_saves_annotated_image(
        self, mock_imwrite, detector_service, sample_image, mock_model, temp_output_dir
    ):
        """
        Verify annotated image is saved.
        """
        # Setup
        mock_result = Mock()
        mock_result.boxes = []
        mock_result.plot = Mock(return_value="fake_image_array")
        mock_model.return_value = [mock_result]

        # Execute
        detector_service.detect(sample_image, save_annotated=True)

        # Assert: cv2.imwrite was called with correct path
        expected_path = str(temp_output_dir / "last_annotated.jpg")
        mock_imwrite.assert_called_once_with(expected_path, "fake_image_array")

    def test_confidence_threshold_applied(self, detector_service, sample_image, mock_model):
        """
        Verify confidence threshold is passed to model.
        """
        # Setup
        mock_result = Mock()
        mock_result.boxes = []
        mock_result.plot = Mock(return_value=None)
        mock_model.return_value = [mock_result]

        # Execute with custom threshold
        detector_service.detect(sample_image, confidence_threshold=0.75)

        # Assert: Model called with correct confidence
        mock_model.assert_called_once()
        call_kwargs = mock_model.call_args[1]
        assert call_kwargs["conf"] == 0.75
