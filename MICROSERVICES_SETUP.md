# Microservices Architecture Setup

The backend is split into three separate services:

1. **AF3 Backend** (port 8001) - Audio Flamingo 3 inference
2. **TTS Backend** (port 8002) - Afro-TTS synthesis  
3. **Main API** (port 8000) - Orchestrates requests, talks to frontend

## Architecture

```
Frontend (Next.js)
    ↓
Main API Server (port 8000)
    ├──→ AF3 Backend (port 8001) - GPU partition: hpg-b200
    └──→ TTS Backend (port 8002) - GPU partition: gpu-l4
```

## Running the Services

### 1. Start AF3 Backend

```bash
sbatch run_af3_backend.slurm
```

This will:
- Run on `hpg-b200` partition (B200 GPUs)
- Load AF3 model
- Listen on port 8001
- Log to `af3_backend_<jobid>.log`

**Get the node hostname:**
```bash
squeue -j <jobid> -o "%N"
```

### 2. Start TTS Backend

```bash
sbatch run_tts_backend.slurm
```

This will:
- Run on `gpu-l4` partition (L4 GPUs)
- Load Afro-TTS model
- Listen on port 8002
- Log to `tts_backend_<jobid>.log`

**Get the node hostname:**
```bash
squeue -j <jobid> -o "%N"
```

### 3. Start Main API Server

```bash
# Set service URLs (replace with actual node hostnames)
export AF3_SERVICE_URL="http://<af3-node-hostname>:8001"
export TTS_SERVICE_URL="http://<tts-node-hostname>:8002"

sbatch run_server.slurm
```

Or update `run_server.slurm` with the URLs directly.

## Service URLs

After starting the services, update the main API with actual node hostnames:

```bash
# In run_server.slurm or before running:
export AF3_SERVICE_URL="http://c1234.ufhpc:8001"
export TTS_SERVICE_URL="http://c5678.ufhpc:8002"
```

## Health Checks

Check if services are running:

```bash
# AF3 service
curl http://<af3-node>:8001/health

# TTS service
curl http://<tts-node>:8002/health
```

## Frontend

**No changes needed!** The frontend still connects to:
- `ws://localhost:8000/ws/audio` (or your main API server)

The main API handles communication with AF3 and TTS services.

## Benefits

- ✅ Separate GPU partitions for each model
- ✅ Independent scaling
- ✅ Isolated environments (AF3 can use different Python/Torch versions than TTS)
- ✅ Better resource utilization
- ✅ Easier debugging (check individual service logs)

## Troubleshooting

### Services can't connect

1. Check service URLs are correct (use actual node hostnames)
2. Check firewall/network between nodes
3. Verify services are running: `squeue -u $USER`

### Main API can't reach services

- Services must be accessible from the main API node
- Use node hostnames, not `localhost`
- Check SLURM network configuration

