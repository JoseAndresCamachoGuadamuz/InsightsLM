# InsightsLM WSL2 Backend - Bill of Materials (BoM)

**Document Version:** 1.0  
**Date:** November 7, 2025  
**Status:** ✅ Production-Ready (Tested & Verified)

---

## 🖥️ System Configuration

### **Hardware**
- **CPU:** AMD Ryzen 9 (20 cores) @ FalconXtreme
- **GPU:** NVIDIA GeForce GTX 1660 SUPER (6GB VRAM)
- **RAM:** 32GB+ (recommended 8GB+ minimum)
- **Storage:** 20GB+ free space (for models and data)

### **Operating System**
- **Platform:** WSL2 Ubuntu 24.04
- **Kernel:** Linux 5.15+
- **Host OS:** Windows 11
- **NVIDIA Driver:** 535+ (Windows host driver, shared with WSL2)

### **Python Environment**
- **Python Version:** 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]
- **pip Version:** 25.3
- **Virtual Environment:** venv (standard library)
- **Total Packages:** 157 installed

---

## 🚀 Core Technology Stack

### **Web Framework**
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.121.0 | REST API framework |
| uvicorn | 0.38.0 | ASGI server |
| starlette | 0.49.3 | Web toolkit |

### **Audio Processing**
| Package | Version | Purpose |
|---------|---------|---------|
| faster-whisper | 1.2.1 | GPU-accelerated transcription |
| ctranslate2 | 4.6.0 | Efficient inference engine |
| ffmpeg-python | 0.2.0 | Audio format conversion |
| yt-dlp | 2025.10.22 | Audio download from URLs |

### **GPU Acceleration (CUDA 12.8)**
| Package | Version | Purpose |
|---------|---------|---------|
| torch | 2.9.0 | PyTorch framework |
| nvidia-cudnn-cu12 | 9.10.2.21 | cuDNN library |
| nvidia-cublas-cu12 | 12.8.4.1 | CUDA BLAS |
| nvidia-cuda-runtime-cu12 | 12.8.90 | CUDA runtime |
| *+ 11 more nvidia packages* | Various | GPU compute libraries |

### **AI/LLM Providers**
| Package | Version | Purpose |
|---------|---------|---------|
| openai | 2.7.1 | OpenAI API client |
| anthropic | 0.72.0 | Anthropic API client |
| google-generativeai | 0.8.5 | Google Gemini client |
| ollama | 0.6.0 | Local LLM client |

### **Database & Vector Store**
| Package | Version | Purpose |
|---------|---------|---------|
| sqlalchemy | 2.0.44 | SQL ORM |
| chromadb | 1.3.4 | Vector database |
| sentence-transformers | 5.1.2 | Embeddings model |

---

## ⚡ Performance Metrics

### **Transcription Performance (GPU-Accelerated)**
- **Speed:** ~19x real-time
- **Benchmark:** 16-minute audio → 52 seconds processing
- **Model:** small (244M parameters)
- **Compute Type:** int8_float32
- **Device:** CUDA (cuDNN disabled for stability)

### **Model Specifications**
| Model Size | Parameters | RAM Required | Use Case |
|------------|-----------|--------------|----------|
| tiny | 39M | ~1GB | Fast, low accuracy |
| base | 74M | ~1GB | Balanced speed |
| **small** ⭐ | 244M | ~2GB | **Production (current)** |
| medium | 769M | ~5GB | High accuracy |
| large-v3 | 1550M | ~10GB | Best accuracy |

**Current Selection Logic:**
- 6GB GPU → `small` model (conservative for stability)
- Prevents OOM errors on long files
- Can be upgraded to `medium` if needed

---

## 🔧 Critical Configuration

### **Environment Variables**

**LD_LIBRARY_PATH** (Required for cuDNN):
```bash
export LD_LIBRARY_PATH="/home/acama/InsightsLM-new/backend/venv/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
```
- **Location:** `~/.bashrc`
- **Purpose:** Load cuDNN library from pip package
- **Persistence:** Persists across reboots ✅

**CUDA_MODULE_LOADING** (Set by code):
```python
os.environ["CUDA_MODULE_LOADING"] = "LAZY"
```
- **Purpose:** Lazy-load CUDA modules to prevent crashes
- **Location:** `transcription_service.py` line 15

