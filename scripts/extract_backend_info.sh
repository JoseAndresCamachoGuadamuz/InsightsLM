#!/bin/bash
################################################################################
# Backend Information Extraction Script for InsightsLM
# Purpose: Gather comprehensive backend information for documentation review
# Location: ~/InsightsLM/scripts/extract_backend_info.sh
# Usage: ./scripts/extract_backend_info.sh
################################################################################

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$HOME/InsightsLM/backend"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$HOME/InsightsLM/backend_info_${TIMESTAMP}.txt"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  INSIGHTSLM BACKEND INFORMATION${NC}"
echo -e "${BLUE}  Generated: $(date)${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Backend directory not found at: $BACKEND_DIR${NC}"
    exit 1
fi

# Create output file
cat > "$OUTPUT_FILE" << EOF
================================================================================
INSIGHTSLM BACKEND INFORMATION EXTRACTION
Generated: $(date)
================================================================================

EOF

################################################################################
# SECTION 1: SYSTEM INFORMATION
################################################################################
echo -e "\n${GREEN}[1/10] Gathering System Information...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
1. SYSTEM INFORMATION
================================================================================

Hostname: $(hostname)
OS: $(lsb_release -d 2>/dev/null | cut -f2 || echo "Unknown")
Kernel: $(uname -r)
Architecture: $(uname -m)

EOF

################################################################################
# SECTION 2: DIRECTORY STRUCTURE
################################################################################
echo -e "${GREEN}[2/10] Analyzing Directory Structure...${NC}"
cd "$BACKEND_DIR"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
2. DIRECTORY STRUCTURE
================================================================================

Backend Root: $BACKEND_DIR

Directory Tree (2 levels, excluding venv and cache):
EOF

if command -v tree &> /dev/null; then
    tree -L 2 -I 'venv|__pycache__|*.pyc|chroma_db|*.egg-info' >> "$OUTPUT_FILE" 2>&1
else
    echo "tree command not available, using ls instead" >> "$OUTPUT_FILE"
    ls -la >> "$OUTPUT_FILE" 2>&1
fi

cat >> "$OUTPUT_FILE" << EOF

Services Directory Contents:
EOF
if [ -d "services" ]; then
    ls -lh services/ >> "$OUTPUT_FILE" 2>&1
else
    echo "services directory not found" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

Database Directory Contents:
EOF
if [ -d "database" ]; then
    ls -lh database/ >> "$OUTPUT_FILE" 2>&1
else
    echo "database directory not found" >> "$OUTPUT_FILE"
fi

################################################################################
# SECTION 3: PYTHON ENVIRONMENT
################################################################################
echo -e "${GREEN}[3/10] Checking Python Environment...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
3. PYTHON ENVIRONMENT
================================================================================

EOF

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null && echo "Virtual environment activated" >> "$OUTPUT_FILE" || echo "Warning: Could not activate venv" >> "$OUTPUT_FILE"
else
    echo "Warning: venv directory not found" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF
Python Version: $(python3 --version 2>&1)
Python Path: $(which python3)
pip Version: $(pip --version 2>&1 || pip3 --version 2>&1)

EOF

################################################################################
# SECTION 4: INSTALLED PACKAGES
################################################################################
echo -e "${GREEN}[4/10] Listing Installed Packages...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
4. INSTALLED PACKAGES (Key Dependencies)
================================================================================

Core Web Framework:
EOF
pip list 2>/dev/null | grep -iE "fastapi|uvicorn|pydantic|starlette" >> "$OUTPUT_FILE" 2>&1 || echo "No matches found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

AI/ML Stack:
EOF
pip list 2>/dev/null | grep -iE "whisper|openai|anthropic|google-generativeai|chromadb|sentence-transformers" >> "$OUTPUT_FILE" 2>&1 || echo "No matches found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

Database & ORM:
EOF
pip list 2>/dev/null | grep -iE "sqlalchemy|alembic|psycopg2" >> "$OUTPUT_FILE" 2>&1 || echo "No matches found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

Audio Processing:
EOF
pip list 2>/dev/null | grep -iE "gtts|yt-dlp|ffmpeg|pydub" >> "$OUTPUT_FILE" 2>&1 || echo "No matches found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

