#!/bin/bash
################################################################################
# Master Information Extraction Script for InsightsLM
# Purpose: Extract both backend and frontend information in one go
# Location: ~/InsightsLM/scripts/extract_all_info.sh
# Usage: ./scripts/extract_all_info.sh
################################################################################

set +e  # Don't exit on error - we want to continue even if one part fails

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMBINED_OUTPUT="$HOME/InsightsLM/application_info_${TIMESTAMP}.txt"
BACKEND_SUCCESS=false
FRONTEND_SUCCESS=false

# Get Windows username from WSL
WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')

echo -e "${CYAN}"
echo "════════════════════════════════════════════════════════════════"
echo "           INSIGHTSLM COMPLETE INFORMATION EXTRACTION           "
echo "════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo -e "This script will extract comprehensive information about:"
echo -e "  ${GREEN}✓${NC} Backend (Python/FastAPI in WSL)"
echo -e "  ${GREEN}✓${NC} Frontend (Electron/React in Windows)"
echo ""
echo -e "Timestamp: ${YELLOW}$TIMESTAMP${NC}"
echo ""

# Create combined output header
cat > "$COMBINED_OUTPUT" << EOF
################################################################################
#                                                                              #
#                  INSIGHTSLM APPLICATION INFORMATION                          #
#                         COMPLETE EXTRACTION                                  #
#                                                                              #
################################################################################

Generated: $(date)
Purpose: Documentation review and verification
System: Windows 11 + WSL2 Ubuntu (Hybrid Architecture)

================================================================================
TABLE OF CONTENTS
================================================================================

PART 1: BACKEND INFORMATION (Python/FastAPI/WSL)
  1. System Information
  2. Directory Structure
  3. Python Environment
  4. Installed Packages
  5. Import Verification
  6. Configuration
  7. Database
  8. Vector Database
  9. API Endpoints
  10. Running Processes
  11. Key Files
  12. Git Information

PART 2: FRONTEND INFORMATION (Electron/React/Windows)
  1. System Information
  2. Directory Structure
  3. Node.js Environment
  4. Installed Packages
  5. Package.json Analysis
  6. TypeScript Configuration
  7. Build Configuration
  8. Source Code Analysis
  9. Electron Processes
  10. Git Information
  11. Additional Information

================================================================================

EOF

################################################################################
# PART 1: BACKEND EXTRACTION
################################################################################
echo -e "${BLUE}[PART 1/2]${NC} Extracting Backend Information..."
echo ""

# Check if backend script exists
BACKEND_SCRIPT="$HOME/InsightsLM/scripts/extract_backend_info.sh"
if [ ! -f "$BACKEND_SCRIPT" ]; then
    echo -e "${RED}Error: Backend extraction script not found at:${NC}"
    echo -e "  $BACKEND_SCRIPT"
    echo ""
    BACKEND_OUTPUT=""
else
    # Make script executable
    chmod +x "$BACKEND_SCRIPT"
    
    # Run backend extraction and capture output file path
    echo -e "${CYAN}Running backend extraction...${NC}"
    BACKEND_OUTPUT=$("$BACKEND_SCRIPT" 2>&1 | tail -n 1)
    
    # Check if output file was created
    if [ -f "$BACKEND_OUTPUT" ]; then
        echo -e "${GREEN}✓ Backend extraction complete${NC}"
        echo -e "  Output: $BACKEND_OUTPUT"
        BACKEND_SUCCESS=true
        
        # Append to combined output
        cat >> "$COMBINED_OUTPUT" << EOF


################################################################################
#                                                                              #
#                         PART 1: BACKEND INFORMATION                          #
#                                                                              #
################################################################################

EOF
        cat "$BACKEND_OUTPUT" >> "$COMBINED_OUTPUT"
    else
        echo -e "${RED}✗ Backend extraction failed${NC}"
        echo -e "  Expected output file not found"
        BACKEND_OUTPUT=""
    fi
fi

################################################################################
# PART 2: FRONTEND EXTRACTION
################################################################################
echo ""
echo -e "${BLUE}[PART 2/2]${NC} Extracting Frontend Information..."
echo ""

# Check if PowerShell is available
if ! command -v powershell.exe &> /dev/null; then
    echo -e "${RED}Error: PowerShell not available in WSL${NC}"
    echo "Cannot extract frontend information."
    FRONTEND_OUTPUT=""
