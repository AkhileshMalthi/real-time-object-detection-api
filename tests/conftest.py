import io

import pytest
from PIL import Image


@pytest.fixture
def sample_image():
    """
    Create a simple test image in memory.
    """
    # Create a simple red image
    img = Image.new("RGB", (640, 480), color="red")
    return img


@pytest.fixture
def sample_image_bytes(sample_image):
    """
    Convert PIL Image to bytes (like an uploaded file).
    """
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()


@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Create a temporary directory for test outputs.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
