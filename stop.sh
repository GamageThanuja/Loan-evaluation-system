#!/bin/bash
# =============================================================================
# LoanWise Application Stop Script
# Stops both backend and frontend servers
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo -e "${BLUE}=============================================================================${NC}"
echo -e "${BLUE}                   LoanWise - Stopping Application                          ${NC}"
echo -e "${BLUE}=============================================================================${NC}"
echo ""

# =============================================================================
# Stop Backend
# =============================================================================

echo -e "${YELLOW}🛑 Stopping Backend...${NC}"

# Try to stop using PID file
if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend PID not found${NC}"
    fi
    rm -f "$PROJECT_ROOT/logs/backend.pid"
fi

# Kill any process on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}🔧 Killing process on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Port 8000 freed${NC}"
fi

# =============================================================================
# Stop Frontend
# =============================================================================

echo -e "\n${YELLOW}🛑 Stopping Frontend...${NC}"

# Try to stop using PID file
if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend PID not found${NC}"
    fi
    rm -f "$PROJECT_ROOT/logs/frontend.pid"
fi

# Kill any process on port 3000
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}🔧 Killing process on port 3000...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Port 3000 freed${NC}"
fi

# =============================================================================
# Cleanup
# =============================================================================

echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"

# Wait for processes to terminate
sleep 2

# Check if ports are really free
BACKEND_RUNNING=$(lsof -Pi :8000 -sTCP:LISTEN -t 2>/dev/null | wc -l | tr -d ' ')
FRONTEND_RUNNING=$(lsof -Pi :3000 -sTCP:LISTEN -t 2>/dev/null | wc -l | tr -d ' ')

if [ "$BACKEND_RUNNING" -eq "0" ] && [ "$FRONTEND_RUNNING" -eq "0" ]; then
    echo -e "${GREEN}✅ All services stopped successfully${NC}"
else
    if [ "$BACKEND_RUNNING" -ne "0" ]; then
        echo -e "${RED}❌ Backend still running on port 8000${NC}"
    fi
    if [ "$FRONTEND_RUNNING" -ne "0" ]; then
        echo -e "${RED}❌ Frontend still running on port 3000${NC}"
    fi
    echo -e "${YELLOW}⚠️  Try running the script again or manually kill processes${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                         Application Stopped                               ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
