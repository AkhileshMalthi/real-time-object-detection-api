The Streamlit web UI must provide an interface to upload an image, send it to the API, and display the results

**Behavior:**
1.  Allows a user to upload a `.jpg` or `.png` file.
2.  Includes a slider or input field to set the confidence threshold.
3.  A "Detect" button triggers a `POST` request to the `api` service's `/detect` endpoint.
4.  On a successful response, it displays the returned annotated image and the JSON summary.

**Verification:**
- This will be primarily verified through the interaction with the API. When the UI is used to perform a detection, the `output/last_annotated.jpg` file (as per `output-annotated-image`) must be updated. This confirms the UI successfully communicated with the API.
