# Running Backend on HiPerGator

This guide explains how to run the African Health Studio backend on HiPerGator with GPU support.

## Quick Start

### Option 1: Interactive GPU Session (Best for Development)

For interactive development and testing:

```bash
bash run_server_interactive.sh
```

This will:
- Request an interactive GPU session (4 hours)
- Automatically set up the environment
- Start the server
- Give you a shell where you can see logs in real-time

### Option 2: SLURM Batch Job (Best for Production)

For production deployment:

```bash
sbatch run_server.slurm
```

This will:
- Submit a batch job to SLURM
- Run for 8 hours (configurable)
- Log output to `backend_<jobid>.log` and `backend_<jobid>.err`
- Keep running even if you disconnect

Check job status:
```bash
squeue -u $USER
```

View logs:
```bash
tail -f backend_<jobid>.log
```

Cancel job:
```bash
scancel <jobid>
```

## Environment Setup

The scripts automatically:
1. Load CUDA 12.8.1 module
2. Set CUDA environment variables
3. Set PYTHONPATH to include project and Audio Flamingo
4. Activate UV environment
5. Start the FastAPI server

## GPU Requirements

- **Partition**: `hpg-b200` (B200 GPUs)
- **GPUs**: 1
- **Memory**: 60-64GB RAM
- **CPUs**: 8

## Server Access

Once the server starts, it will be available at:
- `http://<compute-node>:8000`

To access from outside HiPerGator, you may need to:
1. Set up SSH tunneling
2. Or configure HiPerGator networking

## Model Loading

On startup, the server will:
1. Load Audio Flamingo 3 (AF3) onto GPU
2. Load Meta MMS-TTS onto GPU
3. Log model loading status

Check logs to verify models loaded successfully:
```bash
grep "loaded successfully" backend_*.log
```

## Troubleshooting

### Check GPU allocation
```bash
nvidia-smi
```

### Check if server is running
```bash
squeue -u $USER
netstat -tuln | grep 8000
```

### View real-time logs
```bash
tail -f backend_<jobid>.log
```

### Test server endpoint
```bash
curl http://localhost:8000/
```

## Configuration

### Adjust SLURM resources

Edit `run_server.slurm` to change:
- `--time`: Job time limit (default: 8 hours)
- `--mem`: Memory allocation (default: 60GB)
- `--cpus-per-task`: CPU cores (default: 8)

### Change server port

Edit `backend/app/server.py` last line:
```python
uvicorn.run("backend.app.server:app", host="0.0.0.0", port=8000)
```

## Local Development (Non-GPU)

For local testing without GPU:

```bash
bash run_server.sh
```

This will run on CPU (slower but useful for testing).

