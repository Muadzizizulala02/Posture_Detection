const webcam = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const status = document.getElementById('status');
const statusText = status.querySelector('.status-text');
const confidence = document.getElementById('confidence');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const alert = document.getElementById('alert');

let stream = null;
let ws = null;
let sendInterval = null;
let alertTimeout = null;

startBtn.addEventListener('click', startMonitoring);
stopBtn.addEventListener('click', stopMonitoring);

async function startMonitoring() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        webcam.srcObject = stream;

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);
        
        ws.onopen = () => {
            console.log('Connected');
            updateStatus('neutral', 'Monitoring...');
            sendInterval = setInterval(sendFrame, 1000);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleDetection(data);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            stopMonitoring();
        };

        ws.onclose = () => {
            console.log('Disconnected');
        };

        startBtn.disabled = true;
        stopBtn.disabled = false;

    } catch (error) {
        console.error('Camera error:', error);
        alert('Please allow camera access');
    }
}

function stopMonitoring() {
    if (sendInterval) {
        clearInterval(sendInterval);
        sendInterval = null;
    }

    if (ws) {
        ws.close();
        ws = null;
    }

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    webcam.srcObject = null;
    updateStatus('neutral', 'Not Active');
    confidence.textContent = '';
    hideAlert();

    startBtn.disabled = false;
    stopBtn.disabled = true;
}

function sendFrame() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const ctx = canvas.getContext('2d');
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    ctx.drawImage(webcam, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    ws.send(imageData);
}

function handleDetection(data) {
    const { posture, confidence: conf, trigger_animation } = data;

    if (posture === 'sitting_good') {
        updateStatus('good', 'Good Posture');
        hideAlert();
    } else if (posture === 'sitting_bad') {
        updateStatus('bad', 'Poor Posture');
        if (trigger_animation) {
            showAlert();
        }
    } else {
        updateStatus('neutral', 'No Detection');
        hideAlert();
    }

    if (conf > 0) {
        confidence.textContent = `Confidence: ${(conf * 100).toFixed(0)}%`;
    } else {
        confidence.textContent = '';
    }
}

function updateStatus(type, text) {
    status.className = `status-indicator ${type}`;
    statusText.textContent = text;
}

function showAlert() {
    alert.classList.add('show');
    
    if (alertTimeout) {
        clearTimeout(alertTimeout);
    }
    
    alertTimeout = setTimeout(() => {
        hideAlert();
    }, 3000);
}

function hideAlert() {
    alert.classList.remove('show');
    if (alertTimeout) {
        clearTimeout(alertTimeout);
        alertTimeout = null;
    }
}

window.addEventListener('beforeunload', stopMonitoring);