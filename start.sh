#!/bin/bash

# Home Credit Loan Approval System - Development Startup Script
# This script starts all services (Database, Backend, Frontend) in one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if port_in_use "$1"; then
        print_warning "Port $1 is in use. Killing process..."
        lsof -ti :"$1" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

echo "=========================================="
echo "  Home Credit Loan Approval System"
echo "  Starting All Services..."
echo "=========================================="
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

if ! command_exists python3; then
    print_error "Python is not installed. Please install Python 3.8+"
    exit 1
fi

print_status "All prerequisites met"
echo ""

# Check if setup has been run
if [ ! -d "backend/venv" ]; then
    print_warning "Backend virtual environment not found. Running setup..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    print_status "Backend setup complete"
fi

if [ ! -d "frontend/node_modules" ]; then
    print_warning "Frontend dependencies not found. Installing..."
    cd frontend
    npm install
    cd ..
    print_status "Frontend setup complete"
fi

echo ""

# Check environment files
print_info "Checking environment configuration..."

if [ ! -f "backend/.env" ]; then
    print_warning "backend/.env not found. Creating from example..."
    cp backend/.env.example backend/.env
    print_warning "⚠️  Please edit backend/.env with your Supabase credentials!"
fi

if [ ! -f "frontend/.env.local" ]; then
    print_warning "frontend/.env.local not found. Creating from example..."
    if [ -f "frontend/.env.local.example" ]; then
        cp frontend/.env.local.example frontend/.env.local
    fi
fi

print_status "Environment files checked"
echo ""

# Kill processes on ports if they exist
print_info "Checking ports..."
kill_port 3000
kill_port 8000
print_status "Ports cleared"
echo ""

# Create log directory
mkdir -p logs

# Start services
print_info "Starting services..."
echo ""

# Start Backend
print_status "Starting Backend API (Port 8000)..."
cd backend
source venv/bin/activate
nohup python api.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "Backend PID: $BACKEND_PID"
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    print_status "Backend started successfully at http://localhost:8000"
else
    print_error "Backend failed to start. Check logs/backend.log"
    exit 1
fi

# Start Frontend
print_status "Starting Frontend (Port 3000)..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"
sleep 5

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    print_status "Frontend started successfully at http://localhost:3000"
else
    print_error "Frontend failed to start. Check logs/frontend.log"
    exit 1
fi

echo ""
echo "=========================================="
echo "  ✅ All Services Started Successfully!"
echo "=========================================="
echo ""
echo "📊 Service Status:"
echo "  - Frontend:  http://localhost:3000  (PID: $FRONTEND_PID)"
echo "  - Backend:   http://localhost:8000  (PID: $BACKEND_PID)"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Database:  Supabase (Check your dashboard)"
echo ""
echo "📝 Logs:"
echo "  - Backend:  tail -f logs/backend.log"
echo "  - Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop all services, run:"
echo "  ./stop.sh"
echo ""
echo "🔑 Default Login:"
echo "  Email:    officer@example.com"
echo "  Password: password123"
echo "  Role:     Loan Officer"
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

# Keep script running and show logs
echo "Press Ctrl+C to view logs or run './stop.sh' to stop services"
echo ""

# Option to follow logs
read -p "Would you like to view logs? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    tail -f logs/backend.log logs/frontend.log
fi
