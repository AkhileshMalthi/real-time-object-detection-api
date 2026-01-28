import os
from pathlib import Path

# API configuration
API_PORT = int(os.getenv("API_PORT", "8000"))

# UI configuration
UI_PORT = int(os.getenv("UI_PORT", "8501"))

# Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/yolov8n.pt")

# Detection configuration
CONFIDENCE_THRESHOLD_DEFAULT = float(os.getenv("CONFIDENCE_THRESHOLD_DEFAULT", "0.25"))

# Output configuration
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/app/output"))
