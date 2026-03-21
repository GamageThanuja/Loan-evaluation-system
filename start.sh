#!/bin/bash
# =============================================================================
# LoanWise Application Startup Script
# Starts both backend (FastAPI) and frontend (Next.js) servers
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=============================================================================${NC}"
echo -e "${BLUE}                   LoanWise - Starting Application                           ${NC}"
echo -e "${BLUE}=============================================================================${NC}"
echo ""

# =============================================================================
# Check if services are already running
# =============================================================================

echo -e "${YELLOW}⏳ Checking for existing services...${NC}"

# Check backend port
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}❌ Backend already running on port 8000${NC}"
    echo -e "   Stop it with: lsof -ti:8000 | xargs kill -9"
    exit 1
fi

# Check frontend port
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}❌ Frontend already running on port 3000${NC}"
    echo -e "   Stop it with: lsof -ti:3000 | xargs kill -9"
    exit 1
fi

echo -e "${GREEN}✅ Ports available${NC}\n"

# =============================================================================
# Setup Backend
# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          Backend Setup                                    ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Install/update dependencies
if [ ! -f "venv/.dependencies_installed" ]; then
    echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
    pip install --upgrade pip setuptools wheel -q
    pip install -r requirements.txt --no-cache-dir
    touch venv/.dependencies_installed
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/backend:$PROJECT_ROOT/ml-model"

# =============================================================================
# Setup Frontend
# =============================================================================

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          Frontend Setup                                   ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# =============================================================================
# Start Services
# =============================================================================

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                         Starting Services                                 ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Start Backend
echo -e "${YELLOW}🚀 Starting Backend API (FastAPI)...${NC}"
cd "$PROJECT_ROOT/backend"
source venv/bin/activate
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/backend:$PROJECT_ROOT/ml-model"
nohup python -m uvicorn api:app --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_ROOT/logs/backend.pid"

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    echo -e "   URL: http://localhost:8000"
    echo -e "   Docs: http://localhost:8000/docs"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo -e "   Check logs: $PROJECT_ROOT/logs/backend.log"
    exit 1
fi

# Start Frontend
echo -e "\n${YELLOW}🚀 Starting Frontend (Next.js)...${NC}"
cd "$PROJECT_ROOT/frontend"
nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to initialize...${NC}"
sleep 8

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo -e "   URL: http://localhost:3000"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo -e "   Check logs: $PROJECT_ROOT/logs/frontend.log"
    # Kill backend if frontend failed
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# =============================================================================
# Success Summary
# =============================================================================

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                    🎉 Application Started Successfully! 🎉                ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo -e "   Frontend:    ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}📊 Model Information:${NC}"
echo -e "   Architecture: Hybrid Bayesian (BNN + Gradient Boosting)"
echo -e "   Version:      3.0.0"
echo -e "   Threshold:    0.50"
echo -e "   Accuracy:     99.41%"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   Backend:  $PROJECT_ROOT/logs/backend.log"
echo -e "   Frontend: $PROJECT_ROOT/logs/frontend.log"
echo ""
echo -e "${BLUE}🛑 To stop the application:${NC}"
echo -e "   Run: ${YELLOW}./stop.sh${NC}"
echo -e "   Or manually:"
echo -e "     Backend:  kill $BACKEND_PID"
echo -e "     Frontend: kill $FRONTEND_PID"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Monitor mode (optional)
echo -e "${YELLOW}Press Ctrl+C to stop monitoring (services will continue running)${NC}"
echo -e "${YELLOW}Or run './scripts/stop.sh' to stop all services${NC}\n"

# Keep script running to show real-time logs
tail -f "$PROJECT_ROOT/logs/backend.log" "$PROJECT_ROOT/logs/frontend.log" 2>/dev/null || true
