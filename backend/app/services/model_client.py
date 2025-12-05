"""
Client for communicating with AF3 and TTS backend services.
"""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Backend service URLs (can be overridden via environment)
AF3_SERVICE_URL = "http://localhost:8001"
TTS_SERVICE_URL = "http://localhost:8002"


async def call_af3_service(audio_path: str, text_prompt: Optional[str] = None) -> Optional[str]:
    """
    Call AF3 backend service to process audio.
    
    Args:
        audio_path: Path to audio file
        text_prompt: Optional text prompt
    
    Returns:
        Text response from AF3, or None if error
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{AF3_SERVICE_URL}/infer",
                json={
                    "audio_path": audio_path,
                    "text_prompt": text_prompt
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("text")
            else:
                logger.error(f"AF3 service error: {result.get('error')}")
                return None
                
    except httpx.TimeoutException:
        logger.error("AF3 service timeout")
        return None
    except httpx.RequestError as e:
        logger.error(f"AF3 service connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"AF3 service error: {e}")
        return None


async def call_tts_service(text: str, speaker_wav: Optional[str] = None) -> Optional[bytes]:
    """
    Call TTS backend service to synthesize text.
    
    Args:
        text: Text to synthesize
        speaker_wav: Optional speaker reference audio path
    
    Returns:
        Audio bytes (WAV format), or None if error
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{TTS_SERVICE_URL}/synthesize",
                json={
                    "text": text,
                    "speaker_wav": speaker_wav
                }
            )
            response.raise_for_status()
            
            # Response is audio bytes
            return response.content
                
    except httpx.TimeoutException:
        logger.error("TTS service timeout")
        return None
    except httpx.RequestError as e:
        logger.error(f"TTS service connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"TTS service error: {e}")
        return None

