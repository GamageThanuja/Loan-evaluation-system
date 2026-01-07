#!/bin/bash

# Loan Evaluation System - Start All Services
# This script starts backend API, frontend, and ML services

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOG_DIR="$PROJECT_ROOT/logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Starting Loan Evaluation System${NC}"
echo -e "${GREEN}================================${NC}"

# Create logs directory
mkdir -p "$LOG_DIR"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}Loading environment variables...${NC}"
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
else
    echo -e "${RED}Warning: .env file not found!${NC}"
fi

# Function to check if port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Start Backend API
echo -e "\n${YELLOW}[1/2] Starting Backend API Server...${NC}"
cd "$BACKEND_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if port 8000 is already in use
if check_port 8000; then
    echo -e "${RED}Port 8000 is already in use. Stopping existing process...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start backend in background
echo -e "${GREEN}Starting backend on http://localhost:8000${NC}"
nohup python api.py > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$LOG_DIR/backend.pid"
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    sleep 1
done

# Start Frontend
echo -e "\n${YELLOW}[2/2] Starting Frontend Server...${NC}"
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Check if port 3000 is already in use
if check_port 3000; then
    echo -e "${RED}Port 3000 is already in use. Stopping existing process...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start frontend in background
echo -e "${GREEN}Starting frontend on http://localhost:3000${NC}"
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

# Summary
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}All Services Started Successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${YELLOW}Backend API:${NC}     http://localhost:8000"
echo -e "${YELLOW}API Docs:${NC}        http://localhost:8000/docs"
echo -e "${YELLOW}Frontend:${NC}        http://localhost:3000"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "  Backend:  tail -f $LOG_DIR/backend.log"
echo -e "  Frontend: tail -f $LOG_DIR/frontend.log"
echo -e "\n${YELLOW}To stop all services, run:${NC} ./stop.sh"
echo -e "${GREEN}================================${NC}\n"

cd "$PROJECT_ROOT"
