#!/bin/bash
#SBATCH --account=ufdatastudios
#SBATCH --job-name=main-api-server
#SBATCH --nodes=1
#SBATCH --gpus=0
#SBATCH --time=8:00:00
#SBATCH --mem=16GB
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=4
#SBATCH --output=main_api_%j.log
#SBATCH --error=main_api_%j.err

set -euo pipefail

echo "=========================================="
echo "African Health Studio Main API Server"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "=========================================="
echo ""
echo "This is the main API server (no GPU needed)"
echo "It communicates with:"
echo "  - AF3 Backend: http://<af3-node>:8001"
echo "  - TTS Backend: http://<tts-node>:8002"
echo ""

echo ""
echo "=== Setting up environment ==="

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
echo "=== Starting Main API Server ==="
echo "Server will be available at: http://$(hostname):8000"
echo ""
echo "Make sure AF3 and TTS backend services are running!"
echo ""

# Set backend service URLs (update with actual node hostnames)
export AF3_SERVICE_URL=${AF3_SERVICE_URL:-"http://localhost:8001"}
export TTS_SERVICE_URL=${TTS_SERVICE_URL:-"http://localhost:8002"}

echo "AF3 Service URL: $AF3_SERVICE_URL"
echo "TTS Service URL: $TTS_SERVICE_URL"
echo ""

# Run main API server
uv run python -m backend.app.server 2>&1 | tee main_api_${SLURM_JOB_ID}.log

echo ""
echo "=== Server stopped ==="