Utilities:
EOF
pip list 2>/dev/null | grep -iE "requests|python-multipart|pycryptodome" >> "$OUTPUT_FILE" 2>&1 || echo "No matches found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

All Installed Packages:
EOF
pip list >> "$OUTPUT_FILE" 2>&1 || echo "Could not list packages" >> "$OUTPUT_FILE"

################################################################################
# SECTION 5: IMPORT VERIFICATION
################################################################################
echo -e "${GREEN}[5/10] Verifying Core Imports...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
5. CORE IMPORTS VERIFICATION
================================================================================

EOF

python3 << 'PYEOF' >> "$OUTPUT_FILE" 2>&1
import sys
print("Testing core imports...\n")

tests = [
    ("fastapi", "FastAPI framework"),
    ("whisper", "OpenAI Whisper"),
    ("chromadb", "Vector database"),
    ("sqlalchemy", "Database ORM"),
    ("openai", "OpenAI client"),
    ("anthropic", "Anthropic client"),
    ("google.generativeai", "Google Gemini client"),
    ("gtts", "Text-to-speech"),
    ("yt_dlp", "YouTube downloader"),
]

passed = 0
failed = 0

for module, description in tests:
    try:
        __import__(module)
        print(f"✓ {module:30} - {description}")
        passed += 1
    except ImportError as e:
        print(f"✗ {module:30} - FAILED: {str(e)}")
        failed += 1

print(f"\nResults: {passed} passed, {failed} failed")
PYEOF

################################################################################
# SECTION 6: CONFIGURATION
################################################################################
echo -e "${GREEN}[6/10] Checking Configuration...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
6. CONFIGURATION
================================================================================

Config File Location: ~/.local/share/InsightsLM/config.json
EOF

if [ -f "$HOME/.local/share/InsightsLM/config.json" ]; then
    echo "Status: EXISTS" >> "$OUTPUT_FILE"
    echo "Size: $(du -h $HOME/.local/share/InsightsLM/config.json | cut -f1)" >> "$OUTPUT_FILE"
    echo "Permissions: $(ls -lh $HOME/.local/share/InsightsLM/config.json | awk '{print $1}')" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "Note: Config file is encrypted, cannot display contents" >> "$OUTPUT_FILE"
else
    echo "Status: NOT FOUND" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

Data Directory: ~/.local/share/InsightsLM/
EOF
if [ -d "$HOME/.local/share/InsightsLM" ]; then
    ls -lh $HOME/.local/share/InsightsLM/ >> "$OUTPUT_FILE" 2>&1
else
    echo "Directory does not exist" >> "$OUTPUT_FILE"
fi

################################################################################
# SECTION 7: DATABASE
################################################################################
echo -e "${GREEN}[7/10] Analyzing Database...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
7. DATABASE INFORMATION
================================================================================

Database Location: ~/.local/share/InsightsLM/insightsLM.db
EOF

if [ -f "$HOME/.local/share/InsightsLM/insightsLM.db" ]; then
    echo "Status: EXISTS" >> "$OUTPUT_FILE"
    echo "Size: $(du -h $HOME/.local/share/InsightsLM/insightsLM.db | cut -f1)" >> "$OUTPUT_FILE"
    
    python3 << 'PYEOF' >> "$OUTPUT_FILE" 2>&1
import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/InsightsLM/insightsLM.db")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\nTables:")
    for table in tables:
        print(f"  - {table[0]}")
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    Records: {count}")
    
    conn.close()
except Exception as e:
    print(f"Error reading database: {e}")
PYEOF
else
    echo "Status: NOT FOUND" >> "$OUTPUT_FILE"
fi

################################################################################
# SECTION 8: VECTOR DATABASE
################################################################################
echo -e "${GREEN}[8/10] Checking Vector Database...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
8. VECTOR DATABASE (ChromaDB)
================================================================================

ChromaDB Location: ~/.local/share/InsightsLM/chroma_db/
EOF

if [ -d "$HOME/.local/share/InsightsLM/chroma_db" ]; then
    echo "Status: EXISTS" >> "$OUTPUT_FILE"
    echo "Size: $(du -sh $HOME/.local/share/InsightsLM/chroma_db 2>/dev/null | cut -f1 || echo 'Unknown')" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "Contents:" >> "$OUTPUT_FILE"
    ls -lh $HOME/.local/share/InsightsLM/chroma_db/ >> "$OUTPUT_FILE" 2>&1 || echo "Cannot list contents" >> "$OUTPUT_FILE"
