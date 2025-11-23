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

# MMS-TTS Yoruba Model
MMS_TTS_MODEL_ID = "facebook/mms-tts-yor"

# Temporary directory for audio chunks
TEMP_AUDIO_DIR = "/tmp/speechreason_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
