# 📖 GUIDE: GENERATING APPLICATION STRUCTURE INFORMATION

**Purpose:** This guide provides step-by-step instructions for gathering comprehensive application structure information to share with Claude AI for informed development assistance.

**Use Case:** When starting a new chat session, after major changes, or when Claude needs current application context.

---

## **PART 1: GATHERING THE INFORMATION**

### **Step 1: Open Two Terminals**

- **Terminal 1:** WSL2 Ubuntu (Backend)
- **Terminal 2:** Windows PowerShell (Frontend)

---

### **Step 2: Execute Backend Commands**

Copy and paste these commands **one by one** in your **WSL2 Ubuntu terminal:**

```bash
# Navigate to backend directory
cd ~/InsightsLM/backend

# Show directory structure (exclude unnecessary files)
tree -L 2 -I 'venv|__pycache__|*.pyc|chroma_db'

# List service files with details
ls -lh services/

# Check if backend is running
ps aux | grep uvicorn

# Activate virtual environment
source venv/bin/activate

# Check Python version
python3 --version

# List installed key packages
pip list | grep -E "fastapi|whisper|chromadb|sqlalchemy|openai|anthropic|google"

# Verify core imports work
python3 -c "import fastapi, whisper, chromadb, sqlalchemy; print('All core imports successful')"
```

**💡 Tip:** Keep the terminal visible or save all output to a text file.

---

### **Step 3: Execute Frontend Commands**

Copy and paste these commands **one by one** in your **Windows PowerShell terminal:**

```powershell
# Navigate to frontend directory
cd C:\Users\$env:USERNAME\Projects\InsightsLM\frontend

# Show source directory structure
tree /F src

# Check git status
git status

# List key package versions
npm list react electron typescript vite --depth=0

# Show package.json relevant lines
Get-Content package.json | Select-String -Pattern "react|electron|typescript|vite" -Context 0,1

# Check if Electron app is running
Get-Process | Where-Object {$_.ProcessName -like "*electron*"}
```

**💡 Tip:** Keep the terminal visible or save all output to a text file.

---

## **PART 2: REQUESTING THE COMPREHENSIVE SUMMARY**

Once you have all the command outputs, use this prompt template:

---

### **📋 PROMPT TEMPLATE:**

```
I need you to generate a comprehensive application structure summary for InsightsLM. 

Below are the outputs from the commands I just executed:

---
BACKEND TERMINAL (WSL2 Ubuntu):
---

[PASTE ALL BACKEND COMMAND OUTPUTS HERE]

---
FRONTEND TERMINAL (Windows PowerShell):
---

[PASTE ALL FRONTEND COMMAND OUTPUTS HERE]

---

Based on this information, please provide a comprehensive application structure summary that includes:

1. **Architecture Overview** - Backend/Frontend technologies and communication
2. **Backend Structure** - Directory layout, core files, services
3. **Frontend Structure** - Directory layout, core files, components
4. **Key Dependencies** - Verified versions from the outputs
5. **API Endpoints** - Available routes and their purposes
6. **Database & Storage** - Data location and schema
7. **AI Model Integration** - Available LLM providers and models
8. **Current State** - What's running, what's not, recent work

Format it clearly with sections and code blocks for easy reference.
```

---

## **PART 3: QUICK REFERENCE COMMANDS**

### **One-Line Command Strings (For Easy Copy-Paste)**

**Backend (all commands in sequence):**
```bash
cd ~/InsightsLM/backend && tree -L 2 -I 'venv|__pycache__|*.pyc|chroma_db' && ls -lh services/ && ps aux | grep uvicorn && source venv/bin/activate && python3 --version && pip list | grep -E "fastapi|whisper|chromadb|sqlalchemy|openai|anthropic|google" && python3 -c "import fastapi, whisper, chromadb, sqlalchemy; print('All core imports successful')"
```

**Frontend (all commands in sequence):**
```powershell
cd C:\Users\$env:USERNAME\Projects\InsightsLM\frontend; tree /F src; git status; npm list react electron typescript vite --depth=0; Get-Content package.json | Select-String -Pattern "react|electron|typescript|vite" -Context 0,1; Get-Process | Where-Object {$_.ProcessName -like "*electron*"}
```

