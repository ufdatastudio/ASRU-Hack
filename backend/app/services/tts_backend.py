"""
Afro-TTS Backend Service
Standalone FastAPI service for Afro-TTS inference.
Runs on port 8002.
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from backend.app.services.tts_inference import load_tts, run_tts
from backend.config import AFRO_TTS_SPEAKER_WAV

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Afro-TTS Backend Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
tts_model = None
tts_config = None


class TextRequest(BaseModel):
    text: str
    speaker_wav: Optional[str] = None


class AudioResponse(BaseModel):
    audio_bytes: bytes
    success: bool
    error: Optional[str] = None
    sample_rate: Optional[int] = None


@app.on_event("startup")
async def startup_event():
    """Load Afro-TTS model on startup."""
    global tts_model, tts_config
    
    logger.info("=" * 60)
    logger.info("Starting Afro-TTS Backend Service")
    logger.info("=" * 60)
    
    try:
        logger.info("Loading Afro-TTS...")
        tts_model, tts_config = load_tts()
        logger.info("✓ Afro-TTS loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Afro-TTS: {e}", exc_info=True)
        logger.error("Service will start but inference will fail")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": tts_model is not None
    }


@app.post("/synthesize")
async def synthesize_text(request: TextRequest):
    """
    Synthesize text to speech using Afro-TTS.
    
    Args:
        request: TextRequest with text and optional speaker_wav
    
    Returns:
        Audio bytes (WAV format)
    """
    if tts_model is None or tts_config is None:
        raise HTTPException(
            status_code=503,
            detail="TTS model not loaded. Check server logs."
        )
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    try:
        # Use provided speaker_wav or default
        speaker_wav = request.speaker_wav or AFRO_TTS_SPEAKER_WAV
        
        logger.info(f"Synthesizing text: {request.text[:100]}...")
        audio_bytes = run_tts(tts_model, tts_config, request.text, speaker_wav)
        
        if audio_bytes is None:
            raise HTTPException(
                status_code=500,
                detail="TTS synthesis returned no audio"
            )
        
        # Return audio as binary response
        from fastapi.responses import Response
        return Response(
            content=audio_bytes,
            media_type="audio/wav"
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"TTS synthesis failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.services.tts_backend:app",
        host="0.0.0.0",
        port=8002,
        reload=False
    )

