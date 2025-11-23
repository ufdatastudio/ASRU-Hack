import os
import asyncio
import json
import logging
import wave
import time
import uuid
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import TEMP_AUDIO_DIR
from backend.app.services.flamingo_service import AudioFlamingoService
from backend.app.services.tts_service import MMSTTSService

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="African health studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (Lazy load can be better for dev restart speed, but let's load on startup for readiness)
# Global instances
flamingo_service = None
tts_service = None

@app.on_event("startup")
async def startup_event():
    global flamingo_service, tts_service
    try:
        logger.info("Initializing Audio Flamingo Service...")
        # flamingo_service = AudioFlamingoService(think_mode=False) # Set think_mode=True if needed/supported
        # Mocking service for now if it fails or is slow, but user likely has it setup.
        # For safety, let's assume it might fail if weights aren't there, but we'll try.
        if not flamingo_service:
             flamingo_service = AudioFlamingoService(think_mode=False)
        
        logger.info("Initializing TTS Service...")
        if not tts_service:
            tts_service = MMSTTSService()
        logger.info("Services initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")

# Mount frontend static files
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, websocket: WebSocket, text: str):
        await websocket.send_text(json.dumps({"type": "text_update", "text": text}))

    async def send_audio(self, websocket: WebSocket, audio_data: bytes):
        await websocket.send_bytes(audio_data)

manager = ConnectionManager()

@app.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("WebSocket connection established")
    
    session_id = str(uuid.uuid4())
    audio_buffer = bytearray()
    is_listening = False
    
    # Wav parameters (assuming 48kHz from browser MediaRecorder, but often it's 48000 or 44100)
    # We will need to check the header or assume standard WebRTC Opus/WebM -> decoded by server? 
    # Or raw PCM? 
    # For simplicity, let's assume the frontend sends WEBM blobs. 
    # We might need to transcode them.
    # Actually, sending WAV header or raw PCM is easier if we control frontend. 
    # But MediaRecorder sends WebM usually.
    # Strategy: Save the chunks to a file, then use ffmpeg or sf to read.
    
    current_file_path = os.path.join(TEMP_AUDIO_DIR, f"{session_id}_input.webm")
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                # Append audio chunk
                chunk = message["bytes"]
                with open(current_file_path, "ab") as f:
                    f.write(chunk)
                
            elif "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")
                
                if msg_type == "start":
                    # Start new recording session
                    is_listening = True
                    # Clear existing file if any
                    if os.path.exists(current_file_path):
                        os.remove(current_file_path)
                    logger.info("Started recording")
                    
                elif msg_type == "stop":
                    # Stop recording and process
                    is_listening = False
                    logger.info("Stopped recording, processing...")
                    await manager.send_text(websocket, "Processing audio...")
                    
                    # 1. Inference
                    if os.path.exists(current_file_path) and os.path.getsize(current_file_path) > 0:
                        try:
                            # Audio Flamingo Inference
                            response_text = flamingo_service.process_audio(current_file_path)
                            logger.info(f"Model Response: {response_text}")
                            
                            await manager.send_text(websocket, response_text)
                            
                            # 2. TTS
                            if response_text:
                                logger.info("Synthesizing speech...")
                                audio_bytes = tts_service.synthesize(response_text)
                                if audio_bytes:
                                    await manager.send_audio(websocket, audio_bytes)
                                else:
                                    logger.error("TTS returned no audio")
                        except Exception as e:
                            logger.error(f"Processing error: {e}")
                            await manager.send_text(websocket, f"Error: {str(e)}")
                    else:
                        await manager.send_text(websocket, "No audio received.")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.server:app", host="0.0.0.0", port=8000, reload=False)