### **cuDNN Configuration**
```python
torch.backends.cudnn.enabled = False
torch.backends.cudnn.benchmark = False
```
- **Reason:** Prevents symbol lookup crashes when cuDNN not system-installed
- **Impact:** Minimal performance difference (~5%)
- **Stability:** Prevents random crashes ✅

### **Fallback Strategy**
1. **Attempt 1:** CUDA with cuDNN disabled (int8_float32)
2. **Attempt 2:** CPU with int8 (if GPU fails)
3. **Runtime Fallback:** CPU without VAD (if cuDNN error during transcription)

---

## 📦 Package Organization

### **Direct Dependencies** (58 core packages)
- Explicitly required by application code
- Listed in `requirements_step2b1.txt`

### **Transitive Dependencies** (96 packages)
- Automatically installed by pip
- Required by direct dependencies
- All captured in `requirements-lock_step2b1.txt`

### **Legacy Packages** (to be removed)
- `openai-whisper==20250625` - NOT used, can be uninstalled
- Application uses `faster-whisper` instead

---

## 🔍 Verification Commands

### **Check Python Version**
```bash
python3 --version
# Expected: Python 3.12.3
```

### **Check CUDA Availability**
```bash
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
# Expected: CUDA: True
```

### **Check GPU Info**
```bash
python3 -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
# Expected: GPU: NVIDIA GeForce GTX 1660 SUPER
```

### **Check cuDNN Status**
```bash
python3 -c "import torch; print(f'cuDNN enabled: {torch.backends.cudnn.enabled}')"
# Expected: cuDNN enabled: False (intentionally disabled)
```

### **Test Transcription**
```bash
cd ~/InsightsLM-new/backend
source venv/bin/activate
python services/transcription_service.py path/to/audio.mp3
```

---

## 📋 Installation Checklist

- [ ] Ubuntu 24.04 or compatible Linux
- [ ] Python 3.12.3 installed
- [ ] NVIDIA driver 535+ (on Windows host)
- [ ] WSL2 configured with GPU support
- [ ] Virtual environment created
- [ ] pip upgraded to 25.3+
- [ ] Requirements installed from `requirements_step2b1.txt`
- [ ] LD_LIBRARY_PATH set in `~/.bashrc`
- [ ] CUDA verification passed
- [ ] Test transcription successful

---

## 🔐 Security Notes

- **API Keys:** Encrypted with AES-256 (machine-specific)
- **Encryption Key:** Derived from persistent file (not MAC address)
- **Database:** SQLite with write-ahead logging
- **Dependencies:** All pinned to specific versions

---

## 📝 Maintenance Notes

### **Updating Dependencies**
⚠️ **CAUTION:** GPU stack is fragile. Do not update without testing.

**Safe to update:**
- fastapi, uvicorn (web framework)
- openai, anthropic, google-generativeai (API clients)
- sqlalchemy (database)

**DO NOT update without thorough testing:**
- torch (GPU compute)
- nvidia-cudnn-cu12 (critical for GPU)
- faster-whisper (transcription engine)
- ctranslate2 (inference backend)

### **Backup Strategy**
1. Keep `requirements-lock_step2b1.txt` for exact reproduction
2. Test all changes in isolated environment first
3. Document any version changes in this BoM

---

## 🎯 Production Deployment Checklist

- [x] Requirements files created and tested
- [x] GPU acceleration verified (19x speed)
- [x] Fallback strategy implemented (CPU backup)
- [x] LD_LIBRARY_PATH configured
- [x] cuDNN stability fix applied
- [x] Performance benchmarks documented
- [ ] Windows native testing (Phase 3)
- [ ] Full documentation (Phase 4)

---

## 📚 References

- **Requirements (Organized):** `requirements_step2b1.txt`
- **Requirements (Complete Lock):** `requirements-lock_step2b1.txt`
- **Platform Detection:** `platform_utils.py`
- **Transcription Service:** `services/transcription_service.py` (512 lines)
- **CUDA Setup Guide:** [docs/CUDA_SETUP.md] (to be created)

---

**Last Updated:** November 7, 2025  
**Verified By:** Testing on FalconXtreme (GTX 1660 SUPER)  
**Status:** ✅ Production-Ready
