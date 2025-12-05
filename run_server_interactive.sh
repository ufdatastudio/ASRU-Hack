#!/bin/bash
# Interactive GPU session script for development
# Usage: bash run_server_interactive.sh

echo "=========================================="
echo "Starting Interactive GPU Session"
echo "African Health Studio Backend"
echo "=========================================="
echo ""
echo "This will request an interactive GPU session with:"
echo "  - Account: ufdatastudios"
echo "  - Partition: hpg-b200"
echo "  - GPUs: 1"
echo "  - CPUs: 8"
echo "  - Memory: 64GB"
echo "  - Time: 4 hours"
echo ""
echo "After the session starts, the server will automatically start."
echo "Press Ctrl+C to stop the server and exit the session."
echo ""

# Start interactive session
srun --account=ufdatastudios \
  --partition=hpg-b200 \
  --gpus=1 \
  --cpus-per-task=8 \
  --mem=64GB \
  --time=04:00:00 \
  --pty bash << 'ENDSSH'

# Inside the interactive session
echo ""
echo "=== GPU STATUS ==="
nvidia-smi

echo ""
echo "=== Setting up environment ==="

# Load CUDA module
module load cuda/12.8.1

# Set CUDA paths
export CUDA_HOME=/apps/compilers/cuda/12.8.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Set project root
PROJECT_ROOT="/orange/ufdatastudios/c.okocha/ASRU-Hack"
cd $PROJECT_ROOT

# Set Python path
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH

# Add Audio Flamingo path if needed
export PYTHONPATH=$PYTHONPATH:/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3

echo "Project root: $PROJECT_ROOT"
echo "Python path: $PYTHONPATH"
echo ""
echo "=== Starting AF3 + MMS-TTS backend server ==="
echo "Server will be available at: http://$(hostname):8000"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uv run python -m backend.app.server

ENDSSH

echo ""
echo "=== Session ended ==="

