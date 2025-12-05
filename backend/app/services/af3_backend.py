"""
AF3 Backend Service
Standalone FastAPI service for Audio Flamingo 3 inference.
Runs on port 8001.
"""
import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Add Audio Flamingo root to path
from backend.config import AUDIO_FLAMINGO_ROOT
if AUDIO_FLAMINGO_ROOT not in sys.path:
    sys.path.insert(0, AUDIO_FLAMINGO_ROOT)

from backend.app.services.af3_inference import load_af3, run_af3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AF3 Backend Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
af3_model = None
af3_processor = None


class AudioRequest(BaseModel):
    audio_path: str
    text_prompt: Optional[str] = None


class AudioResponse(BaseModel):
    text: str
    success: bool
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Load AF3 model on startup."""
    global af3_model, af3_processor
    
    logger.info("=" * 60)
    logger.info("Starting AF3 Backend Service")
    logger.info("=" * 60)
    
    try:
        logger.info("Loading Audio Flamingo 3...")
        af3_model, af3_processor = load_af3()
        logger.info("✓ AF3 loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load AF3: {e}", exc_info=True)
        logger.error("Service will start but inference will fail")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": af3_model is not None
    }


@app.post("/infer", response_model=AudioResponse)
async def infer_audio(request: AudioRequest):
    """
    Process audio through AF3 and return text response.
    
    Args:
        request: AudioRequest with audio_path and optional text_prompt
    
    Returns:
        AudioResponse with text result
    """
    if af3_model is None or af3_processor is None:
        raise HTTPException(
            status_code=503,
            detail="AF3 model not loaded. Check server logs."
        )
    
    if not os.path.exists(request.audio_path):
        raise HTTPException(
            status_code=404,
            detail=f"Audio file not found: {request.audio_path}"
        )
    
    try:
        logger.info(f"Processing audio: {request.audio_path}")
        text_response = run_af3(af3_model, af3_processor, request.audio_path)
        
        return AudioResponse(
            text=text_response,
            success=True,
            error=None
        )
    except Exception as e:
        logger.error(f"AF3 inference error: {e}", exc_info=True)
        return AudioResponse(
            text="",
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.services.af3_backend:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )

