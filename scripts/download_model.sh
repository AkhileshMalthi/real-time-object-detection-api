#!/bin/bash
# Create the models directory if it doesn't exist
mkdir -p models

# URL of the YOLOv8n model
MODEL_URL="https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"

# Download the model using wget or curl
wget -O models/yolov8n.pt $MODEL_URL

echo "Model downloaded successfully to models/yolov8n.pt"

# File: scripts/download_model.sh

# Behavior:

# The script must download a pre-trained YOLO model (e.g., yolov8n.pt) from a public URL.
# It must save the model to the models/ directory.
# The Dockerfile for the api service should execute this script or a similar command to ensure the model is present before the application starts.
# Verification:

# Check that no .pt files are present in the Git history.
# After building and running the containers, verify that the model file exists at the path specified by the MODEL_PATH environment variable inside the api containe
