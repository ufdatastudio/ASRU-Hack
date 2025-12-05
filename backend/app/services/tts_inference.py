"""
Afro-TTS Inference Module (by Intron Innovation / intronhealth)
Loads Afro-TTS model for African-accented English synthesis.

Can use either:
1. Coqui TTS (from separate venv) - if TTS_ENV_PATH is set
2. TTS library from main environment - fallback
"""
import os
import sys
import torch
import logging
import numpy as np
import soundfile as sf
import io
import subprocess
from typing import Optional

# Import config for model paths
from backend.config import AFRO_TTS_CONFIG_PATH, AFRO_TTS_CHECKPOINT_DIR, AFRO_TTS_SPEAKER_WAV

logger = logging.getLogger(__name__)

# Global model instances
tts_model = None
tts_config = None
tts_env_path = os.getenv("TTS_ENV_PATH", "/orange/ufdatastudios/c.okocha/ASRU-Hack/tts-env/venv")


def _use_tts_env():
    """Check if we should use separate TTS environment."""
    return os.path.exists(tts_env_path) and os.path.exists(os.path.join(tts_env_path, "bin", "python"))


def _run_in_tts_env(script_content: str) -> Optional[bytes]:
    """Run Python code in the TTS virtual environment."""
    if not _use_tts_env():
        return None
    
    tts_python = os.path.join(tts_env_path, "bin", "python")
    
    try:
        result = subprocess.run(
            [tts_python, "-c", script_content],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"TTS subprocess error: {result.stderr}")
            return None
        
        # Parse output (assuming audio bytes are returned)
        # This is a simplified version - you may need to adjust based on actual output format
        return result.stdout.encode() if result.stdout else None
        
    except subprocess.TimeoutExpired:
        logger.error("TTS subprocess timed out")
        return None
    except Exception as e:
        logger.error(f"Error running TTS in separate env: {e}")
        return None


def load_tts():
    """
    Load Afro-TTS model from local path.
    Tries to use separate TTS environment if available, otherwise uses main environment.
    
    Returns:
        tuple: (model, config) - config is used as "processor" for compatibility
    """
    global tts_model, tts_config
    
    if tts_model is not None and tts_config is not None:
        logger.info("TTS model already loaded, returning existing instance")
        return (tts_model, tts_config)
    
    # Try using separate TTS environment first
    if _use_tts_env():
        logger.info(f"Using separate TTS environment: {tts_env_path}")
        logger.warning("Separate TTS environment detected, but subprocess loading not fully implemented.")
        logger.warning("Falling back to main environment. For now, install TTS in main environment.")
        # TODO: Implement subprocess-based loading if needed
    
    # Load from main environment
    try:
        logger.info("Loading Afro-TTS model from main environment...")
        
        # Import TTS library
        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.tts.models.xtts import Xtts
        except ImportError as e:
            logger.error("TTS library not found. Install with: uv pip install TTS")
            logger.info(f"Or set up separate TTS env: bash scripts/setup_tts_env.sh")
            raise ImportError("TTS library is required. Install with: uv pip install TTS")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Afro-TTS model on {device}")
        logger.info(f"Config path: {AFRO_TTS_CONFIG_PATH}")
        logger.info(f"Checkpoint dir: {AFRO_TTS_CHECKPOINT_DIR}")
        
        # Check if paths exist
        if not os.path.exists(AFRO_TTS_CONFIG_PATH):
            raise FileNotFoundError(f"Afro-TTS config not found at: {AFRO_TTS_CONFIG_PATH}")
        
        if not os.path.exists(AFRO_TTS_CHECKPOINT_DIR):
            raise FileNotFoundError(f"Afro-TTS checkpoint directory not found at: {AFRO_TTS_CHECKPOINT_DIR}")
        
        # Load config
        logger.info("Loading Afro-TTS config...")
        tts_config = XttsConfig()
        tts_config.load_json(AFRO_TTS_CONFIG_PATH)
        
        # Initialize model from config
        logger.info("Initializing Afro-TTS model from config...")
        tts_model = Xtts.init_from_config(tts_config)
        
        # Load checkpoint
        logger.info(f"Loading checkpoint from {AFRO_TTS_CHECKPOINT_DIR}...")
        tts_model.load_checkpoint(AFRO_TTS_CHECKPOINT_DIR, eval=True)
        
        # Move model to device
        if device == "cuda":
            tts_model.cuda()
        else:
            tts_model.cpu()
        
        logger.info("✓ Afro-TTS model loaded successfully!")
        return (tts_model, tts_config)
        
    except Exception as e:
        logger.error(f"Failed to load Afro-TTS model: {e}", exc_info=True)
        raise


def run_tts(model, config, text: str, speaker_wav: Optional[str] = None) -> Optional[bytes]:
    """
    Run Afro-TTS synthesis on text input.
    
    Args:
        model: Xtts model instance
        config: XttsConfig instance
        text: Text to synthesize
        speaker_wav: Path to speaker reference audio file (6 seconds). 
                     If None, uses default from config.
    
    Returns:
        bytes: WAV audio bytes, or None if error
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to TTS")
        return None
    
    try:
        logger.info(f"Synthesizing speech for text: {text[:100]}...")  # Log first 100 chars
        
        # Use default speaker_wav if not provided
        if speaker_wav is None:
            speaker_wav = AFRO_TTS_SPEAKER_WAV
        
        if not speaker_wav or not os.path.exists(speaker_wav):
            logger.warning(f"Speaker reference audio not found at {speaker_wav}, trying to continue without it")
            # Try with empty string - model might have a default
            speaker_wav = None
        
        # Generate speech
        logger.info(f"Using speaker reference: {speaker_wav or 'default'}")
        
        with torch.no_grad():
            if speaker_wav and os.path.exists(speaker_wav):
                outputs = model.synthesize(
                    text,
                    config,
                    speaker_wav=speaker_wav,
                    language="en"
                )
            else:
                # Try without speaker_wav if file doesn't exist
                logger.warning("Running synthesis without speaker reference audio")
                outputs = model.synthesize(
                    text,
                    config,
                    language="en"
                )
        
        # Extract waveform from outputs
        # Afro-TTS outputs format may vary - check structure
        if isinstance(outputs, dict):
            waveform = outputs.get('wav', outputs.get('audio', None))
            sample_rate = outputs.get('sample_rate', config.sample_rate if hasattr(config, 'sample_rate') else 22050)
        elif isinstance(outputs, (np.ndarray, torch.Tensor)):
            waveform = outputs
            sample_rate = getattr(config, 'sample_rate', 22050)
        else:
            # Try to extract from tuple if that's the format
            if isinstance(outputs, tuple):
                waveform = outputs[0]
                sample_rate = outputs[1] if len(outputs) > 1 else getattr(config, 'sample_rate', 22050)
            else:
                raise ValueError(f"Unexpected output format from Afro-TTS: {type(outputs)}")
        
        # Convert to numpy if tensor
        if isinstance(waveform, torch.Tensor):
            waveform = waveform.cpu().numpy()
        
        # Handle different output shapes
        if len(waveform.shape) > 1:
            waveform = waveform.squeeze()
        
        # Ensure 1D array
        if len(waveform.shape) > 1:
            waveform = waveform.flatten()
        
        logger.info(f"Generated audio waveform - shape: {waveform.shape}, sample_rate: {sample_rate}")
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, waveform, sample_rate, format='WAV')
        buffer.seek(0)
        audio_bytes = buffer.read()
        
        logger.info(f"Generated {len(audio_bytes)} bytes of audio")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"Error running Afro-TTS synthesis: {e}", exc_info=True)
        return None
