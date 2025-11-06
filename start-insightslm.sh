#!/bin/bash

# InsightsLM Startup Script - Step 10
# This script starts both the backend and frontend for InsightsLM
# UPDATED: Now includes port fallback logic (8000-8050) matching Electron auto-start

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     InsightsLM Startup Script         ║${NC}"
echo -e "${BLUE}║     Step 10: Port Fallback Support    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: This script must be run from the InsightsLM root directory${NC}"
    echo -e "${YELLOW}Usage: cd ~/InsightsLM && ./start-insightslm.sh${NC}"
    exit 1
fi

# Port configuration (matches Electron implementation)
PORT_MIN=8000
PORT_MAX=8050
BACKEND_PID=""
BACKEND_PORT=""

# Cleanup function to kill backend on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down InsightsLM...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID, Port: $BACKEND_PORT)...${NC}"
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}Backend stopped${NC}"
    fi
    echo -e "${GREEN}InsightsLM shutdown complete${NC}"
    exit 0
}

# Set up trap to call cleanup on script exit
trap cleanup EXIT INT TERM

# Step 1: Navigate to backend directory
echo -e "${BLUE}[1/4] Preparing backend environment...${NC}"

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at backend/venv${NC}"
    echo -e "${YELLOW}Please create it first: python3 -m venv venv${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated${NC}"

# Step 2: Start Backend with Port Fallback
echo -e "${BLUE}[2/4] Starting backend with port fallback (${PORT_MIN}-${PORT_MAX})...${NC}"

BACKEND_STARTED=false

for PORT in $(seq $PORT_MIN $PORT_MAX); do
    echo -e "${CYAN}Trying port ${PORT}...${NC}"
    
    # Start uvicorn on current port in background
    uvicorn main:app --host 0.0.0.0 --port $PORT > /tmp/insightslm-backend-$PORT.log 2>&1 &
    TEMP_PID=$!
    
    # Wait a moment for the process to start
    sleep 1
    
    # Check if process is still running
    if ! kill -0 $TEMP_PID 2>/dev/null; then
        echo -e "${YELLOW}Port ${PORT} spawn failed, trying next...${NC}"
        continue
    fi
    
    # Try health check (30 attempts = 30 seconds)
    MAX_RETRIES=30
    RETRY_COUNT=0
    HEALTH_PASSED=false
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s http://127.0.0.1:$PORT/health > /dev/null 2>&1; then
            HEALTH_PASSED=true
            break
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 1
        
        # Check if backend process is still alive
        if ! kill -0 $TEMP_PID 2>/dev/null; then
            echo -e "${YELLOW}Backend died during startup on port ${PORT}${NC}"
            break
        fi
    done
    
    if [ "$HEALTH_PASSED" = true ]; then
        echo -e "${GREEN}✅ Backend started successfully on port ${PORT}!${NC}"
        BACKEND_PID=$TEMP_PID
        BACKEND_PORT=$PORT
        BACKEND_STARTED=true
        break
    else
        # Health check failed, kill this attempt and try next port
        echo -e "${YELLOW}Port ${PORT} health check failed, trying next...${NC}"
        kill $TEMP_PID 2>/dev/null
        wait $TEMP_PID 2>/dev/null
    fi
done

# Check if backend started successfully
if [ "$BACKEND_STARTED" = false ]; then
    echo -e "${RED}❌ Failed to start backend on any port (${PORT_MIN}-${PORT_MAX})${NC}"
    echo -e "${YELLOW}All ports may be in use or there's a configuration issue${NC}"
    echo -e "${YELLOW}Check logs: ls -lh /tmp/insightslm-backend-*.log${NC}"
    echo -e "${YELLOW}View latest log: tail /tmp/insightslm-backend-${PORT_MAX}.log${NC}"
    exit 1
fi

# Step 3: Export port for frontend (if needed)
echo -e "${BLUE}[3/4] Configuring frontend environment...${NC}"
export INSIGHTSLM_PORT=$BACKEND_PORT
echo -e "${GREEN}Backend port ${BACKEND_PORT} exported to environment${NC}"

# Step 4: Start Frontend
echo -e "${BLUE}[4/4] Starting frontend...${NC}"
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Backend: http://127.0.0.1:${BACKEND_PORT}       ║${NC}"
echo -e "${GREEN}║  Status: Running (PID: $BACKEND_PID)         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop InsightsLM${NC}"
echo -e "${CYAN}Frontend will open in Electron app...${NC}"
echo ""

cd ../frontend

# Start the Electron app (this blocks until app is closed)
npm start

# When npm start exits, the trap will call cleanup()
