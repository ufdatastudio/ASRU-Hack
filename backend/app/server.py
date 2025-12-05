"""
African Health Studio Backend Server
Main FastAPI server with WebSocket support for voice conversations.

Pipeline: Web App Mic Audio → AF3 (audio→text) → Afro-TTS (text→voice)
"""
import os
import json
import logging
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

# Import services
from backend.app.services.audio_converter import convert_webm_to_wav
from backend.app.services.model_client import call_af3_service, call_tts_service
from backend.config import TEMP_AUDIO_DIR, AUDIO_STORAGE_DIR
import httpx

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="African health studio - Mental Health Support")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend service URLs (can be overridden via environment)
AF3_SERVICE_URL = os.getenv("AF3_SERVICE_URL", "http://localhost:8001")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://localhost:8002")


@app.on_event("startup")
async def startup_event():
    """Check backend services on startup."""
    logger.info("=" * 60)
    logger.info("Starting African Health Studio Main API")
    logger.info("=" * 60)
    logger.info(f"AF3 Service: {AF3_SERVICE_URL}")
    logger.info(f"TTS Service: {TTS_SERVICE_URL}")
    logger.info("")
    
    # Check if backend services are available
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check AF3 service
            try:
                response = await client.get(f"{AF3_SERVICE_URL}/health")
                if response.status_code == 200:
                    logger.info("✓ AF3 service is available")
                else:
                    logger.warning(f"AF3 service returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"AF3 service not available: {e}")
            
            # Check TTS service
            try:
                response = await client.get(f"{TTS_SERVICE_URL}/health")
                if response.status_code == 200:
                    logger.info("✓ TTS service is available")
                else:
                    logger.warning(f"TTS service returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"TTS service not available: {e}")
    except Exception as e:
        logger.warning(f"Could not check backend services: {e}")
    
    logger.info("=" * 60)
    logger.info("Main API ready. Backend services will be called on demand.")
    logger.info("=" * 60)


# Mount frontend static files (legacy frontend)
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


@app.get("/api/audio/sessions")
async def list_audio_sessions():
    """List all saved audio session files for testing/debugging."""
    sessions_dir = os.path.join(AUDIO_STORAGE_DIR, "sessions")
    sessions = []
    
    if os.path.exists(sessions_dir):
        for root, dirs, files in os.walk(sessions_dir):
            for file in files:
                if file.endswith('.wav'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, AUDIO_STORAGE_DIR)
                    file_size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    
                    sessions.append({
                        'filename': file,
                        'path': rel_path,
                        'full_path': file_path,
                        'size_bytes': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(mtime).isoformat(),
                        'type': 'input' if '_input.wav' in file else 'response'
                    })
    
    # Sort by modified time, newest first
    sessions.sort(key=lambda x: x['modified'], reverse=True)
    
    return {
        'count': len(sessions),
        'storage_dir': AUDIO_STORAGE_DIR,
        'sessions': sessions
    }


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_text(self, websocket: WebSocket, text: str):
        """Send text message to client."""
        await websocket.send_text(json.dumps({"type": "text_update", "text": text}))

    async def send_audio(self, websocket: WebSocket, audio_data: bytes):
        """Send audio bytes to client."""
        await websocket.send_bytes(audio_data)


manager = ConnectionManager()


@app.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for voice conversations.
    
    Pipeline:
    1. Receive audio chunks (WebM format) from frontend
    2. On "stop" message: Convert WebM → WAV
    3. Process with AF3: Audio → Text (reasoning)
    4. Synthesize with MMS-TTS: Text → Voice (African-accented)
    5. Send response audio back to frontend
    """
    await manager.connect(websocket)
    logger.info("WebSocket connection established")
    
    session_id = str(uuid.uuid4())
    is_listening = False
    current_file_path = os.path.join(TEMP_AUDIO_DIR, f"{session_id}_input.webm")
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                # Receive audio chunk from frontend
                if is_listening:
                    chunk = message["bytes"]
                    # Append chunk to temporary WebM file
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
                    logger.info(f"[{session_id[:8]}] Started recording")
                    
                elif msg_type == "stop":
                    # Stop recording and process through pipeline
                    is_listening = False
                    logger.info(f"[{session_id[:8]}] Stopped recording, processing...")
                    await manager.send_text(websocket, "Processing audio...")
                    
                    # Check if we have audio to process
                    if not os.path.exists(current_file_path) or os.path.getsize(current_file_path) == 0:
                        await manager.send_text(websocket, "No audio received.")
                        continue
                    
                    try:
                        # Create storage directory for this session
                        now = datetime.now()
                        date_dir = os.path.join(
                            AUDIO_STORAGE_DIR, "sessions",
                            str(now.year), f"{now.month:02d}", f"{now.day:02d}"
                        )
                        os.makedirs(date_dir, exist_ok=True)
                        
                        # Step 1: Convert WebM to WAV and save
                        wav_filename = f"{session_id}_input.wav"
                        wav_path = os.path.join(date_dir, wav_filename)
                        
                        logger.info(f"[{session_id[:8]}] Converting WebM to WAV: {wav_path}")
                        convert_webm_to_wav(current_file_path, wav_path)
                        
                        file_size = os.path.getsize(wav_path)
                        logger.info(f"[{session_id[:8]}] Audio saved: {wav_path} ({file_size} bytes)")
                        
                        # Step 2: Call AF3 Service - Audio → Text
                        logger.info(f"[{session_id[:8]}] Calling AF3 service...")
                        response_text = await call_af3_service(wav_path)
                        
                        if not response_text:
                            error_msg = "AF3 service returned no response. Check AF3 service logs."
                            logger.error(f"[{session_id[:8]}] {error_msg}")
                            await manager.send_text(websocket, f"Error: {error_msg}")
                            continue
                        
                        logger.info(f"[{session_id[:8]}] AF3 Response: {response_text[:200]}...")
                        
                        # Send text response to frontend
                        await manager.send_text(websocket, response_text)
                        
                        # Step 3: Call TTS Service - Text → Voice
                        if not response_text or not response_text.strip():
                            logger.warning(f"[{session_id[:8]}] Empty response text, skipping TTS")
                            continue
                        
                        logger.info(f"[{session_id[:8]}] Calling TTS service...")
                        audio_bytes = await call_tts_service(response_text)
                        
                        if audio_bytes:
                            # Save TTS response audio
                            response_wav_path = os.path.join(date_dir, f"{session_id}_response.wav")
                            with open(response_wav_path, 'wb') as f:
                                f.write(audio_bytes)
                            logger.info(f"[{session_id[:8]}] Response audio saved: {response_wav_path}")
                            
                            # Send audio response to frontend
                            await manager.send_audio(websocket, audio_bytes)
                            logger.info(f"[{session_id[:8]}] Pipeline complete! Sent {len(audio_bytes)} bytes of audio")
                        else:
                            logger.error(f"[{session_id[:8]}] TTS returned no audio")
                            await manager.send_text(websocket, "Error: Failed to generate audio response.")
                        
                    except Exception as e:
                        logger.error(f"[{session_id[:8]}] Processing error: {e}", exc_info=True)
                        await manager.send_text(websocket, f"Error: {str(e)}")
                
                elif msg_type == "model":
                    # Optional: Model selection (for future use)
                    selected_model = data.get("model", "audio-flamingo-3")
                    logger.info(f"[{session_id[:8]}] Model selected: {selected_model}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"[{session_id[:8]}] WebSocket disconnected")
    except Exception as e:
        logger.error(f"[{session_id[:8]}] WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)
    finally:
        # Cleanup temporary file
        if os.path.exists(current_file_path):
            try:
                os.remove(current_file_path)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.server:app", host="0.0.0.0", port=8000, reload=False)
