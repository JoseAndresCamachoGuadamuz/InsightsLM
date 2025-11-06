# Setup Guide

**InsightsLM Installation and Configuration Guide**

**Version:** 1.1 (Updated with actual system requirements)  
**Last Updated:** November 4, 2025  
**Estimated Setup Time:** 30-45 minutes

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Backend Setup (WSL2/Linux)](#backend-setup-wsl2linux)
4. [Frontend Setup (Windows)](#frontend-setup-windows)
5. [First Run](#first-run)
6. [Configuration](#configuration)
7. [GPU Setup (Optional)](#gpu-setup-optional)
8. [Troubleshooting](#troubleshooting)
9. [Verification](#verification)
10. [Next Steps](#next-steps)
11. [Additional Resources](#additional-resources)
12. [Getting Help](#getting-help)

---

## 💻 System Requirements

### Minimum Requirements

**Hardware:**
- **CPU:** Intel/AMD quad-core processor (2.5 GHz+)
- **RAM:** 8 GB (16 GB recommended for GPU acceleration)
- **Storage:** 10 GB free space (5 GB for Whisper model + application)
- **GPU:** (Optional) NVIDIA GPU with 4+ GB VRAM for faster transcription

**Operating System:**
- **Windows:** Windows 10 Pro/Enterprise (64-bit) or Windows 11
- **WSL Version:** WSL2 with Ubuntu 24.04 LTS
- **Kernel:** Linux kernel 6.6+ (WSL2)

### Recommended Configuration

**Hardware:**
- **CPU:** Intel Core i7/AMD Ryzen 7 or better
- **RAM:** 16 GB or more
- **Storage:** SSD with 20+ GB free space
- **GPU:** NVIDIA RTX 3060 or better (for 30x real-time transcription)

**Network:**
- Internet connection required for:
  - Initial setup and package downloads
  - AI provider API calls (except Ollama)
  - Software updates

---

## 📦 Prerequisites

### 1. Windows Subsystem for Linux (WSL2)

**Check if WSL2 is installed:**
```powershell
wsl --version
```

**If not installed, install WSL2:**
```powershell
# Run as Administrator
wsl --install
# Restart your computer
```

**Install Ubuntu 24.04:**
```powershell
wsl --install -d Ubuntu-24.04
```

**Verify WSL2:**
```powershell
wsl --list --verbose
# Should show Ubuntu-24.04 with VERSION 2
```

**Update WSL2 kernel:**
```powershell
wsl --update
```

---

### 2. Node.js and npm (Windows)

**Required Versions:**
- Node.js: **v22.17.1** or higher
- npm: **11.6.2** or higher

**Download and install:**
1. Visit: https://nodejs.org/
2. Download LTS version (v22.17.1 or later)
3. Run installer with default options
4. Restart terminal

**Verify installation:**
```powershell
node --version  # Should show v22.17.1 or higher
npm --version   # Should show 11.6.2 or higher
```

---

### 3. Python (WSL2)

**Required Version:** Python **3.12.3** or higher

**Install Python in WSL2:**
```bash
# Open WSL2 terminal
wsl

# Update package lists
sudo apt update
sudo apt upgrade -y

# Install Python 3.12+
sudo apt install python3 python3-pip python3-venv -y

# Verify installation
python3 --version  # Should show Python 3.12.3 or higher
pip3 --version     # Should show pip 24.0 or higher
```

---

### 4. ffmpeg (WSL2)

**Required for audio processing**

```bash
# In WSL2
sudo apt install ffmpeg -y

# Verify installation
ffmpeg -version
```

---

### 5. Git (Both Environments)

**Windows:**
```powershell
# Download from https://git-scm.com/download/win
# Or use winget:
winget install Git.Git
```

**WSL2:**
```bash
sudo apt install git -y
```

**Verify:**
```bash
git --version
```

---

## 🐧 Backend Setup (WSL2/Linux)

### Step 1: Clone Repository

```bash
# In WSL2 terminal
cd ~
git clone https://github.com/yourusername/InsightsLM.git
cd InsightsLM/backend
```

---

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Verify activation (should show (venv) prefix)
which python  # Should point to venv/bin/python
```

---

### Step 3: Install Dependencies

**Install from requirements.txt:**

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies (this may take 10-15 minutes)
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|whisper|chromadb"
```

**Expected key packages:**
- `fastapi==0.118.3`
- `openai-whisper==20250625`
- `chromadb==1.1.1`
- `sqlalchemy==2.0.44`
- `anthropic==0.69.0`
- `openai==2.3.0`
- `google-generativeai==0.8.5`
- `ollama==0.6.0`
- `pycryptodome==3.23.0`

---

### Step 4: Download Whisper Model

The Whisper model will download automatically on first transcription, but you can pre-download it:

```bash
# Activate venv if not already active
source venv/bin/activate

# Test Whisper installation and download model
python3 -c "import whisper; whisper.load_model('large-v3')"
```

**Model download:**
- Size: ~3 GB
- Location: `~/.cache/whisper/large-v3.pt`
- Time: 5-10 minutes depending on internet speed

---

### Step 5: Initialize Database

```bash
# Create data directory
mkdir -p ~/.local/share/InsightsLM

# Start backend once to initialize database
uvicorn main:app --host 0.0.0.0 --port 8000

# Press Ctrl+C after you see "Application startup complete"
```

**Created files:**
- `~/.local/share/InsightsLM/insightslm.db` (SQLite database)
- `~/.local/share/InsightsLM/chroma_db/` (Vector database)
- `~/.local/share/InsightsLM/temp_uploads/` (Temporary file storage)

---

### Step 6: Test Backend

```bash
# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000

# In a new terminal, test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

**Keep this terminal open** - the backend needs to run while using the app.

---

## 🪟 Frontend Setup (Windows)

### Step 1: Navigate to Frontend Directory

```powershell
# In Windows PowerShell or Command Prompt
cd C:\Users\<your-username>\Projects\InsightsLM\frontend

# Or clone if needed:
# git clone https://github.com/yourusername/InsightsLM.git
# cd InsightsLM\frontend
```

---

### Step 2: Install Dependencies

```powershell
# Install all npm packages (takes 3-5 minutes)
npm install

# Verify key packages
npm list react electron typescript
```

**Expected versions:**
- `react@19.2.0`
- `electron@38.2.2`
- `typescript@4.5.5`
- `vite@5.4.21`
- `axios@1.12.2`

---

### Step 3: Build Configuration

**Verify configuration files exist:**
```powershell
dir vite.*.config.mjs
dir forge.config.mjs
dir tsconfig.json
```

**Files should include:**
- `vite.main.config.mjs` - Main process build config
- `vite.preload.config.mjs` - Preload script config
- `vite.renderer.config.mjs` - Renderer process (React) config
- `forge.config.mjs` - Electron Forge packaging config
- `tsconfig.json` - TypeScript configuration

---

### Step 4: Test Frontend

```powershell
# Start in development mode
npm start
```

**Expected behavior:**
1. Vite builds the application (~10 seconds)
2. Electron window opens
3. Backend auto-starts in WSL2
4. Health check succeeds
5. Application UI appears

**If errors occur**, see [Troubleshooting](#troubleshooting) section.

---

## 🎯 First Run

### 1. Launch Application

**Method 1: npm start (Development)**
```powershell
cd C:\Users\<your-username>\Projects\InsightsLM\frontend
npm start
```

**Method 2: Built Application (Production)**
```powershell
# Build first
npm run make

# Then run the installer from out/make/
```

---

### 2. Configure AI Providers

**First-time setup wizard:**

1. **Application opens** → Shows settings panel
2. **Choose default provider:**
   - **Ollama** (recommended for free/private use)
   - OpenAI (requires API key)
   - Anthropic (requires API key)
   - Google Gemini (requires API key)

---

### 3. Ollama Setup (Recommended Free Option)

**Install Ollama:**
```powershell
# Download from https://ollama.com/download
# Or use winget:
winget install Ollama.Ollama
```

**Pull a model:**
```bash
# In WSL2 or Windows terminal
ollama pull llama3.2
ollama pull qwen2.5:latest
```

**Test Ollama:**
```bash
ollama list  # Should show downloaded models
```

**In InsightsLM:**
- Settings → Ollama Base URL: `http://localhost:11434`
- Test Connection → Should show "✓ Available"
- Select model from dropdown

---

### 4. OpenAI Setup (Optional)

**Get API Key:**
1. Visit: https://platform.openai.com/api-keys
2. Create new API key
3. Copy key (starts with `sk-proj-...`)

**In InsightsLM:**
- Settings → OpenAI API Key: Paste your key
- Test Connection
- Select model (recommended: `gpt-4o` or `gpt-4o-mini`)

---

### 5. Anthropic Setup (Optional)

**Get API Key:**
1. Visit: https://console.anthropic.com/
2. Create new API key
3. Copy key (starts with `sk-ant-...`)

**In InsightsLM:**
- Settings → Anthropic API Key: Paste your key
- Test Connection
- Select model (recommended: `claude-sonnet-4`)

---

### 6. Google Gemini Setup (Optional)

**Get API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy key

**In InsightsLM:**
- Settings → Google API Key: Paste your key
- Test Connection
- Select model (recommended: `gemini-1.5-pro`)

---

## ⚙️ Configuration

### Application Configuration

**Config file location:**
```
~/.local/share/InsightsLM/config.json
```

**Configuration is managed through the UI Settings panel.**

**Manual edit (if needed):**
```bash
# In WSL2
cd ~/.local/share/InsightsLM
nano config.json  # Or use your preferred editor
```

**Config schema:**
```json
{
  "ollama_base_url": "http://localhost:11434",
  "ollama_api_key_encrypted": "[ENCRYPTED]",
  "openai_api_key_encrypted": "[ENCRYPTED]",
  "openai_model": "gpt-4o",
  "anthropic_api_key_encrypted": "[ENCRYPTED]",
  "anthropic_model": "claude-sonnet-4",
  "google_api_key_encrypted": "[ENCRYPTED]",
  "google_model": "gemini-1.5-pro",
  "default_provider": "ollama",
  "whisper_model": "large-v3",
  "language": "auto"
}
```

**Note:** API keys are automatically encrypted with AES-256. Never share this file.

---

### Database Locations

**SQLite Database:**
```
~/.local/share/InsightsLM/insightslm.db
```

**Vector Database (ChromaDB):**
```
~/.local/share/InsightsLM/chroma_db/
```

**Temp Uploads:**
```
~/.local/share/InsightsLM/temp_uploads/
```

---

## 🚀 GPU Setup (Optional)

**For 30x faster transcription with NVIDIA GPUs**

### Prerequisites

- NVIDIA GPU with 4+ GB VRAM
- Windows NVIDIA drivers installed
- CUDA Toolkit 12.6+ installed

---

### Step 1: Install CUDA Toolkit (Windows)

**Download:**
- Visit: https://developer.nvidia.com/cuda-downloads
- Download CUDA Toolkit 12.6 or later
- Install with default options

**Verify:**
```powershell
nvcc --version
nvidia-smi
```

---

### Step 2: Install cuDNN (Windows)

**Download:**
- Visit: https://developer.nvidia.com/cudnn
- Download cuDNN 9.5+ for CUDA 12.6
- Extract to CUDA installation directory

---

### Step 3: Install PyTorch with CUDA (WSL2)

```bash
# In WSL2, with venv activated
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA is available
python3 -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

---

### Step 4: Test GPU Transcription

```bash
# Start backend with GPU
uvicorn main:app --host 0.0.0.0 --port 8000

# Upload a test file through the UI
# Check backend terminal for GPU usage
```

**Expected speed:**
- **CPU only:** 1x real-time (5-minute audio = 5 minutes to transcribe)
- **With GPU:** 30x real-time (5-minute audio = 10 seconds to transcribe)

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Backend not responding" / Health check fails

**Symptoms:**
- Application shows "Waiting for backend..."
- Frontend can't connect to backend

**Solutions:**

```bash
# Check if backend is running
# In WSL2:
ps aux | grep uvicorn

# If not running, start it manually:
cd ~/InsightsLM/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# Check if port 8000 is in use:
netstat -tuln | grep 8000

# If port is in use by another process:
kill <pid>
```

---

#### 2. "Address already in use" (Port 8000)

**Symptoms:**
- Error: `OSError: [Errno 98] Address already in use`

**Solutions:**

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port:
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

#### 3. Whisper model fails to download

**Symptoms:**
- Error downloading model
- Transcription fails with "Model not found"

**Solutions:**

```bash
# Download manually
cd ~/.cache/whisper
wget https://openaipublic.azureedge.net/main/whisper/models/large-v3.pt

# Or clear cache and retry:
rm -rf ~/.cache/whisper
python3 -c "import whisper; whisper.load_model('large-v3')"
```

---

#### 4. "ModuleNotFoundError" errors

**Symptoms:**
- Python import errors
- Missing package errors

**Solutions:**

```bash
# Ensure venv is activated
source ~/InsightsLM/backend/venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check installed packages
pip list
```

---

#### 5. Ollama not connecting

**Symptoms:**
- "Ollama unavailable" error
- No models shown

**Solutions:**

```bash
# Check if Ollama is running
ollama list

# If not running, start Ollama:
# Windows: Open Ollama app
# WSL2: Start Ollama service

# Test connection:
curl http://localhost:11434/api/tags

# Verify WSL2 can access Windows Ollama:
curl http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):11434/api/tags
```

---

#### 6. React/npm errors

**Symptoms:**
- Frontend build fails
- Module not found errors

**Solutions:**

```powershell
# Delete node_modules and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm install

# Clear npm cache if still failing
npm cache clean --force
npm install
```

---

#### 7. GPU not being used (slow transcription)

**Symptoms:**
- Transcription is slow (CPU speed)
- `torch.cuda.is_available()` returns False

**Solutions:**

```bash
# Verify CUDA installation
python3 -c "import torch; print(torch.cuda.is_available())"
python3 -c "import torch; print(torch.version.cuda)"

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Check NVIDIA driver
nvidia-smi
```

---

## ✅ Verification

### Backend Verification

**1. Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

**2. Test API Status:**
```bash
curl http://localhost:8000/test-api/status
# Expected: JSON with all provider statuses
```

**3. List Models:**
```bash
curl http://localhost:8000/models/all
# Expected: List of 104+ models
```

---

### Frontend Verification

**1. Launch application:**
```powershell
npm start
```

**2. Check for:**
- ✅ Electron window opens
- ✅ Backend starts automatically
- ✅ UI loads without errors
- ✅ Settings panel is accessible

---

### Full System Test

**Complete workflow test:**

1. **Upload audio file**
   - Settings → Upload File
   - Select test audio file (MP3/WAV)
   - Wait for transcription

2. **Verify transcription**
   - Transcript appears with timestamps
   - Segments are clickable

3. **Test AI analysis**
   - Click "Summarize"
   - Select model
   - Generate summary

4. **Test export**
   - Export → Select format (TXT/DOCX/PDF)
   - Verify file downloads

---

## 🎓 Next Steps

After successful setup:

1. **Read the User Guide:** [USER_GUIDE.md](./USER_GUIDE.md)
2. **Explore templates:** Create custom report templates
3. **Try different models:** Compare AI providers
4. **Configure settings:** Optimize for your use case
5. **Join the community:** Share feedback and improvements

---

## 📚 Additional Resources

- **User Guide:** [USER_GUIDE.md](./USER_GUIDE.md)
- **API Documentation:** [API_REFERENCE.md](./API_REFERENCE.md)
- **Architecture:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)
- **GitHub Issues:** [Report bugs or request features](https://github.com/yourusername/InsightsLM/issues)

---

## 🆘 Getting Help

**If you're still having issues:**

1. Check [GitHub Issues](https://github.com/yourusername/InsightsLM/issues)
2. Search [GitHub Discussions](https://github.com/yourusername/InsightsLM/discussions)
3. Create a new issue with:
   - Your system information
   - Error messages (full text)
   - Steps to reproduce
   - Logs from backend terminal

---

**Version:** 1.1  
**Last Updated:** November 4, 2025  
**Status:** ✅ Verified - Updated with actual system requirements (Python 3.12.3, Node.js 22.17.1, React 19.2.0)
