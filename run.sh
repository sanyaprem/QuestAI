#!/bin/bash

# QuestAI Startup Script
# This script starts both backend and frontend servers

echo "=================================="
echo "QuestAI - Starting Application"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and add your API keys"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${RED}Warning: No virtual environment detected${NC}"
    echo "Consider activating your environment first:"
    echo "  conda activate ai-agent"
    echo ""
fi

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Servers stopped${NC}"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT TERM

# Start backend server
echo -e "${BLUE}Starting Backend Server...${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend_server.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Backend failed to start${NC}"
    echo "Check logs/backend_server.log for details"
    exit 1
fi

echo -e "${GREEN}✓ Backend running on http://localhost:8000${NC}"

# Start frontend server
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd frontend
streamlit run Home.py --server.port 8501 --server.address localhost > ../logs/frontend_server.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "Waiting for frontend to initialize..."
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Frontend failed to start${NC}"
    echo "Check logs/frontend_server.log for details"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend running on http://localhost:8501${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}QuestAI is now running!${NC}"
echo "=================================="
echo ""
echo "Backend API:  http://localhost:8000"
echo "Frontend UI:  http://localhost:8501"
echo "API Docs:     http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:    logs/backend_server.log"
echo "  Frontend:   logs/frontend_server.log"
echo "  App:        logs/quest_ai.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for processes
wait