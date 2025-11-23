#!/bin/bash
export CUDA_HOME=/apps/compilers/cuda/12.8.1
export PATH=$CUDA_HOME/bin:$PATH

# Add the local Audio Flamingo directory to PYTHONPATH just in case
export PYTHONPATH=$PYTHONPATH:/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3

# Run the server
uv run python -m backend.app.server

