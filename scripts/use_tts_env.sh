#!/bin/bash
# Activate TTS environment and run a command
# Usage: bash scripts/use_tts_env.sh <command>

TTS_ENV_DIR="/orange/ufdatastudios/c.okocha/ASRU-Hack/tts-env/venv"

if [ ! -d "$TTS_ENV_DIR" ]; then
    echo "TTS environment not found. Run: bash scripts/setup_tts_env.sh"
    exit 1
fi

source "$TTS_ENV_DIR/bin/activate"

# Run the command if provided
if [ $# -gt 0 ]; then
    exec "$@"
else
    echo "TTS environment activated. Run your command now."
    echo "To deactivate: deactivate"
    exec bash
fi