else
    # Build frontend script path using environment variable
    FRONTEND_SCRIPT_WIN="C:\Users\\$WIN_USER\Projects\InsightsLM\scripts\extract_frontend_info.ps1"
    
    echo -e "${CYAN}Running frontend extraction via PowerShell...${NC}"
    
    # Pass the same timestamp to ensure matching filenames
    EXPECTED_WIN_PATH="C:\Users\\$WIN_USER\Projects\InsightsLM\frontend_info_${TIMESTAMP}.txt"
    
    # Run PowerShell script with NoProfile and bypassed execution policy
    FRONTEND_RAW_OUTPUT=$(powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$FRONTEND_SCRIPT_WIN" -OutputFile "$EXPECTED_WIN_PATH" 2>&1)
    
    # Extract the Windows path from PowerShell output (robust parsing)
    # Look for lines starting with a drive letter and backslash
    FRONTEND_OUTPUT_WIN=$(echo "$FRONTEND_RAW_OUTPUT" | tr -d '\r' | grep -E '^[A-Za-z]:\\.*\.txt$' | tail -n 1)
    
    if [ -n "$FRONTEND_OUTPUT_WIN" ]; then
        # Convert Windows path to WSL path
        FRONTEND_OUTPUT_WSL=$(wslpath -u "$FRONTEND_OUTPUT_WIN" 2>/dev/null)
        
        if [ -n "$FRONTEND_OUTPUT_WSL" ] && [ -f "$FRONTEND_OUTPUT_WSL" ]; then
            echo -e "${GREEN}✓ Frontend extraction complete${NC}"
            echo -e "  Output: $FRONTEND_OUTPUT_WIN"
            echo -e "  WSL path: $FRONTEND_OUTPUT_WSL"
            FRONTEND_SUCCESS=true
            FRONTEND_OUTPUT="$FRONTEND_OUTPUT_WIN"
            
            # Append to combined output
            cat >> "$COMBINED_OUTPUT" << EOF


################################################################################
#                                                                              #
#                        PART 2: FRONTEND INFORMATION                          #
#                                                                              #
################################################################################

EOF
            cat "$FRONTEND_OUTPUT_WSL" >> "$COMBINED_OUTPUT"
        else
            echo -e "${YELLOW}⚠ Frontend output file not found at WSL path: $FRONTEND_OUTPUT_WSL${NC}"
            echo -e "  Windows path was: $FRONTEND_OUTPUT_WIN"
        fi
    else
        echo -e "${RED}✗ Frontend extraction failed${NC}"
        echo ""
        echo "PowerShell output:"
        echo "$FRONTEND_RAW_OUTPUT"
        echo ""
        echo -e "${YELLOW}Possible issues:${NC}"
        echo "  1. PowerShell execution policy blocked the script"
        echo "  2. Script has syntax errors"
        echo "  3. Frontend directory not accessible"
        echo ""
        echo -e "${CYAN}To fix PowerShell execution policy:${NC}"
        echo "  Run in PowerShell: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    fi
fi

################################################################################
# COMPLETION
################################################################################
cat >> "$COMBINED_OUTPUT" << EOF


################################################################################
#                                                                              #
#                              END OF EXTRACTION                               #
#                                                                              #
################################################################################

Extraction completed: $(date)

Results:
  Backend:  $($BACKEND_SUCCESS && echo "✓ Success" || echo "✗ Failed")
  Frontend: $($FRONTEND_SUCCESS && echo "✓ Success" || echo "✗ Failed")

To share this information:
  1. Review the contents of this file
  2. Share with Claude or other developers
  3. Use for documentation verification

File locations:
  - Combined: $COMBINED_OUTPUT
  - Backend: ${BACKEND_OUTPUT:-"Not generated"}
  - Frontend: ${FRONTEND_OUTPUT:-"Not generated"}

EOF

echo ""
echo -e "${CYAN}"
echo "════════════════════════════════════════════════════════════════"
echo "                    EXTRACTION COMPLETE                          "
echo "════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""

# Summary
if $BACKEND_SUCCESS && $FRONTEND_SUCCESS; then
    echo -e "${GREEN}✓ All information extracted successfully${NC}"
elif $BACKEND_SUCCESS || $FRONTEND_SUCCESS; then
    echo -e "${YELLOW}⚠ Partial extraction completed${NC}"
    $BACKEND_SUCCESS || echo -e "  ${RED}✗${NC} Backend extraction failed"
    $FRONTEND_SUCCESS || echo -e "  ${RED}✗${NC} Frontend extraction failed"
else
    echo -e "${RED}✗ Extraction failed${NC}"
    echo ""
    echo "Please run the scripts individually to see detailed errors:"
    echo "  Backend:  ./scripts/extract_backend_info.sh"
    echo "  Frontend: cd /mnt/c/Users/$WIN_USER/Projects/InsightsLM && powershell.exe -ExecutionPolicy Bypass -File scripts\\extract_frontend_info.ps1"
fi

echo ""
echo -e "${YELLOW}Combined Output:${NC}"
echo -e "  Location: $COMBINED_OUTPUT"
echo -e "  Size: $(du -h $COMBINED_OUTPUT | cut -f1)"
echo ""

if [ -n "$BACKEND_OUTPUT" ] || [ -n "$FRONTEND_OUTPUT" ]; then
    echo -e "${YELLOW}Individual Outputs:${NC}"
    [ -n "$BACKEND_OUTPUT" ] && echo -e "  Backend:  $BACKEND_OUTPUT"
    [ -n "$FRONTEND_OUTPUT" ] && echo -e "  Frontend: $FRONTEND_OUTPUT"
    echo ""
fi

echo -e "${CYAN}Quick Actions:${NC}"
echo -e "  View file:        ${YELLOW}less $COMBINED_OUTPUT${NC}"
echo -e "  Copy to Windows:  ${YELLOW}cp $COMBINED_OUTPUT /mnt/c/Users/$WIN_USER/Downloads/${NC}"
echo -e "  Search in file:   ${YELLOW}grep -i 'search_term' $COMBINED_OUTPUT${NC}"
echo ""
