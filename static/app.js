const video = document.getElementById("camera");
const canvas = document.getElementById("snapshot");
const cameraPlaceholder = document.getElementById("camera-placeholder");
const snapshotPlaceholder = document.getElementById("snapshot-placeholder");
const startCameraButton = document.getElementById("start-camera");
const capturePhotoButton = document.getElementById("capture-photo");
const submitPhotoButton = document.getElementById("submit-photo");
const statusText = document.getElementById("status");
const predictionText = document.getElementById("prediction-text");
const probabilityText = document.getElementById("probability-text");

let cameraStream = null;
let capturedBlob = null;

function setStatus(message) {
  statusText.textContent = message;
}

function setResult(message, probability) {
  predictionText.textContent = message;

  if (typeof probability === "number") {
    probabilityText.textContent = "Cat probability: " + (probability * 100).toFixed(2) + "%";
  } else {
    probabilityText.textContent = "";
  }
}

async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
      audio: false,
    });

    video.srcObject = cameraStream;
    cameraPlaceholder.hidden = true;
    capturePhotoButton.disabled = false;
    setStatus("Camera ready");
  } catch (error) {
    setStatus("Camera blocked");
    setResult("Could not access the camera. Check browser permissions.");
  }
}

function capturePhoto() {
  if (!cameraStream) {
    setResult("Start the camera before capturing a photo.");
    return;
  }

  const width = video.videoWidth;
  const height = video.videoHeight;

  if (!width || !height) {
    setResult("Camera preview is not ready yet. Try again in a moment.");
    return;
  }

  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d").drawImage(video, 0, 0, width, height);
  snapshotPlaceholder.hidden = true;

  canvas.toBlob((blob) => {
    capturedBlob = blob;
    submitPhotoButton.disabled = false;
    setStatus("Photo captured");
    setResult("Photo captured. Submit it for prediction.");
  }, "image/jpeg", 0.92);
}

async function submitPhoto() {
  if (!capturedBlob) {
    setResult("Capture a photo before submitting.");
    return;
  }

  const formData = new FormData();
  formData.append("image", capturedBlob, "webcam.jpg");

  submitPhotoButton.disabled = true;
  setStatus("Predicting");
  setResult("Sending image to the model...");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Prediction request failed.");
    }

    setStatus("Prediction complete");
    setResult(data.prediction, data.cat_probability);
  } catch (error) {
    setStatus("Prediction failed");
    setResult(error.message);
  } finally {
    submitPhotoButton.disabled = false;
  }
}

startCameraButton.addEventListener("click", startCamera);
capturePhotoButton.addEventListener("click", capturePhoto);
submitPhotoButton.addEventListener("click", submitPhoto);
