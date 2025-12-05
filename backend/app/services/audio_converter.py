import os
import subprocess
import logging
from pathlib import Path

# Try to use static_ffmpeg if available (adds ffmpeg to PATH)
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

logger = logging.getLogger(__name__)

def convert_webm_to_wav(webm_path: str, wav_path: str = None) -> str:
    """
    Convert WebM audio file to WAV format using ffmpeg.
    Fast conversion - typically takes <1 second for short audio files.
    
    Args:
        webm_path: Path to input WebM file
        wav_path: Optional output WAV path. If None, replaces .webm with .wav
    
    Returns:
        Path to the converted WAV file
    """
    if not os.path.exists(webm_path):
        raise FileNotFoundError(f"WebM file not found: {webm_path}")
    
    if wav_path is None:
        wav_path = str(Path(webm_path).with_suffix('.wav'))
    
    try:
        # Use ffmpeg to convert WebM to WAV
        # -y: overwrite output file if exists
        # -i: input file
        # -ar 16000: set sample rate to 16kHz (common for speech)
        # -ac 1: mono channel
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', webm_path,  # Input
            '-ar', '16000',  # Sample rate 16kHz
            '-ac', '1',  # Mono
            '-f', 'wav',  # Format WAV
            wav_path  # Output
        ]
        
        logger.info(f"Converting {webm_path} to {wav_path}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # 30 second timeout
        )
        
        if os.path.exists(wav_path):
            file_size = os.path.getsize(wav_path)
            logger.info(f"Converted to WAV: {wav_path} ({file_size} bytes)")
            return wav_path
        else:
            raise RuntimeError("WAV file was not created")
            
    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg conversion timed out for {webm_path}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Error converting WebM to WAV: {e}")
        raise

