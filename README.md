# African Health Studio

Mental health support platform for Africa - accessible, compassionate, and culturally aware.

A real-time conversational audio system using **Audio Flamingo 3** for audio reasoning and **Afro-TTS** for speech synthesis.

## Quick Start

### Prerequisites

- NVIDIA GPU (B200 or similar recommended)
- Python 3.12
- `uv` package manager
- Audio Flamingo 3 model (local path configured)
- Afro-TTS model (local path configured)

### Installation

**Install all dependencies (AF3 + TTS):**
```bash
uv sync --all-extras
```

**Or install specific groups:**
```bash
# Only AF3 dependencies
uv sync --extra af3

# Only TTS dependencies  
uv sync --extra tts

# Both
uv sync --extra af3 --extra tts
```

See `ENVIRONMENT_SETUP.md` for detailed dependency group information.

3. **Configure model paths:**
   Edit `backend/config.py` to set paths:
   - Audio Flamingo 3: `AUDIO_FLAMINGO_MODEL_PATH`
   - Afro-TTS: `AFRO_TTS_CONFIG_PATH`, `AFRO_TTS_CHECKPOINT_DIR`, `AFRO_TTS_SPEAKER_WAV`

### Running Locally

Start the backend server:
```bash
bash run_server.sh
```

Start the Next.js frontend:
```bash
cd frontend-next
npm run dev
```

### Running on HiPerGator

See `HIPERGATOR_SETUP.md` for detailed instructions on running with GPU.

**Quick commands:**
- Interactive: `bash run_server_interactive.sh`
- Production: `sbatch run_server.slurm`

## Architecture

**Pipeline:** Web App Mic Audio → AF3 (audio→text reasoning) → Afro-TTS (text→voice)

- **Frontend:** Next.js with MediaRecorder and WebSockets
- **Backend:** FastAPI with WebSocket support
  - Audio Flamingo 3: Local model loading for audio reasoning
  - Afro-TTS: Text-to-speech with African accent
  - Audio storage: Organized by date in `data/audio/sessions/`

For detailed backend architecture, see `backend/BACKEND_ARCHITECTURE.md`.

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── server.py              # FastAPI server
│   │   └── services/
│   │       ├── af3_inference.py   # Audio Flamingo 3
│   │       ├── tts_inference.py   # Afro-TTS
│   │       └── audio_converter.py # WebM to WAV
│   └── config.py                  # Configuration
├── frontend-next/                 # Next.js frontend
├── scripts/                       # Utility scripts
└── run_server.slurm              # SLURM batch script
```

## Configuration

Model paths are configured in `backend/config.py`:

- `AUDIO_FLAMINGO_MODEL_PATH`: Path to Audio Flamingo 3 model
- `AFRO_TTS_CONFIG_PATH`: Path to Afro-TTS config.json
- `AFRO_TTS_CHECKPOINT_DIR`: Path to Afro-TTS checkpoint directory
- `AFRO_TTS_SPEAKER_WAV`: Path to speaker reference audio (6 seconds)

## Development

The system uses:
- **UV** for Python package management
- **Next.js** for the frontend
- **FastAPI** for the backend API
- **WebSockets** for real-time audio streaming

See `backend/BACKEND_ARCHITECTURE.md` for detailed technical documentation.
