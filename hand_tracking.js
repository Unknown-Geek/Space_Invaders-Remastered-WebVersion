let handsModule;
let hands;
let resultsData = [];

async function initializeHandTracking() {
  handsModule = await import("https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1635986972/hands.js");
  const Hands = handsModule.Hands;
  
  hands = new Hands({
    locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1635986972/${file}`;
    }
  });
  
  hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });
  
  hands.onResults(onResults);
  
  startCamera();
}

function startCamera() {
  const video = document.createElement('video');
  video.style.display = 'none';
  document.body.appendChild(video);
  
  navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
      video.play();
      detectHands(video);
    })
    .catch((err) => {
      console.error("Error accessing the camera", err);
    });
}

async function detectHands(video) {
  await hands.send({ image: video });
  requestAnimationFrame(() => detectHands(video));
}

function onResults(results) {
  resultsData = results.multiHandLandmarks.map((landmarks, index) => ({
    handedness: results.multiHandedness[index].label,
    keypoints: landmarks.map((landmark, i) => ({
      x: landmark.x * window.innerWidth,
      y: landmark.y * window.innerHeight,
      z: landmark.z,
      name: handsModule.HAND_CONNECTIONS[i]
    }))
  }));
}

function getHandsData() {
  return resultsData;
}

window.initializeHandTracking = initializeHandTracking;
window.getHandsData = getHandsData;