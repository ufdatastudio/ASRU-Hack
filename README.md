# African health studio

A real-time conversational audio system using **Audio Flamingo 3** for reasoning and **Meta MMS-TTS (Yoruba)** for speech synthesis.

## Prerequisites

- NVIDIA GPU (B200 or similar high-end GPU recommended)
- Python 3.12
- `uv` package manager

## Setup

1.  **Install dependencies:**
    The project uses `uv` for dependency management.
    ```bash
    uv sync
    ```

2.  **Environment Configuration:**
    The `backend/config.py` is pre-configured with the paths to Audio Flamingo 3:
    - Root: `/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3`
    - Model: `/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3/audio-flamingo-3`
    
    Ensure you have access to these directories.

3.  **Running the System:**

    Start the backend server:
    ```bash
    uv run python -m backend.app.server
    ```

    The server will start on `http://0.0.0.0:8000`.

4.  **Frontend:**
    Open `frontend/index.html` in a modern web browser.
    - Click "Start Conversation" to begin recording.
    - Speak into the microphone.
    - Click "Stop" to send the audio for processing.
    - The system will display the text response and play back the spoken Yoruba-accented response.

## Architecture

- **Frontend:** HTML/JS with MediaRecorder and WebSockets. Streams audio chunks to backend.
- **Backend:** FastAPI WebSocket server.
  - `AudioFlamingoService`: Loads Audio Flamingo 3 from the local path and runs inference.
  - `MMSTTSService`: Uses `facebook/mms-tts-yor` (VITS) to synthesize speech.
  - Pipeline: Audio Input -> Save to Disk -> Flamingo Inference -> Text -> MMS-TTS -> Audio Output.

## Notes
- The system uses a simple "Push-to-Talk" style interaction for reliability (Start/Stop buttons).
- Audio is saved temporarily in `/tmp/speechreason_audio`.
