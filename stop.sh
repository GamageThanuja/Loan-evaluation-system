#!/bin/bash

# Loan Evaluation System - Stop All Services
# This script stops backend API, frontend, and ML services

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}================================${NC}"
echo -e "${RED}Stopping Loan Evaluation System${NC}"
echo -e "${RED}================================${NC}"

# Function to stop process by PID file
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping $service_name (PID: $PID)...${NC}"
            kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
            rm -f "$pid_file"
            echo -e "${GREEN}✓ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}$service_name is not running${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}No PID file found for $service_name${NC}"
    fi
}

# Function to kill process by port
kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}Killing process on port $port ($service_name)...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ Stopped process on port $port${NC}"
    fi
}

# Stop Backend
echo -e "\n${YELLOW}[1/2] Stopping Backend API Server...${NC}"
stop_service "Backend" "$LOG_DIR/backend.pid"
kill_port 8000 "Backend API"

# Stop Frontend
echo -e "\n${YELLOW}[2/2] Stopping Frontend Server...${NC}"
stop_service "Frontend" "$LOG_DIR/frontend.pid"
kill_port 3000 "Frontend"

# Kill any remaining Node.js processes from Next.js
pkill -f "next dev" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

# Kill any remaining Python API processes
pkill -f "api.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Summary
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}All Services Stopped Successfully!${NC}"
echo -e "${GREEN}================================${NC}"

# Cleanup log files (optional)
read -p "Do you want to clear log files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$LOG_DIR"/*.log
    echo -e "${GREEN}✓ Log files cleared${NC}"
fi

echo -e "${YELLOW}To start all services again, run:${NC} ./start.sh\n"
