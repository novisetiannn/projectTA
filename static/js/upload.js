const button = document.querySelector(".button");
const nameInput = document.querySelector("#name");
const rollInput = document.querySelector("#roll");
const imageData = document.querySelector("#image_data");
const video = document.querySelector("#video");
const previewContainer = document.getElementById("preview-container");

// Toggle button class based on inputs
function toggleClass() {
  if (
    nameInput.value !== "" &&
    rollInput.value !== "" &&
    (document.querySelector(".file-upload-input").files.length > 0 || imageData.value !== "")
  ) {
    button.classList.add("active");
  } else {
    button.classList.remove("active");
  }
}

// Open camera for video capture
function openCamera() {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      video.srcObject = stream;
      video.play();
    })
    .catch(function (err) {
      console.error("An error occurred: " + err);
    });
}

// Capture image from video stream
function captureImage() {
  let canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  let base64data = canvas.toDataURL("image/jpeg");
  imageData.value = base64data;

  // Create an image element for the preview
  const imgElement = document.createElement('img');
  imgElement.src = base64data;
  imgElement.className = 'file-upload-image';
  imgElement.style.maxWidth = '150px';
  imgElement.style.margin = '10px';
  previewContainer.appendChild(imgElement);

  video.pause();
  video.srcObject.getVideoTracks()[0].stop();
}

// Read uploaded file URL
function previewImages(input) {
  if (input.files) {
    const files = Array.from(input.files);
    if (files.length > 5) {
      alert("You can upload a maximum of 5 images.");
      input.value = ""; // Clear the input
      return;
    }

    previewContainer.innerHTML = ""; // Clear previous previews
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = function (e) {
        const imgElement = document.createElement('img');
        imgElement.src = e.target.result;
        imgElement.className = 'file-upload-image';
        imgElement.style.maxWidth = '150px';
        imgElement.style.margin = '10px';
        previewContainer.appendChild(imgElement);
      };
      reader.readAsDataURL(file);
    });
  }
}

// Validate form submission
document.querySelector("form").addEventListener("submit", function (event) {
  if (imageData.value === "" && document.querySelector(".file-upload-input").files.length === 0) {
    alert("Please capture or upload an image.");
    event.preventDefault();
  }
});

// Initialize camera
openCamera();

// Listen for changes in inputs to toggle button state
nameInput.addEventListener("input", toggleClass);
rollInput.addEventListener("input", toggleClass);
document.querySelector(".file-upload-input").addEventListener("change", toggleClass);
imageData.addEventListener("input", toggleClass);