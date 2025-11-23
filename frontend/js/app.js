class AudioStreamer {
    constructor() {
        this.websocket = null;
        this.mediaRecorder = null;
        this.audioContext = null;
        this.analyser = null;
        this.source = null;
        this.stream = null;
        this.isRecording = false;
        this.canvas = document.getElementById('waveform');
        this.canvasCtx = this.canvas.getContext('2d');
        
        this.videoElement = document.getElementById('webcam-video');
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.testAudioBtn = document.getElementById('test-audio-btn');
        this.statusEl = document.getElementById('connection-status');
        this.listeningEl = document.getElementById('listening-status');
        this.logEl = document.getElementById('conversation-log');

        this.bindEvents();
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.start());
        this.stopBtn.addEventListener('click', () => this.stop());
        this.testAudioBtn.addEventListener('click', () => this.testAudio());
    }

    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.hostname || 'localhost';
            const port = '8000'; 
            const wsUrl = `${protocol}//${host}:${port}/ws/audio`;
            
            console.log(`Connecting to WebSocket at ${wsUrl}`);
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.statusEl.innerHTML = '● Connected';
                this.statusEl.className = 'status connected';
                resolve();
            };

            this.websocket.onclose = () => {
                this.statusEl.innerHTML = '● Disconnected';
                this.statusEl.className = 'status disconnected';
                this.stop();
            };

            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket Error:', error);
            };
        });
    }

    handleMessage(data) {
        if (data instanceof Blob) {
            this.playAudioResponse(data);
        } else {
            try {
                const message = JSON.parse(data);
                if (message.type === 'text_update') {
                    this.updateConversationLog(message.text, 'model');
                }
            } catch (e) {
                console.log("Received text:", data);
            }
        }
    }

    updateConversationLog(text, sender) {
        // Remove empty state if it exists
        const emptyState = this.logEl.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        let lastMsg = this.logEl.lastElementChild;
        if (lastMsg && lastMsg.dataset.sender === sender && sender === 'model') {
            lastMsg.textContent = text; 
        } else {
            const div = document.createElement('div');
            div.className = `message ${sender}-message`;
            div.dataset.sender = sender;
            div.textContent = text;
            this.logEl.appendChild(div);
            this.logEl.scrollTop = this.logEl.scrollHeight;
        }
    }

    async start() {
        try {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            await this.connectWebSocket();
            
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error("Browser does not support audio/video capture or not in a secure context.");
            }

            // Request both audio and video
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
            
            // Attach stream to video element
            this.videoElement.srcObject = this.stream;

            // Setup Audio Analyser
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256; // For better visualization
            this.source = this.audioContext.createMediaStreamSource(this.stream);
            this.source.connect(this.analyser);
            
            this.drawWaveform();

            // Setup Recorder (Audio only for sending to backend)
            // Note: We pass the same stream which has video, but MediaRecorder might record both unless specified.
            // The backend expects audio. Let's just record the audio track if possible, or rely on backend to ignore video.
            // Actually, let's create a stream with only audio tracks for the MediaRecorder to be safe.
            const audioStream = new MediaStream(this.stream.getAudioTracks());
            this.mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
            
            this.mediaRecorder.ondataavailable = async (e) => {
                if (e.data.size > 0 && this.websocket.readyState === WebSocket.OPEN) {
                    this.websocket.send(e.data);
                }
            };

            this.websocket.send(JSON.stringify({ type: 'start' }));
            this.mediaRecorder.start(100);
            
            this.isRecording = true;
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.listeningEl.classList.remove('hidden');
            this.updateConversationLog("Recording started...", "system");

        } catch (err) {
            console.error('Error starting stream:', err);
            alert(`Error: ${err.message}\nCheck console for details.`);
            this.updateConversationLog(`Error: ${err.message}`, "system");
        }
    }

    stop() {
        if (!this.isRecording) return;

        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ type: 'stop' }));
        }
        
        // Stop all tracks (audio and video) to turn off camera light
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.videoElement.srcObject = null;
            this.stream = null;
        }

        if (this.source) {
            this.source.disconnect();
        }
        
        this.isRecording = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.listeningEl.classList.add('hidden');
    }

    drawWaveform() {
        if (!this.isRecording) return;

        requestAnimationFrame(() => this.drawWaveform());

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteTimeDomainData(dataArray);

        // Use CSS variables if possible, or fallback
        const style = getComputedStyle(document.body);
        const bgColor = style.getPropertyValue('--bg-secondary').trim() || '#1a1d24';
        const waveColor = style.getPropertyValue('--accent-primary').trim() || '#3b82f6';

        this.canvasCtx.fillStyle = bgColor;
        this.canvasCtx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.canvasCtx.lineWidth = 2;
        this.canvasCtx.strokeStyle = waveColor;
        this.canvasCtx.beginPath();

        const sliceWidth = this.canvas.width * 1.0 / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * this.canvas.height / 2;

            if (i === 0) {
                this.canvasCtx.moveTo(x, y);
            } else {
                this.canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        this.canvasCtx.lineTo(this.canvas.width, this.canvas.height / 2);
        this.canvasCtx.stroke();
    }

    playAudioResponse(blob) {
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play().catch(e => console.error("Error playing audio:", e));
    }

    testAudio() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.5);
        
        this.updateConversationLog("Playing test beep...", "system");
    }
}

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    const app = new AudioStreamer();
});