else
    echo "Status: NOT FOUND" >> "$OUTPUT_FILE"
fi

################################################################################
# SECTION 9: API ENDPOINTS
################################################################################
echo -e "${GREEN}[9/10] Extracting API Endpoints...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
9. API ENDPOINTS
================================================================================

Endpoints defined in main.py:
EOF

if [ -f "main.py" ]; then
    grep -E "@app\.(get|post|put|delete|patch)" main.py | sed 's/^/  /' >> "$OUTPUT_FILE" 2>&1 || echo "No endpoints found" >> "$OUTPUT_FILE"
else
    echo "main.py not found" >> "$OUTPUT_FILE"
fi

################################################################################
# SECTION 10: RUNNING PROCESSES
################################################################################
echo -e "${GREEN}[10/10] Checking Running Processes...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
10. RUNNING PROCESSES
================================================================================

Uvicorn (Backend Server):
EOF
ps aux 2>/dev/null | grep uvicorn | grep -v grep >> "$OUTPUT_FILE" || echo "Not running" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

Python Processes:
EOF
ps aux 2>/dev/null | grep python | grep -v grep | head -10 >> "$OUTPUT_FILE" || echo "No Python processes found" >> "$OUTPUT_FILE"

################################################################################
# SECTION 11: KEY FILE CONTENTS
################################################################################
echo -e "${GREEN}[EXTRA] Extracting Key File Information...${NC}"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
11. KEY FILE INFORMATION
================================================================================

main.py:
  Lines: $(wc -l < main.py 2>/dev/null || echo "N/A")
  First 10 lines (imports):
EOF
if [ -f "main.py" ]; then
    head -10 main.py 2>/dev/null | sed 's/^/    /' >> "$OUTPUT_FILE"
else
    echo "    File not accessible" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

requirements.txt:
EOF
if [ -f "requirements.txt" ]; then
    cat requirements.txt 2>/dev/null | sed 's/^/  /' >> "$OUTPUT_FILE"
else
    echo "  File not found" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

schemas.py (Models):
EOF
if [ -f "schemas.py" ]; then
    grep -E "^class.*\(BaseModel\)" schemas.py 2>/dev/null | sed 's/^/  /' >> "$OUTPUT_FILE" || echo "  No models found" >> "$OUTPUT_FILE"
else
    echo "  File not accessible" >> "$OUTPUT_FILE"
fi

################################################################################
# SECTION 12: GIT INFORMATION
################################################################################
echo -e "${GREEN}[EXTRA] Gathering Git Information...${NC}"
cd "$HOME/InsightsLM"
cat >> "$OUTPUT_FILE" << EOF

================================================================================
12. GIT REPOSITORY INFORMATION
================================================================================

Repository Root: $HOME/InsightsLM

Current Branch:
  $(git branch --show-current 2>/dev/null || echo "Not in git repository")

Recent Commits (last 5):
EOF
git log --oneline -5 2>/dev/null | sed 's/^/  /' >> "$OUTPUT_FILE" || echo "  Not in git repository" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

Git Status:
EOF
git status 2>/dev/null | sed 's/^/  /' >> "$OUTPUT_FILE" || echo "  Not in git repository" >> "$OUTPUT_FILE"

################################################################################
# COMPLETION
################################################################################
cat >> "$OUTPUT_FILE" << EOF

================================================================================
END OF BACKEND INFORMATION EXTRACTION
Generated: $(date)
================================================================================
EOF

# Get Windows username from WSL for copy command
WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}✓ Backend information extraction complete!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Output saved to: ${YELLOW}$OUTPUT_FILE${NC}"
echo -e "File size: $(du -h $OUTPUT_FILE | cut -f1)"
echo ""
echo -e "To view: ${YELLOW}cat $OUTPUT_FILE${NC}"
echo -e "To copy to Windows: ${YELLOW}cp $OUTPUT_FILE /mnt/c/Users/$WIN_USER/Downloads/${NC}"
echo ""

# Return the output file path for the master script
echo "$OUTPUT_FILE"
