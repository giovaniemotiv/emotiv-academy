#!/usr/bin/env bash

# Terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Spotify BCI Setup and Launcher...${NC}"

# Check for Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null && python --version 2>&1 | grep -q 'Python 3'; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python 3 is not installed or not in your PATH.${NC}"
    echo -e "${YELLOW}Please install Python 3 from https://www.python.org/downloads/ and try again.${NC}"
    exit 1
fi

echo -e "Found Python: $($PYTHON_CMD --version)"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: requirements.txt not found in the current directory.${NC}"
    exit 1
fi

# Install requirements
echo -e "${YELLOW}Checking and installing dependencies...${NC}"
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Please check your internet connection or Python setup.${NC}"
    exit 1
fi

# Start the application
echo -e "${GREEN}Dependencies verified. Starting Spotify BCI...${NC}"
$PYTHON_CMD spotify_bci.py
