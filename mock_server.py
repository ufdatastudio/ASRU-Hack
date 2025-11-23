import asyncio
import json
import logging
import wave
import uuid
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="African health studio - Mock Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mock Backend Running"}

@app.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("Frontend connected")
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                # Just log the size to confirm we got audio
                chunk_size = len(message["bytes"])
                # logger.info(f"Received audio chunk: {chunk_size} bytes")
                pass
                
            elif "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")
                logger.info(f"Received control: {msg_type}")
                
                if msg_type == "stop":
                    # Simulate processing delay
                    await websocket.send_text(json.dumps({"type": "text_update", "text": "Processing (Mock)..."}))
                    await asyncio.sleep(1)
                    
                    # Send mock text response
                    response_text = "This is a mock response from the backend. I heard you!"
                    await websocket.send_text(json.dumps({"type": "text_update", "text": response_text}))
                    
                    # Send a simple beep as "audio response" (Mocking TTS)
                    # Generating a 1-second sine wave
                    import io
                    import math
                    import struct
                    
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(44100)
                        
                        # Generate 1 second of 440Hz tone
                        for i in range(44100):
                            value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / 44100.0))
                            data = struct.pack('<h', value)
                            wav_file.writeframesraw(data)
                            
                    buffer.seek(0)
                    await websocket.send_bytes(buffer.read())
                    logger.info("Sent mock audio response")

    except WebSocketDisconnect:
        logger.info("Frontend disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

