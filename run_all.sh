#!/bin/bash

# Script to run both backend and frontend together

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Setup Node.js
export PATH="/apps/nodejs/22.12.0/bin:$PATH"
NODE_BIN="/apps/nodejs/22.12.0/bin/node"
NPM_BIN="/apps/nodejs/22.12.0/bin/npm"

echo -e "${BLUE}Starting African health studio...${NC}\n"

# Check if Node.js is available
if [ ! -f "$NODE_BIN" ]; then
    echo -e "${YELLOW}Error: Node.js not found at $NODE_BIN${NC}"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend-next/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend-next
    $NPM_BIN install
    cd ..
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Start backend in background
echo -e "${GREEN}Starting backend server on port 8000...${NC}"
export CUDA_HOME=/apps/compilers/cuda/12.8.1
export PATH=$CUDA_HOME/bin:$PATH
export PYTHONPATH=$PYTHONPATH:/orange/ufdatastudios/c.okocha/audio-flamingo-audio_flamingo_3

uv run python -m backend.app.server &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend server on port 3000...${NC}"
cd frontend-next
PATH="/apps/nodejs/22.12.0/bin:$PATH" $NPM_BIN run dev &
FRONTEND_PID=$!
cd ..

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Backend: http://localhost:8000${NC}"
echo -e "${GREEN}✓ Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}========================================${NC}\n"
echo -e "Press Ctrl+C to stop both servers\n"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