---

## **PART 4: WHEN TO USE THIS GUIDE**

Use this guide when:

✅ **Starting a new chat session** - To give Claude fresh context  
✅ **After major structural changes** - New services, dependencies, or reorganization  
✅ **After a long break** - To refresh both your and Claude's understanding  
✅ **Before modifying features** - To ensure Claude has accurate current state  
✅ **When debugging** - To verify what's installed and running  
✅ **When onboarding** - To document the current application state  

---

## **PART 5: SAVING THIS GUIDE**

**Recommended location:**
```
~/InsightsLM/docs/APPLICATION_STRUCTURE_GUIDE.md
```

Or keep it in your project documentation folder for easy access.

---

## **💡 PRO TIP: AUTOMATION SCRIPTS**

Create scripts to automate the command execution and save outputs for both backend and frontend:

### **Backend Script**

**File:** `~/InsightsLM/backend/get_info.sh`

```bash
#!/bin/bash
cd ~/InsightsLM/backend
echo "=== BACKEND STRUCTURE ===" > /tmp/backend_info.txt
tree -L 2 -I 'venv|__pycache__|*.pyc|chroma_db' >> /tmp/backend_info.txt
echo -e "\n=== SERVICES ===" >> /tmp/backend_info.txt
ls -lh services/ >> /tmp/backend_info.txt
echo -e "\n=== RUNNING PROCESSES ===" >> /tmp/backend_info.txt
ps aux | grep uvicorn >> /tmp/backend_info.txt
source venv/bin/activate
echo -e "\n=== PYTHON VERSION ===" >> /tmp/backend_info.txt
python3 --version >> /tmp/backend_info.txt
echo -e "\n=== KEY PACKAGES ===" >> /tmp/backend_info.txt
pip list | grep -E "fastapi|whisper|chromadb|sqlalchemy|openai|anthropic|google" >> /tmp/backend_info.txt
echo -e "\n=== IMPORT TEST ===" >> /tmp/backend_info.txt
python3 -c "import fastapi, whisper, chromadb, sqlalchemy; print('All core imports successful')" >> /tmp/backend_info.txt
cat /tmp/backend_info.txt
```

**Make executable:**
```bash
chmod +x ~/InsightsLM/backend/get_info.sh
```

**Run it:**
```bash
cd ~/InsightsLM/backend
./get_info.sh
```

---

### **Frontend Script**

**File:** `C:\Users\%USERNAME%\Projects\InsightsLM\frontend\get_info.ps1`

```powershell
# Frontend Information Gathering Script
Set-Location "C:\Users\$env:USERNAME\Projects\InsightsLM\frontend"

$outputFile = "$env:TEMP\frontend_info.txt"

# Clear previous output
Clear-Content -Path $outputFile -ErrorAction SilentlyContinue

"=== FRONTEND STRUCTURE ===" | Out-File -FilePath $outputFile
tree /F src | Out-File -FilePath $outputFile -Append

"`n=== GIT STATUS ===" | Out-File -FilePath $outputFile -Append
git status | Out-File -FilePath $outputFile -Append

"`n=== KEY PACKAGE VERSIONS ===" | Out-File -FilePath $outputFile -Append
npm list react electron typescript vite --depth=0 | Out-File -FilePath $outputFile -Append

"`n=== PACKAGE.JSON DETAILS ===" | Out-File -FilePath $outputFile -Append
Get-Content package.json | Select-String -Pattern "react|electron|typescript|vite" -Context 0,1 | Out-File -FilePath $outputFile -Append

"`n=== RUNNING PROCESSES ===" | Out-File -FilePath $outputFile -Append
$electronProcess = Get-Process | Where-Object {$_.ProcessName -like "*electron*"}
if ($electronProcess) {
    $electronProcess | Out-File -FilePath $outputFile -Append
} else {
    "No Electron process running" | Out-File -FilePath $outputFile -Append
}

