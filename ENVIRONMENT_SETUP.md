# Environment Setup with UV

This project uses **UV dependency groups** to organize dependencies for AF3 and TTS separately, while still using one virtual environment.

## Recommended: Dependency Groups (One Environment)

### Install Everything

```bash
uv sync --all-extras
```

### Install Specific Groups

```bash
# Only AF3 dependencies
uv sync --extra af3

# Only TTS dependencies  
uv sync --extra tts

# Both groups
uv sync --extra af3 --extra tts
```

## Dependency Groups

### Core Dependencies (Always Installed)
- FastAPI, Uvicorn, WebSockets
- Audio processing (pydub, soundfile, static-ffmpeg)
- Basic ML (torch, numpy)

### AF3 Group (`--extra af3`)
- Audio Flamingo 3 dependencies
- Transformers, accelerate, deepspeed
- All AF3-specific packages

### TTS Group (`--extra tts`)
- TTS library for Afro-TTS

## Alternative: Separate Virtual Environments

If you truly need separate environments, you can create them:

### Create AF3 Environment

```bash
# Create separate venv for AF3
uv venv .venv-af3

# Activate and install AF3 dependencies
source .venv-af3/bin/activate  # Linux/Mac
# or
.venv-af3\Scripts\activate     # Windows

uv pip install -e ".[af3]"
```

### Create TTS Environment

```bash
# Create separate venv for TTS
uv venv .venv-tts

# Activate and install TTS dependencies
source .venv-tts/bin/activate  # Linux/Mac
# or
.venv-tts\Scripts\activate     # Windows

uv pip install -e ".[tts]"
```

### Using Separate Environments

**Note:** Since both models run in the same server process, you'd need to:
1. Run AF3 in a subprocess with `.venv-af3`
2. Run TTS in a subprocess with `.venv-tts`
3. This requires significant code changes

**Not recommended** - dependency groups are simpler and work better for this use case.

## Why Dependency Groups?

- ✅ One environment (simpler)
- ✅ Organized dependencies
- ✅ Can install only what you need
- ✅ Both models work in same process
- ✅ No subprocess overhead

## Running the Server

The server works with whatever dependencies are installed:

```bash
# If only AF3 is installed, TTS will fail to load (gracefully)
# If only TTS is installed, AF3 will fail to load (gracefully)  
# If both are installed, everything works
uv run python -m backend.app.server
```

## Checking Installed Groups

```bash
# See what's installed
uv pip list

# Check if specific package is installed
uv pip show TTS
uv pip show transformers
```
