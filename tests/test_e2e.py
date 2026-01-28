"""
End-to-End (E2E) test
"""

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Mark all tests in this file as e2e tests
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def test_image_path():
    """
    Path to a real test image.
    """
    # Check if sample images exist
    sample_dir = Path("sample")
    if sample_dir.exists():
        images = list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg"))
        if images:
            return images[0]

    # Create a test image if no samples exist
    test_dir = Path("tests/fixtures")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_image = test_dir / "test_image.jpg"

    if not test_image.exists():
        # Create a simple test image with some shapes
        img = Image.new("RGB", (640, 480), color="blue")
        img.save(test_image)

    return test_image


@pytest.fixture(scope="module")
def real_client():
    """
    Real FastAPI client with actual model loaded.
    """
    # Import here so model loads only when running E2E tests
    from api.main import app

    return TestClient(app)


class TestEndToEndDetection:
    """E2E tests for the complete detection pipeline."""

    def test_model_loads_successfully(self, real_client):
        """
        Verify the application starts and model loads.
        """
        # Health check should work if app started successfully
        response = real_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_real_detection_with_actual_image(self, real_client, test_image_path):
        """
        Run real detection with actual YOLO model.
        """
        # Load real image
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()

        # Send real request
        response = real_client.post(
            "/detect",
            files={"image": ("test.jpg", image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.25"},
        )

        # Assert: Request should succeed
        assert response.status_code == 200

        # Assert: Response has correct structure
        json_data = response.json()
        assert "detections" in json_data
        assert "summary" in json_data
        assert isinstance(json_data["detections"], list)
        assert isinstance(json_data["summary"], dict)

        # Assert: Detections have correct structure (if any found)
        for detection in json_data["detections"]:
            assert "box" in detection
            assert "label" in detection
            assert "score" in detection
            assert len(detection["box"]) == 4
            assert 0.0 <= detection["score"] <= 1.0
            assert all(isinstance(x, int) for x in detection["box"])

    def test_annotated_image_actually_saved(self, real_client, test_image_path, tmp_path):
        """
        Verify annotated image is actually written to disk.
        """
        # Setup: Override output directory for this test
        from api import config

        original_output = config.OUTPUT_DIR
        test_output_dir = tmp_path / "output"
        test_output_dir.mkdir()
        config.OUTPUT_DIR = test_output_dir

        # Also update the detector's output directory
        from api.main import detector

        detector.output_dir = test_output_dir

        try:
            # Load and send real image
            with open(test_image_path, "rb") as f:
                image_bytes = f.read()

            response = real_client.post(
                "/detect",
                files={"image": ("test.jpg", image_bytes, "image/jpeg")},
                data={"confidence_threshold": "0.25"},
            )

            assert response.status_code == 200

            # Assert: File was actually created
            output_file = test_output_dir / "last_annotated.jpg"
            assert output_file.exists(), "Annotated image was not saved!"

            # Assert: File is not empty
            assert output_file.stat().st_size > 0, "Annotated image is empty!"

            # Assert: File is a valid image
            img = Image.open(output_file)
            assert img.format == "JPEG"
            assert img.size[0] > 0 and img.size[1] > 0

        finally:
            # Restore original config
            config.OUTPUT_DIR = original_output
            detector.output_dir = original_output

    def test_different_confidence_thresholds(self, real_client, test_image_path):
        """
        Verify confidence threshold actually affects results.
        """
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()

        # Test with low threshold
        response_low = real_client.post(
            "/detect",
            files={"image": ("test.jpg", image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.1"},
        )

        # Reset file pointer
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()

        # Test with high threshold
        response_high = real_client.post(
            "/detect",
            files={"image": ("test.jpg", image_bytes, "image/jpeg")},
            data={"confidence_threshold": "0.8"},
        )

        assert response_low.status_code == 200
        assert response_high.status_code == 200

        low_count = len(response_low.json()["detections"])
        high_count = len(response_high.json()["detections"])

        # Lower threshold should detect >= higher threshold
        # (might be equal if no objects detected or all high confidence)
        assert (
            low_count >= high_count
        ), f"Lower threshold ({low_count}) should detect >= higher threshold ({high_count})"

    def test_handles_image_with_no_objects(self, real_client):
        """
        Verify system handles images with no detections.
        """
        # Create a solid white image (unlikely to contain detectable objects)
        blank_image = Image.new("RGB", (640, 480), color="white")
        img_byte_arr = io.BytesIO()
        blank_image.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)

        response = real_client.post(
            "/detect",
            files={"image": ("blank.jpg", img_byte_arr.getvalue(), "image/jpeg")},
            data={"confidence_threshold": "0.5"},
        )

        assert response.status_code == 200
        json_data = response.json()

        # Should return empty but valid response
        assert json_data["detections"] == []
        assert json_data["summary"] == {}

    @pytest.mark.skipif(not Path("sample").exists(), reason="Requires sample directory with images")
    def test_real_sample_images(self, real_client):
        """
        Test with all available sample images.
        """
        sample_dir = Path("sample")
        images = list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg"))

        assert len(images) > 0, "No sample images found!"

        for image_path in images:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            response = real_client.post(
                "/detect",
                files={"image": (image_path.name, image_bytes, "image/jpeg")},
                data={"confidence_threshold": "0.25"},
            )

            assert response.status_code == 200, f"Failed to detect objects in {image_path.name}"

            json_data = response.json()
            assert "detections" in json_data
            assert "summary" in json_data


class TestModelPerformance:
    """E2E performance and load tests."""

    def test_concurrent_requests_dont_crash(self, real_client, test_image_path):
        """
        Verify async handling works with real model.
        """
        import concurrent.futures

        with open(test_image_path, "rb") as f:
            image_bytes = f.read()

        def make_request():
            response = real_client.post(
                "/detect",
                files={"image": ("test.jpg", image_bytes, "image/jpeg")},
                data={"confidence_threshold": "0.25"},
            )
            return response.status_code

        # Send 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(status == 200 for status in results), "Some concurrent requests failed!"
