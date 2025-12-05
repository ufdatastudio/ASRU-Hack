import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Path to the root folder containing 'audio-flamingo-3'
AUDIO_FLAMINGO_ROOT = "/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3"
AUDIO_FLAMINGO_MODEL_PATH = os.path.join(AUDIO_FLAMINGO_ROOT, "audio-flamingo-3")

# Add the model directory to sys.path to allow importing 'llava'
if AUDIO_FLAMINGO_ROOT not in sys.path:
    sys.path.append(AUDIO_FLAMINGO_ROOT)

# Afro-TTS Model (by Intron Innovation / intronhealth)
# Path to Afro-TTS model files
AFRO_TTS_BASE_DIR = os.getenv("AFRO_TTS_BASE_DIR", "/orange/ufdatastudios/c.okocha/afro-tts")
AFRO_TTS_CONFIG_PATH = os.getenv("AFRO_TTS_CONFIG_PATH", os.path.join(AFRO_TTS_BASE_DIR, "config.json"))
AFRO_TTS_CHECKPOINT_DIR = os.getenv("AFRO_TTS_CHECKPOINT_DIR", os.path.join(AFRO_TTS_BASE_DIR, "checkpoint_dir"))
# Speaker reference audio (6 seconds) - can be overridden per request
AFRO_TTS_SPEAKER_WAV = os.getenv("AFRO_TTS_SPEAKER_WAV", os.path.join(AFRO_TTS_BASE_DIR, "speaker", "6s_voice_sample.wav"))

# Legacy MMS-TTS config (kept for reference, not used)
# MMS_TTS_MODEL_ID = "facebook/mms-tts-yor"

# Audio storage directories
# Temporary directory for incoming chunks (fast write during streaming)
TEMP_AUDIO_DIR = "/tmp/speechreason_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Permanent storage directory for processed audio files
# Default to project directory, can be overridden via environment variable
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIO_STORAGE_DIR = os.getenv("AUDIO_STORAGE_DIR", os.path.join(_project_root, "data", "audio"))
os.makedirs(os.path.join(AUDIO_STORAGE_DIR, "sessions"), exist_ok=True)
os.makedirs(os.path.join(AUDIO_STORAGE_DIR, "responses"), exist_ok=True)
