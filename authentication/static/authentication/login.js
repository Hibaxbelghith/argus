// static/authentication/login.js
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("camera");
  const captureBtn = document.getElementById("faceLoginBtn");
  const usernameInput = document.getElementById("usernameInput");
  const feedback = document.getElementById("faceFeedback");

  // --- Initialiser la webcam ---
  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
    } catch (err) {
      feedback.textContent = "Erreur d’accès à la caméra.";
    }
  }

  // --- Convertir le flux vidéo en image base64 ---
  function captureFrame() {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL("image/png");
  }

  // --- Envoi à l’API Django ---
  async function sendToServer(imageData, username) {
    const response = await fetch("/auth/face-login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageData, username }),
    });

    const result = await response.json();
    feedback.textContent = result.message;
    if (result.success) {
      window.location.href = "/auth/dashboard/";
    }
  }

  captureBtn.addEventListener("click", async () => {
    const username = usernameInput.value.trim();
    if (!username) {
      feedback.textContent = "Entrez votre nom d'utilisateur.";
      return;
    }
    const img = captureFrame();
    feedback.textContent = "Analyse du visage...";
    await sendToServer(img, username);
  });

  startCamera();
});
