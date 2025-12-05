# Coqui TTS Separate Virtual Environment Setup

This guide sets up a separate virtual environment specifically for Coqui TTS, as per the official installation instructions.

## Quick Setup

```bash
bash scripts/setup_tts_env.sh
```

This will:
1. Create `tts-env/` directory
2. Clone Coqui TTS repository
3. Create a Python virtual environment
4. Install TTS in editable mode

## Manual Setup (Linux)

### 1. Create TTS Environment Directory

```bash
cd /orange/ufdatastudios/c.okocha/ASRU-Hack
mkdir -p tts-env
cd tts-env
```

### 2. Clone Coqui TTS

```bash
git clone https://github.com/coqui-ai/TTS.git
cd TTS
```

### 3. Create Virtual Environment

```bash
python3 -m venv ../venv
```

### 4. Activate and Install

```bash
source ../venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## Using the TTS Environment

### Activate Manually

```bash
source /orange/ufdatastudios/c.okocha/ASRU-Hack/tts-env/venv/bin/activate
```

### Use Helper Script

```bash
bash scripts/use_tts_env.sh python your_script.py
```

## Integration with Backend

The backend will automatically detect the TTS environment if it exists at:
```
/orange/ufdatastudios/c.okocha/ASRU-Hack/tts-env/venv
```

You can override the path with:
```bash
export TTS_ENV_PATH="/path/to/your/tts-env/venv"
```

## Python Version

**Important:** Coqui TTS requires Python 3.8 (not 3.9+). 

If your system Python is 3.9+, you may need to:
1. Install Python 3.8 separately
2. Use it to create the venv: `python3.8 -m venv ../venv`

## Directory Structure

After setup:
```
tts-env/
├── venv/              # Virtual environment
│   ├── bin/
│   └── ...
└── TTS/               # Coqui TTS repository
    ├── TTS/
    ├── setup.py
    └── ...
```

## Notes

- The TTS environment is separate from your main project environment
- The backend can use either the main environment's TTS or the separate TTS environment
- Currently, the backend uses the main environment by default
- Future: Can be enhanced to use subprocess calls to the separate TTS environment

