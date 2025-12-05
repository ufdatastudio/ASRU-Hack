#!/bin/bash
# Local development server script (CPU or if GPU already available)
# For GPU on HiPerGator, use: bash run_server_interactive.sh or sbatch run_server.slurm
#
# Note: Ensure dependencies are installed with: uv sync --all-extras

export CUDA_HOME=/apps/compilers/cuda/12.8.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Set project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $PROJECT_ROOT

# Set Python path
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH

# Add the local Audio Flamingo directory to PYTHONPATH just in case
export PYTHONPATH=$PYTHONPATH:/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3

echo "Starting African Health Studio Backend Server..."
echo "Project root: $PROJECT_ROOT"
echo "Python path: $PYTHONPATH"
echo ""
echo "Note: Using UV environment with dependency groups"
echo "Install dependencies with: uv sync --all-extras"
echo ""

# Run the server
uv run python -m backend.app.server

