import os

import requests
import streamlit as st
from PIL import Image

st.title("YOLOv8 Object Detection")

# Get API URL from environment variable
API_URL = os.getenv("API_URL", "http://api:8000/detect")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)
    st.write("")

    if st.button("Detect Objects"):
        st.write("Detecting...")
        files = {"image": uploaded_file.getvalue()}
        params = {"confidence_threshold": confidence}
        response = requests.post(API_URL, files=files, data=params)

        if response.status_code == 200:
            # ... logic to display results from API ...
            st.success("Detection complete!")
        else:
            st.error("Error during detection.")
