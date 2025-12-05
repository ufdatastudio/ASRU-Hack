#!/bin/bash
#SBATCH --account=ufdatastudios
#SBATCH --job-name=tts-backend
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=8:00:00
#SBATCH --mem=32GB
#SBATCH --partition=gpu-l4
#SBATCH --cpus-per-task=4
#SBATCH --output=tts_backend_%j.log
#SBATCH --error=tts_backend_%j.err

set -euo pipefail

echo "=========================================="
echo "Afro-TTS Backend Service"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "=========================================="

echo ""
echo "=== GPU STATUS ==="
nvidia-smi

echo ""
echo "=== Setting up TTS environment ==="

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

# Activate TTS environment if it exists
if [ -d "$PROJECT_ROOT/tts-env/venv" ]; then
    echo "Activating TTS virtual environment..."
    source $PROJECT_ROOT/tts-env/venv/bin/activate
else
    echo "TTS virtual environment not found, using main environment"
fi

echo "Project root: $PROJECT_ROOT"
echo "Python path: $PYTHONPATH"

echo ""
echo "=== Starting Afro-TTS Backend Service ==="
echo "Service will be available at: http://$(hostname):8002"
echo ""

# Run TTS backend service
if [ -d "$PROJECT_ROOT/tts-env/venv" ]; then
    # Use TTS environment's Python
    $PROJECT_ROOT/tts-env/venv/bin/python -m backend.app.services.tts_backend 2>&1 | tee tts_backend_${SLURM_JOB_ID}.log
else
    # Use main environment
    uv run python -m backend.app.services.tts_backend 2>&1 | tee tts_backend_${SLURM_JOB_ID}.log
fi

echo ""
echo "=== TTS Backend Service stopped ==="

