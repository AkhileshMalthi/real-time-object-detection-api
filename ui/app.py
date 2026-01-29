"""
YOLOv8 Object Detection UI - Single Column Layout
"""

import base64
import os
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Object Detection", layout="centered")

# Header
st.title("Object Detection")

# Settings in sidebar
with st.sidebar:
    st.header("Settings")
    confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)

    st.divider()

    base_url = os.getenv("API_URL", "http://api:8000").rstrip("/")
    DETECT_URL = f"{base_url}/detect"
    HEALTH_URL = f"{base_url}/health"

    try:
        if requests.get(HEALTH_URL, timeout=3).status_code == 200:
            st.success("API Connected")
        else:
            st.warning("API Issue")
    except requests.exceptions.RequestException:
        st.error("API Offline")

# File upload
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Show uploaded image (smaller preview)
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=400)

    # Detect button
    if st.button("Detect Objects", type="primary"):
        with st.spinner("Detecting..."):
            try:
                uploaded_file.seek(0)
                files = {"image": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                data = {"confidence_threshold": str(confidence)}

                response = requests.post(DETECT_URL, files=files, data=data, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    detections = result.get("detections", [])
                    summary = result.get("summary", {})
                    annotated_b64 = result.get("annotated_image")

                    st.divider()

                    # Annotated image (full width)
                    if annotated_b64:
                        img_bytes = base64.b64decode(annotated_b64)
                        annotated_img = Image.open(BytesIO(img_bytes))
                        st.image(
                            annotated_img, caption="Detection Results", use_container_width=True
                        )

                    # Summary metrics
                    if summary:
                        st.subheader(f"{len(detections)} objects detected")
                        cols = st.columns(min(len(summary), 4))
                        for idx, (label, count) in enumerate(summary.items()):
                            with cols[idx % 4]:
                                st.metric(label.capitalize(), count)
                    else:
                        st.info("No objects detected at this confidence level")

                    # Details (expandable)
                    if detections:
                        with st.expander("View Details"):
                            st.dataframe(
                                [
                                    {
                                        "Label": d["label"].capitalize(),
                                        "Confidence": f"{d['score']:.0%}",
                                        "Box": str(d["box"]),
                                    }
                                    for d in detections
                                ],
                                use_container_width=True,
                                hide_index=True,
                            )
                else:
                    st.error(f"API Error: {response.status_code}")

            except requests.exceptions.Timeout:
                st.error("Request timed out")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API")
            except Exception as e:
                st.error(str(e))
