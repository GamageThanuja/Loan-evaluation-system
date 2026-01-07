#!/bin/bash

# Home Credit Loan Approval System - Stop Script
# This script stops all running services

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[ℹ]${NC} $1"
}

echo "=========================================="
echo "  Stopping All Services..."
echo "=========================================="
echo ""

# Kill processes by PID
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        print_status "Backend stopped (PID: $BACKEND_PID)"
    else
        print_info "Backend process not running"
    fi
    rm logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        print_status "Frontend stopped (PID: $FRONTEND_PID)"
    else
        print_info "Frontend process not running"
    fi
    rm logs/frontend.pid
fi

# Also kill any process on ports 3000 and 8000
if lsof -i :3000 >/dev/null 2>&1; then
    lsof -ti :3000 | xargs kill -9 2>/dev/null || true
    print_status "Cleared port 3000"
fi

if lsof -i :8000 >/dev/null 2>&1; then
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    print_status "Cleared port 8000"
fi

echo ""
print_status "All services stopped successfully!"
echo ""
