#!/bin/bash
# Shell script to download models with proper environment setup

echo "=========================================="
echo "African Health Studio - Model Download"
echo "=========================================="
echo ""

# Set project root
PROJECT_ROOT="/orange/ufdatastudios/c.okocha/ASRU-Hack"
cd $PROJECT_ROOT

# Load CUDA module if available
if command -v module &> /dev/null; then
    echo "Loading CUDA module..."
    module load cuda/12.8.1
fi

# Set CUDA paths
export CUDA_HOME=/apps/compilers/cuda/12.8.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Set Python path
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3

echo "Project root: $PROJECT_ROOT"
echo "Python path: $PYTHONPATH"
echo ""

# Check GPU availability
if command -v nvidia-smi &> /dev/null; then
    echo "=== GPU Status ==="
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
fi

# Run download script
echo "Starting model download..."
echo ""

uv run python scripts/download_models.py

echo ""
echo "=========================================="
echo "Download complete!"
echo "=========================================="

