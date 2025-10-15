// start webcam
const video = document.getElementById('video');
navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
  video.srcObject = stream;
}).catch(err => {
  console.log('Erreur caméra', err);
});

// capture et envoi
document.getElementById('captureBtn').addEventListener('click', async () => {
  const username = document.getElementById('username').value.trim();
  if (!username) {
    alert('Entrez votre nom d’utilisateur.');
    return;
  }
  const canvas = document.getElementById('canvas');
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL('image/png');

  const res = await fetch('/auth/api/face-login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ image: dataUrl, username })
  });
  const json = await res.json();
  document.getElementById('face-result').innerText = json.message;
  if (json.success) {
    // rediriger vers dashboard
    window.location.href = '/';  // adapter
  }
});
