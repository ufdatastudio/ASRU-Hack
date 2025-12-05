#!/bin/bash
#SBATCH --account=ufdatastudios
#SBATCH --job-name=af3-backend
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=8:00:00
#SBATCH --mem=60GB
#SBATCH --partition=hpg-b200
#SBATCH --cpus-per-task=8
#SBATCH --output=af3_backend_%j.log
#SBATCH --error=af3_backend_%j.err

set -euo pipefail

echo "=========================================="
echo "AF3 Backend Service"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "=========================================="

echo ""
echo "=== GPU STATUS ==="
nvidia-smi

echo ""
echo "=== Setting up AF3 environment ==="

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
export PYTHONPATH=$PYTHONPATH:/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3

echo "Project root: $PROJECT_ROOT"
echo "Python path: $PYTHONPATH"

echo ""
echo "=== Starting AF3 Backend Service ==="
echo "Service will be available at: http://$(hostname):8001"
echo ""

# Run AF3 backend service
uv run python -m backend.app.services.af3_backend 2>&1 | tee af3_backend_${SLURM_JOB_ID}.log

echo ""
echo "=== AF3 Backend Service stopped ==="