# Display the results
Get-Content $outputFile
Write-Host "`nOutput saved to: $outputFile" -ForegroundColor Green
```

**Run it:**
```powershell
cd C:\Users\$env:USERNAME\Projects\InsightsLM\frontend
.\get_info.ps1
```

**Note:** If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### **💡 BONUS: Combined Output Script**

For maximum efficiency, create a script that gathers BOTH backend and frontend info and combines them:

**File:** `~/InsightsLM/get_full_info.sh`

```bash
#!/bin/bash
echo "========================================="
echo "  GATHERING INSIGHTSLM STRUCTURE INFO"
echo "========================================="

# Get Windows username from WSL
WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')

# Get backend info
echo -e "\n📊 Gathering Backend Info..."
cd ~/InsightsLM/backend
source venv/bin/activate

echo "=== BACKEND TERMINAL (WSL2 Ubuntu) ===" > /tmp/full_info.txt
echo "---" >> /tmp/full_info.txt
tree -L 2 -I 'venv|__pycache__|*.pyc|chroma_db' >> /tmp/full_info.txt
echo -e "\n" >> /tmp/full_info.txt
ls -lh services/ >> /tmp/full_info.txt
echo -e "\n" >> /tmp/full_info.txt
ps aux | grep uvicorn >> /tmp/full_info.txt
echo -e "\n" >> /tmp/full_info.txt
python3 --version >> /tmp/full_info.txt
echo -e "\n" >> /tmp/full_info.txt
pip list | grep -E "fastapi|whisper|chromadb|sqlalchemy|openai|anthropic|google" >> /tmp/full_info.txt
echo -e "\n" >> /tmp/full_info.txt
python3 -c "import fastapi, whisper, chromadb, sqlalchemy; print('All core imports successful')" >> /tmp/full_info.txt

# Get frontend info via PowerShell
echo -e "\n✅ Backend info collected!"
echo "📊 Gathering Frontend Info..."
echo -e "\n\n=== FRONTEND TERMINAL (Windows PowerShell) ===" >> /tmp/full_info.txt
echo "---" >> /tmp/full_info.txt

# Execute PowerShell commands from WSL
powershell.exe -Command "cd C:\Users\$env:USERNAME\Projects\InsightsLM\frontend; tree /F src; git status; npm list react electron typescript vite --depth=0; Get-Content package.json | Select-String -Pattern 'react|electron|typescript|vite' -Context 0,1; Get-Process | Where-Object {\$_.ProcessName -like '*electron*'}" >> /tmp/full_info.txt 2>&1

echo "✅ Frontend info collected!"
echo -e "\n========================================="
echo "  COMPLETE INFO GATHERED"
echo "========================================="

# Display results
cat /tmp/full_info.txt

# Also save to a sharable location
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE=~/InsightsLM/structure_info_${TIMESTAMP}.txt
cp /tmp/full_info.txt "$OUTPUT_FILE"
echo -e "\n📁 Full output saved to: $OUTPUT_FILE"
```

**Make executable and run:**
```bash
chmod +x ~/InsightsLM/get_full_info.sh
cd ~/InsightsLM
./get_full_info.sh
```

**This single script gathers BOTH backend and frontend information in one go!**

---

## **SUMMARY**

This guide provides three approaches to gathering application structure information:

1. **Manual Approach** (Part 1-3): Run commands manually in both terminals
2. **Semi-Automated** (Pro Tips): Use separate scripts for backend and frontend
3. **Fully Automated** (Bonus): Use the combined script to gather everything at once

Choose the approach that best fits your workflow. The combined script (`get_full_info.sh`) is the most efficient for regular use.

---

## **QUICK START CHECKLIST**

- [ ] Save this guide to `~/InsightsLM/docs/APPLICATION_STRUCTURE_GUIDE.md`
- [ ] Create backend script: `~/InsightsLM/backend/get_info.sh`
- [ ] Create frontend script: `C:\Users\%USERNAME%\Projects\InsightsLM\frontend\get_info.ps1`
- [ ] Create combined script: `~/InsightsLM/get_full_info.sh`
- [ ] Make scripts executable: `chmod +x *.sh`
- [ ] Test the combined script: `./get_full_info.sh`
- [ ] Bookmark this guide for future reference

---

**Last Updated:** October 24, 2025  
**Version:** 1.0  
**Project:** InsightsLM  
**Author:** Development Team
