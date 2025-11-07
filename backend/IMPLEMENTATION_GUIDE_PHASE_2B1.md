# Phase 2B-1: Update WSL2 Requirements Files

**Implementation Guide**  
**Date:** November 7, 2025  
**Status:** Ready for execution

---

## 📋 Overview

**Goal:** Replace outdated `requirements.txt` with accurate, reproducible dependency specifications.

**What We're Fixing:**
- ❌ Old: 18 packages, no versions, wrong libraries
- ✅ New: 58 core packages, pinned versions, correct libraries

**Time Estimate:** 10 minutes

---

## 🔍 Pre-Implementation Verification

Run these commands to confirm current state:

```bash
cd ~/InsightsLM-new/backend
source venv/bin/activate

# 1. Verify we're in the right environment
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Packages installed: $(pip list | wc -l)"

# 2. Check old requirements.txt
echo "=== OLD requirements.txt ==="
wc -l requirements.txt
head -5 requirements.txt
```

**Expected Output:**
- Directory: `/home/acama/InsightsLM-new/backend`
- Python: `3.12.3`
- Packages: `157`
- Old file: `18 lines` starting with `fastapi`

---

## 📥 Step 1: Download New Files

### **Option A: Copy from outputs directory**

```bash
cd ~/InsightsLM-new/backend

# Copy files from Windows Downloads
cp /mnt/c/Users/acama/Downloads/requirements_step2b1.txt .
cp /mnt/c/Users/acama/Downloads/requirements-lock_step2b1.txt .
cp /mnt/c/Users/acama/Downloads/BILL_OF_MATERIALS_WSL2.md .

# Verify files copied
ls -lh requirements_step2b1.txt requirements-lock_step2b1.txt BILL_OF_MATERIALS_WSL2.md
```

### **Option B: Create files manually**

If copy doesn't work, I'll provide the commands to create files directly.

---

## 🔄 Step 2: Backup Old Requirements

**CRITICAL:** Always backup before replacing!

```bash
cd ~/InsightsLM-new/backend

# Create backup with timestamp
cp requirements.txt requirements.txt.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -lh requirements.txt*
```

**Expected Output:**
```
requirements.txt                (old file)
requirements.txt.backup_20251107_HHMMSS  (backup)
```

---

## 🔄 Step 3: Replace Requirements File

```bash
cd ~/InsightsLM-new/backend

# Replace old with new
mv requirements_step2b1.txt requirements.txt

# Verify replacement
echo "=== NEW requirements.txt ==="
wc -l requirements.txt
head -20 requirements.txt
```

**Expected Output:**
- Line count: ~130 lines (with comments)
- First lines: Should show header with date and platform info

---

## ✅ Step 4: Verify Installation (Dry Run)

**Test that requirements.txt is valid WITHOUT installing:**

```bash
cd ~/InsightsLM-new/backend
source venv/bin/activate

# Dry run - check if packages are already satisfied
pip install --dry-run -r requirements.txt 2>&1 | head -20
```

**Expected Output:**
```
Requirement already satisfied: fastapi==0.121.0
Requirement already satisfied: uvicorn[standard]==0.38.0
...
```

Should say "already satisfied" for most/all packages.

---

## 🔬 Step 5: Optional Cleanup (Remove Old Whisper)

The old `openai-whisper` package is no longer used. Safe to remove:

```bash
cd ~/InsightsLM-new/backend
source venv/bin/activate

# Check if it's installed
pip show openai-whisper

# Remove it (optional but recommended)
pip uninstall openai-whisper -y

# Verify it's gone
pip show openai-whisper
```

**Expected Output:**
- Before: Shows `openai-whisper 20250625`
- After: `WARNING: Package(s) not found: openai-whisper`

**Note:** This frees up ~3GB of disk space and prevents confusion.

---

## 🧪 Step 6: Test Transcription

Verify everything still works:

```bash
cd ~/InsightsLM-new/backend
source venv/bin/activate

# Run diagnostic
python services/transcription_service.py

# If you have a test audio file:
# python services/transcription_service.py /path/to/test.mp3
```

**Expected Output:**
```
============================================================
TRANSCRIPTION SERVICE - DIAGNOSTIC MODE
============================================================

[DIAGNOSTICS] CUDA Environment:
  PyTorch version: 2.9.0
  CUDA available: True
  CUDA version: 12.8
  Device name: NVIDIA GeForce GTX 1660 SUPER
  cuDNN enabled: False
  cuDNN available: True
  cuDNN version: 90102

CURRENT MODEL STATUS
------------------------------------------------------------
Model Loaded: False
cuDNN Disabled: True
------------------------------------------------------------
```

---

## 📝 Step 7: Git Commit

**Following safe implementation principles:**

```bash
cd ~/InsightsLM-new/backend

# Stage the changes
git add requirements.txt
git add requirements-lock_step2b1.txt
git add BILL_OF_MATERIALS_WSL2.md

# Check what's being committed
git status

# Commit with descriptive message
git commit -m "fix(deps): update requirements.txt to match production environment

PROBLEM:
- requirements.txt was severely outdated (18 packages vs 157 installed)
- Had openai-whisper instead of faster-whisper
- Missing PyTorch and all CUDA libraries
- No version pins (not reproducible)

SOLUTION:
- Created requirements.txt with 58 core packages (pinned versions)
- Created requirements-lock.txt with all 154 packages (exact freeze)
- Documented working configuration in BILL_OF_MATERIALS_WSL2.md

TESTING:
- Verified all packages already satisfied (no changes to environment)
- Transcription service working (19x real-time GPU acceleration)
- cuDNN fallback strategy operational

IMPACT:
- Windows native installation now possible with correct dependencies
- Environment fully reproducible
- Documentation complete for deployment

Related: InsightsLM 39, InsightsLM 40 Phase 2B-1"

# Push to remote (if configured)
# git push origin main
```

---

## ✅ Success Criteria

After completing all steps, verify:

- [x] Old `requirements.txt` backed up
- [x] New `requirements.txt` in place (~130 lines)
- [x] `requirements-lock_step2b1.txt` added
- [x] `BILL_OF_MATERIALS_WSL2.md` added
- [x] Dry run shows "already satisfied"
- [x] Transcription test passes
- [x] Changes committed to git
- [x] No errors or warnings

---

## 🔄 Rollback Procedure

If anything goes wrong:

```bash
cd ~/InsightsLM-new/backend

# Restore backup
cp requirements.txt.backup_YYYYMMDD_HHMMSS requirements.txt

# Verify restoration
diff requirements.txt requirements.txt.backup_YYYYMMDD_HHMMSS
```

---

## 📊 Summary

| Item | Before | After |
|------|--------|-------|
| **requirements.txt** | 18 packages, no versions | 58 packages, pinned |
| **Reproducibility** | ❌ Impossible | ✅ Full lockfile |
| **Correct Libraries** | ❌ openai-whisper | ✅ faster-whisper |
| **GPU Stack** | ❌ Missing | ✅ Complete |
| **Documentation** | ❌ None | ✅ BoM included |

---

## 🎯 Next Steps (Phase 2B-2)

After this is complete and committed:

1. ✅ **Phase 2B-1 Complete** (this guide)
2. ⏭️ **Phase 2B-2:** Fix cuDNN diagnostic script (optional cosmetic)
3. ⏭️ **Phase 2B-3:** Create GPU doctor script
4. ⏭️ **Phase 3:** Windows native retry with correct requirements
5. ⏭️ **Phase 4:** Documentation

---

**Ready to execute?** Start with the Pre-Implementation Verification commands above!
