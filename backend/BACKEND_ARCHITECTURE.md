# Backend Architecture

## Overview

The backend implements the voice conversation pipeline:
```
Web App Mic Audio → AF3 (audio→text reasoning) → Afro-TTS (text→voice)
```

## Structure

```
backend/
├── app/
│   ├── server.py              # Main FastAPI server with WebSocket endpoint
│   └── services/
│       ├── af3_inference.py   # Audio Flamingo 3 inference module
│       ├── tts_inference.py   # Afro-TTS inference module
│       └── audio_converter.py # WebM to WAV conversion utility
├── config.py                  # Configuration (paths, directories)
└── BACKEND_ARCHITECTURE.md    # This file
```

## Pipeline Flow

### 1. WebSocket Connection (`/ws/audio`)

Frontend connects via WebSocket and sends:
- **Audio chunks** (bytes): WebM format audio chunks
- **Text messages**:
  - `{"type": "start"}` - Begin recording
  - `{"type": "stop"}` - Stop recording and process

### 2. Audio Reception

Server accumulates audio chunks in a temporary WebM file:
- Location: `/tmp/speechreason_audio/{session_id}_input.webm`
- Chunks appended as they arrive

### 3. Processing (on "stop" message)

#### Step 1: Convert WebM → WAV
- Convert WebM audio to WAV format using ffmpeg
- Save to permanent storage: `data/audio/sessions/YYYY/MM/DD/{session_id}_input.wav`

#### Step 2: AF3 Inference (Audio → Text)
- Uses Audio Flamingo 3 model (local path)
- Process WAV audio through AF3
- Generate text response from audio reasoning
- Send text response to frontend

#### Step 3: Afro-TTS Synthesis (Text → Voice)
- Uses Afro-TTS model (local path)
- Synthesize text response to African-accented English audio
- Generate WAV audio bytes
- Save response: `data/audio/sessions/YYYY/MM/DD/{session_id}_response.wav`
- Send audio bytes back to frontend

## Model Loading

Models are loaded **on server startup** for performance:

```python
@app.on_event("startup")
async def startup_event():
    # Load AF3
    af3_model, af3_processor = load_af3()
    
    # Load Afro-TTS
    tts_model, tts_config = load_tts()
```

### Audio Flamingo 3 (AF3)

**Local Model Path:**
- Uses local model at: `/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3/audio-flamingo-3`
- Configured in: `backend/config.py` → `AUDIO_FLAMINGO_MODEL_PATH`
- Uses `llava` module from local repository

**Fallback:**
- If local path not found, falls back to HuggingFace: `nvidia/audio-flamingo-3-chat`
- Requires: `audio-flamingo` package

**Module:** `backend/app/services/af3_inference.py`

### Afro-TTS

**Local Model Path:**
- Config: `AFRO_TTS_CONFIG_PATH` → path to `config.json`
- Checkpoint: `AFRO_TTS_CHECKPOINT_DIR` → path to checkpoint directory
- Speaker: `AFRO_TTS_SPEAKER_WAV` → path to 6-second speaker reference audio
- Configured in: `backend/config.py`

**Directory Structure:**
```
afro-tts/
├── config.json              # Model configuration
├── checkpoint_dir/          # Model checkpoints
└── speaker/
    └── 6s_voice_sample.wav  # Reference speaker audio
```

**Module:** `backend/app/services/tts_inference.py`

**Installation:**
```bash
uv pip install TTS
```

## Configuration

All paths configured in `backend/config.py`:

```python
# Audio Flamingo 3
AUDIO_FLAMINGO_ROOT = "/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3"
AUDIO_FLAMINGO_MODEL_PATH = os.path.join(AUDIO_FLAMINGO_ROOT, "audio-flamingo-3")

# Afro-TTS
AFRO_TTS_BASE_DIR = "/orange/ufdatastudios/c.okocha/afro-tts"
AFRO_TTS_CONFIG_PATH = os.path.join(AFRO_TTS_BASE_DIR, "config.json")
AFRO_TTS_CHECKPOINT_DIR = os.path.join(AFRO_TTS_BASE_DIR, "checkpoint_dir")
AFRO_TTS_SPEAKER_WAV = os.path.join(AFRO_TTS_BASE_DIR, "speaker", "6s_voice_sample.wav")

# Storage
TEMP_AUDIO_DIR = "/tmp/speechreason_audio"
AUDIO_STORAGE_DIR = "data/audio"
```

Paths can be overridden via environment variables.

## API Endpoints

### WebSocket: `/ws/audio`
Main conversation endpoint (see Pipeline Flow above)

### GET: `/api/audio/sessions`
List all saved audio session files for debugging/testing

### GET: `/`
Serves legacy frontend HTML (for development)

## Storage

### Temporary Storage
- **Location**: `/tmp/speechreason_audio/`
- **Format**: WebM chunks
- **Cleanup**: Removed after processing

### Permanent Storage
- **Location**: `data/audio/sessions/YYYY/MM/DD/`
- **Files**:
  - `{session_id}_input.wav` - User's recorded audio
  - `{session_id}_response.wav` - AI's voice response
- **Purpose**: Debugging, logging, potential future use

## Error Handling

- Models loaded on startup with error logging
- If models fail to load, server continues but inference will fail gracefully
- Each session has unique error handling
- Errors are sent back to frontend as text messages

## Dependencies

Key dependencies (from `pyproject.toml`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
- `transformers` - HuggingFace models (for fallback)
- `torch` - PyTorch for models
- `soundfile` - Audio file handling
- `static-ffmpeg` - Audio conversion
- `TTS` - Text-to-speech library for Afro-TTS

## Frontend Compatibility

The backend maintains **full compatibility** with the existing frontend:
- **WebSocket URL**: `ws://localhost:8000/ws/audio`
- **Message Protocol**: Same format
- **Response Format**: Same format

No frontend changes required!
