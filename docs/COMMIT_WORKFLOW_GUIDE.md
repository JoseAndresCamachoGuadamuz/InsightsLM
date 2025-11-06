# Git Commit Workflow Guide

**InsightsLM - Hybrid Environment Git Workflow**

**Version:** 1.0 (Generic)  
**Last Updated:** November 4, 2025  
**For:** InsightsLM hybrid Windows/WSL2 development environment

---

## ⚠️ **IMPORTANT: Customize for Your System**

**Before using this guide, replace the following placeholders:**
- `YOUR-USERNAME` → Your actual username (e.g., `john`, `alice`, `dev`)
- `YOUR-HOSTNAME` → Your actual hostname (e.g., `MyPC`, `DevMachine`)

**Example replacements:**
- `/home/YOUR-USERNAME/InsightsLM` → `/home/john/InsightsLM`
- `C:\Users\YOUR-USERNAME\Projects\` → `C:\Users\alice\Projects\`
- `YOUR-USERNAME@YOUR-HOSTNAME` → `john@DevMachine`

**Tip:** Use your editor's Find & Replace function (Ctrl+H) to replace all instances at once.

---


---

## 📋 Table of Contents

1. [IMPORTANT: Customize for Your System](#-important-customize-for-your-system)

2. [Overview](#-overview)
3. [System Setup](#-system-setup)
4. [Commit Strategy](#-commit-strategy)
5. [Step-by-Step Workflow](#-step-by-step-workflow)
6. [Conventional Commits Format](#-conventional-commits-format)
7. [Common Scenarios](#-common-scenarios)
8. [Troubleshooting](#-troubleshooting)
9. [Best Practices](#-best-practices)
10. [Quick Reference](#-quick-reference)
11. [Additional Resources](#-additional-resources)
12. [Getting Help](#-getting-help)

---

## 🎯 Overview

InsightsLM uses a **hybrid development environment** with:
- **Backend** developed in WSL2/Linux (Python/FastAPI)
- **Frontend** developed in Windows (Electron/React/TypeScript)
- **Single Git repository** with separate backend/ and frontend/ directories

This guide documents the proper workflow for committing changes in this dual-environment setup.

---

## 💻 System Setup

### **Git Repository Structure**

```
InsightsLM/
├── .git/                  # Git repository root
├── README.md
├── LICENSE
├── backend/               # Python/FastAPI backend
│   ├── main.py
│   ├── services/
│   ├── database/
│   └── ...
├── frontend/              # Electron/React frontend
│   ├── src/
│   ├── package.json
│   └── ...
└── docs/                  # Documentation
    └── ...
```

---

### **Development Environments**

#### **Backend Environment (WSL2/Linux)**

**Location:** Ubuntu 24.04 LTS on WSL2  
**Current Directory:** `(venv) YOUR-USERNAME@YOUR-HOSTNAME:~/InsightsLM/backend$`  
**Git Root:** `/home/YOUR-USERNAME/InsightsLM`  
**Primary Language:** Python 3.12.3  

**Access:**
```bash
# Open WSL2 terminal
wsl

# Navigate to backend
cd ~/InsightsLM/backend
source venv/bin/activate
```

---

#### **Frontend Environment (Windows)**

**Location:** Windows 10 Pro  
**Current Directory:** `PS C:\Users\YOUR-USERNAME\Projects\InsightsLM\frontend>`  
**Git Root:** `C:\Users\YOUR-USERNAME\Projects\InsightsLM`  
**Primary Language:** TypeScript 4.5.5, React 19.2.0  

**Access:**
```powershell
# Open PowerShell
# Navigate to frontend
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM\frontend
```

---

### **Critical Path Information**

| Environment | Working Dir | Git Root |
|-------------|-------------|----------|
| **Backend (WSL2)** | `~/InsightsLM/backend` | `/home/YOUR-USERNAME/InsightsLM` |
| **Frontend (Windows)** | `C:\Users\YOUR-USERNAME\Projects\InsightsLM\frontend` | `C:\Users\YOUR-USERNAME\Projects\InsightsLM` |

**⚠️ IMPORTANT:** Git commands must be run from the **Git root**, not from backend/ or frontend/ subdirectories.

---

## 🎯 Commit Strategy

### **Core Principles**

1. **Commit backend and frontend SEPARATELY**
2. **Always commit backend FIRST**
3. **Synchronize both systems after each commit**
4. **Use conventional commits format**
5. **Navigate to git root before committing**

---

### **Why Backend First?**

**Reasoning:**
- Backend changes are often dependencies for frontend
- Backend APIs should be stable before frontend integration
- Easier to track which frontend changes correspond to backend changes
- Reduces merge conflicts

---

### **Typical Workflow Pattern**

```
1. Develop backend feature → Commit backend → Push
2. Pull in frontend → Develop frontend feature → Commit frontend → Push
3. Synchronize both environments
```

---

## 📝 Step-by-Step Workflow

### **STEP 1: Gather Current Status**

Before making any commits, check the status in both environments.

#### **Backend Status (WSL2)**

```bash
cd /home/YOUR-USERNAME/InsightsLM
pwd  # Verify you're in git root
git status
git diff --stat
git log --oneline -3
```

**Expected Output:**
```
/home/YOUR-USERNAME/InsightsLM
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   backend/main.py
  modified:   backend/services/llm_service.py

 backend/main.py               | 15 ++++++++++-----
 backend/services/llm_service.py | 23 +++++++++++++++++++----
 2 files changed, 29 insertions(+), 9 deletions(-)
```

---

#### **Frontend Status (Windows)**

```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
pwd  # Verify you're in git root
git status
git diff --stat
git log --oneline -3
```

**Expected Output:**
```
Path: C:\Users\YOUR-USERNAME\Projects\InsightsLM

On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   frontend/src/App.tsx
  modified:   frontend/src/services/api.ts

 frontend/src/App.tsx           | 42 +++++++++++++++++++++++++++++++-------
 frontend/src/services/api.ts   | 18 +++++++++++-----
 2 files changed, 48 insertions(+), 12 deletions(-)
```

---

### **STEP 2: Analyze Changes**

Review the output and categorize changes:

**Backend Changes:**
- Modified files: List all modified files
- Purpose: What was implemented?
- Related to: Which feature/fix?

**Frontend Changes:**
- Modified files: List all modified files
- Purpose: What was implemented?
- Dependencies: Does it depend on backend changes?

---

### **STEP 3: Commit Backend Changes**

#### **3.1 Navigate to Git Root**

```bash
cd /home/YOUR-USERNAME/InsightsLM
```

**⚠️ VERIFY:** Run `pwd` and ensure output is `/home/YOUR-USERNAME/InsightsLM`

---

#### **3.2 Stage Backend Files**

```bash
# Stage specific files (recommended)
git add backend/main.py
git add backend/services/llm_service.py

# OR stage all backend changes (use with caution)
git add backend/
```

**Verify staging:**
```bash
git status
# Should show files in "Changes to be committed"
```

---

#### **3.3 Create Backend Commit**

```bash
git commit -m "feat(backend): add support for new AI provider

- Add provider discovery endpoint
- Update model listing
- Add integration tests"
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

See [Conventional Commits Format](#conventional-commits-format) for details.

---

#### **3.4 Push Backend Commit**

```bash
git push origin main
```

**Expected Output:**
```
Counting objects: 5, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (5/5), done.
Writing objects: 100% (5/5), 1.23 KiB | 1.23 MiB/s, done.
Total 5 (delta 3), reused 0 (delta 0)
To https://github.com/yourusername/InsightsLM.git
   abc1234..def5678  main -> main
```

---

#### **3.5 Return to Working Directory**

```bash
cd backend
# Now back in ~/InsightsLM/backend
```

---

### **STEP 4: Commit Frontend Changes**

#### **4.1 Pull Latest Changes**

**⚠️ CRITICAL:** Always pull before committing frontend to get backend changes

```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git pull origin main
```

**Expected Output:**
```
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 5 (delta 3), reused 0 (delta 0)
Unpacking objects: 100% (5/5), done.
From https://github.com/yourusername/InsightsLM
   abc1234..def5678  main       -> origin/main
Updating abc1234..def5678
Fast-forward
 backend/main.py               | 15 ++++++++++-----
 backend/services/llm_service.py | 23 +++++++++++++++++++----
 2 files changed, 29 insertions(+), 9 deletions(-)
```

**If Merge Editor Opens:**
- This is normal if both environments made commits
- **Action:** Just close the editor (save and exit)
- Git will auto-merge if no conflicts

---

#### **4.2 Navigate to Git Root**

```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
```

**⚠️ VERIFY:** Run `pwd` and ensure output is `C:\Users\YOUR-USERNAME\Projects\InsightsLM`

---

#### **4.3 Stage Frontend Files**

```powershell
# Stage specific files (recommended)
git add frontend/src/App.tsx
git add frontend/src/services/api.ts

# OR stage all frontend changes (use with caution)
git add frontend/
```

**Verify staging:**
```powershell
git status
# Should show files in "Changes to be committed"
```

---

#### **4.4 Create Frontend Commit**

```powershell
git commit -m "feat(frontend): integrate new AI provider in UI

- Add provider selection dropdown
- Update model display
- Add connection testing"
```

---

#### **4.5 Push Frontend Commit**

```powershell
git push origin main
```

**Expected Output:**
```
Counting objects: 7, done.
Delta compression using up to 16 threads.
Compressing objects: 100% (7/7), done.
Writing objects: 100% (7/7), 2.45 KiB | 2.45 MiB/s, done.
Total 7 (delta 5), reused 0 (delta 0)
To https://github.com/yourusername/InsightsLM.git
   def5678..ghi9012  main -> main
```

---

#### **4.6 Return to Working Directory**

```powershell
cd frontend
# Now back in C:\Users\YOUR-USERNAME\Projects\InsightsLM\frontend
```

---

### **STEP 5: Handle package-lock.json (Optional)**

If `package-lock.json` changed due to dependency updates:

**Option A: Commit Separately**
```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git add frontend/package-lock.json
git commit -m "chore(frontend): update package-lock.json"
git push origin main
cd frontend
```

**Option B: Discard Changes**
```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git checkout frontend/package-lock.json
cd frontend
```

**Recommendation:** Commit separately if you intentionally updated dependencies.

---

### **STEP 6: Synchronize Both Systems**

After all commits are pushed, synchronize both environments.

#### **Backend Synchronization (WSL2)**

```bash
cd /home/YOUR-USERNAME/InsightsLM
git pull origin main
git log --oneline -5
git status
```

**Expected Output:**
```
Already up to date.
OR
Updating def5678..ghi9012
Fast-forward
 frontend/src/App.tsx         | 42 ++++++++++++++++++++++++++++
 frontend/src/services/api.ts | 18 +++++++++++
 2 files changed, 60 insertions(+)

ghi9012 feat(frontend): integrate new AI provider in UI
def5678 feat(backend): add support for new AI provider
abc1234 fix(backend): resolve API key encryption issue

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

#### **Frontend Synchronization (Windows)**

```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git log --oneline -5
git status
```

**Expected Output:**
```
ghi9012 feat(frontend): integrate new AI provider in UI
def5678 feat(backend): add support for new AI provider
abc1234 fix(backend): resolve API key encryption issue

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

### **STEP 7: Verify Success**

**✅ Success Indicators:**
- Both systems show the SAME latest commit hash (e.g., `ghi9012`)
- Both show "nothing to commit, working tree clean"
- Both show "Your branch is up to date with 'origin/main'"
- `git log` shows the same recent commits in both environments

**If ANY indicator is missing, see [Troubleshooting](#troubleshooting).**

---

## 📐 Conventional Commits Format

InsightsLM follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### **Format Structure**

```
<type>(<scope>): <subject>

<body>

<footer>
```

---

### **Types**

| Type | Description | Example |
|------|-------------|---------|
| **feat** | New feature | `feat(backend): add Gemini provider` |
| **fix** | Bug fix | `fix(frontend): resolve audio player seek bug` |
| **docs** | Documentation changes | `docs(setup): update Python requirements` |
| **style** | Code style (formatting, no logic change) | `style(backend): format with Black` |
| **refactor** | Code refactoring | `refactor(llm): extract provider logic` |
| **perf** | Performance improvements | `perf(whisper): optimize GPU memory usage` |
| **test** | Adding or updating tests | `test(api): add integration tests` |
| **chore** | Build, dependencies, tooling | `chore(deps): update fastapi to 0.118.3` |

---

### **Scopes**

Use specific scopes to indicate which part of the codebase was modified:

**Backend Scopes:**
- `backend` - General backend changes
- `api` - API endpoints
- `llm` - LLM service
- `config` - Configuration service
- `transcription` - Transcription service
- `database` - Database models
- `vector-db` - Vector database

**Frontend Scopes:**
- `frontend` - General frontend changes
- `ui` - User interface
- `electron` - Electron main process
- `api-client` - API client
- `settings` - Settings panel
- `audio-player` - Audio player component

**General Scopes:**
- `docs` - Documentation
- `deps` - Dependencies
- `build` - Build configuration
- `ci` - CI/CD pipeline

---

### **Subject**

- Use imperative mood ("add" not "added" or "adds")
- No period at the end
- Lowercase first letter (after the scope)
- Maximum 72 characters
- Describe WHAT changed, not WHY

**Good Examples:**
- `feat(backend): add Anthropic Claude 4 support`
- `fix(frontend): resolve audio player seek bug`
- `docs(api): update endpoint documentation`

**Bad Examples:**
- `Added new feature` (past tense)
- `Fix bug.` (period at end)
- `Updates` (too vague)

---

### **Body (Optional)**

- Explain WHY the change was made
- Provide additional context
- Separate from subject with blank line
- Wrap at 72 characters

**Example:**
```
feat(backend): add rate limiting to API endpoints

The API was experiencing abuse from a single client making excessive
requests. This adds rate limiting middleware to protect the backend
and ensure fair usage across all clients.
```

---

### **Footer (Optional)**

- Reference issue numbers
- Note breaking changes
- Credit contributors

**Examples:**
```
Fixes #123
Closes #45, #67
BREAKING CHANGE: API key format changed from v1 to v2
Co-authored-by: John Doe <john@example.com>
```

---

### **Complete Examples**

#### **Feature Addition**

```
feat(backend): add Google Gemini provider support

- Implement Gemini API client
- Add model discovery endpoint
- Update provider selection logic
- Add integration tests

This enables users to use Google's Gemini models for analysis,
providing an alternative to OpenAI and Anthropic.

Closes #234
```

---

#### **Bug Fix**

```
fix(frontend): resolve audio player timestamp sync issue

The audio player was not properly syncing with clicked timestamps
in the transcript. Fixed by updating the time update handler to
respect manual seeks and prevent race conditions.

Fixes #156
```

---

#### **Documentation**

```
docs(setup): update Python version requirement to 3.12.3

Updated all documentation to reflect actual system requirements
based on production deployment information extraction.

- README.md: Updated tech stack versions
- SETUP_GUIDE.md: Updated prerequisites
- CONTRIBUTING.md: Updated dev requirements
```

---

## 📦 Common Scenarios

### **Scenario 1: Backend-Only Changes**

**Example:** Fixed a bug in backend API

```bash
# Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git add backend/main.py
git commit -m "fix(api): resolve null pointer in /summarize endpoint"
git push origin main
cd backend

# Frontend (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git pull origin main
cd frontend
```

---

### **Scenario 2: Frontend-Only Changes**

**Example:** Updated UI styling

```bash
# Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git pull origin main
cd backend

# Frontend (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git pull origin main
git add frontend/src/index.css
git commit -m "style(ui): update color scheme for dark mode"
git push origin main
cd frontend
```

---

### **Scenario 3: Coordinated Backend + Frontend**

**Example:** New feature requiring both backend and frontend changes

```bash
# Backend FIRST (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git add backend/main.py backend/services/export_service.py
git commit -m "feat(backend): add PDF export endpoint"
git push origin main
cd backend

# Frontend SECOND (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git pull origin main  # Get backend changes
git add frontend/src/App.tsx frontend/src/services/api.ts
git commit -m "feat(frontend): add PDF export button and API integration"
git push origin main
cd frontend

# Synchronize Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git pull origin main
cd backend
```

---

### **Scenario 4: Documentation Changes**

**Example:** Updated README

```bash
# Can be done from EITHER environment

# From Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git add README.md
git commit -m "docs(readme): update installation instructions"
git push origin main
cd backend

# Then sync Frontend (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git pull origin main
cd frontend
```

---

### **Scenario 5: Dependency Updates**

**Backend Dependencies:**
```bash
# Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git add backend/requirements.txt
git commit -m "chore(deps): update fastapi to 0.118.3"
git push origin main
cd backend
```

**Frontend Dependencies:**
```powershell
# Frontend (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git add frontend/package.json frontend/package-lock.json
git commit -m "chore(deps): update react to 19.2.0"
git push origin main
cd frontend
```

---

## 🔧 Troubleshooting

### **Issue 1: "fatal: not a git repository"**

**Symptom:**
```
fatal: not a git repository (or any of the parent directories): .git
```

**Cause:** Running git commands from wrong directory

**Solution:**
```bash
# Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
pwd  # Should show /home/YOUR-USERNAME/InsightsLM

# Frontend (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
pwd  # Should show C:\Users\YOUR-USERNAME\Projects\InsightsLM
```

---

### **Issue 2: "Updates were rejected"**

**Symptom:**
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work
```

**Cause:** Remote has commits you don't have locally

**Solution:**
```bash
git pull origin main
# Resolve any conflicts if they appear
git push origin main
```

---

### **Issue 3: Merge Conflicts**

**Symptom:**
```
CONFLICT (content): Merge conflict in backend/main.py
Automatic merge failed; fix conflicts and then commit the result.
```

**Solution:**
1. Open the conflicted file
2. Look for conflict markers:
   ```python
   <<<<<<< HEAD
   your changes
   =======
   remote changes
   >>>>>>> origin/main
   ```
3. Edit to keep desired changes
4. Remove conflict markers
5. Stage and commit:
   ```bash
   git add backend/main.py
   git commit -m "fix: resolve merge conflict in main.py"
   git push origin main
   ```

---

### **Issue 4: Merge Editor Opens Unexpectedly**

**Symptom:** Git opens a text editor (nano/vim) for merge commit message

**Cause:** Git wants you to confirm the merge message

**Solution:**
- **In nano:** Press `Ctrl+X`, then `Y`, then `Enter`
- **In vim:** Press `Esc`, then type `:wq`, then `Enter`
- **Or:** Just close the editor - Git will use the default message

---

### **Issue 5: Different Commit History in Both Environments**

**Symptom:** `git log` shows different commits in backend vs frontend

**Cause:** Forgot to synchronize after pushing

**Solution:**
```bash
# Backend (WSL2)
cd /home/YOUR-USERNAME/InsightsLM
git pull origin main

# Frontend (Windows)
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git pull origin main

# Verify both show same commits
git log --oneline -5
```

---

### **Issue 6: Accidentally Committed from Wrong Directory**

**Symptom:** Commit includes unexpected files or is in wrong scope

**Solution - Undo Last Commit (before push):**
```bash
git reset --soft HEAD~1
# This undoes the commit but keeps changes staged
# Now you can recommit correctly
```

**Solution - Undo Last Commit (after push):**
```bash
# This is more complex, requires force push
git reset --hard HEAD~1
git push --force origin main
# ⚠️ WARNING: Only do this if you're the only one working on the branch
```

---

### **Issue 7: package-lock.json Changes Unexpectedly**

**Symptom:** `git status` shows `frontend/package-lock.json` modified even though you didn't change dependencies

**Cause:** npm install updated the lock file due to npm version differences

**Solution - Option A (Commit it):**
```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git add frontend/package-lock.json
git commit -m "chore(frontend): update package-lock.json"
git push origin main
```

**Solution - Option B (Discard it):**
```powershell
cd C:\Users\YOUR-USERNAME\Projects\InsightsLM
git checkout frontend/package-lock.json
```

**Prevention:** Use the same npm version across all environments

---

## ✅ Best Practices

### **1. Commit Frequently**

- Commit logical units of work
- Don't wait for entire feature to be done
- Smaller commits are easier to review and debug

**Good:**
- `feat(api): add /health endpoint`
- `feat(api): add /status endpoint`
- `feat(api): add error handling to health checks`

**Bad:**
- `feat(api): add all new endpoints and fix bugs` (too large)

---

### **2. Write Descriptive Messages**

**Good:**
```
feat(transcription): add language auto-detection

Whisper now automatically detects the audio language if not specified.
This improves user experience by eliminating the need to manually
select the language for each transcription.

Closes #123
```

**Bad:**
```
update code
```

---

### **3. Always Pull Before Pushing**

```bash
# Always do this before pushing
git pull origin main
git push origin main
```

This prevents "updates were rejected" errors.

---

### **4. Review Changes Before Committing**

```bash
# Review what changed
git status
git diff

# Review what's staged
git diff --staged
```

Don't commit blindly - know what you're committing.

---

### **5. Use .gitignore Properly**

**Already ignored:**
- `backend/venv/`
- `backend/__pycache__/`
- `frontend/node_modules/`
- `frontend/.vite/`
- `frontend/out/`
- `.env` files

**Verify .gitignore:**
```bash
cat .gitignore
```

---

### **6. Keep Commit History Clean**

- Don't commit temporary files
- Don't commit sensitive data (API keys, passwords)
- Don't commit large binary files (use Git LFS if needed)
- Don't commit debugging code (console.log, print statements)

---

### **7. Synchronize Regularly**

```bash
# At least once per day, sync both environments
# Backend (WSL2)
git pull origin main

# Frontend (Windows)
git pull origin main
```

This prevents divergence and merge conflicts.

---

### **8. Use Branches for Major Features**

For large features that take multiple days:

```bash
# Create feature branch
git checkout -b feature/ai-model-comparison

# Work on feature, commit normally
git add ...
git commit -m "feat: ..."

# When done, merge to main
git checkout main
git merge feature/ai-model-comparison
git push origin main
```

---

### **9. Test Before Committing**

**Backend:**
```bash
# Run tests
pytest

# Verify server starts
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```powershell
# Lint code
npm run lint

# Build succeeds
npm run make
```

Don't commit broken code.

---

### **10. Document Breaking Changes**

If a commit breaks compatibility:

```
feat(api): change authentication to use JWT tokens

BREAKING CHANGE: API key authentication is removed. All clients must
now use JWT tokens for authentication. Update your API client to
include the Authorization header with Bearer token.

Migration guide: docs/migration-v2.md
```

---

## 📚 Quick Reference

### **Essential Commands**

```bash
# Check status
git status

# View recent commits
git log --oneline -5

# Stage files
git add <file>

# Commit
git commit -m "message"

# Push
git push origin main

# Pull
git pull origin main

# View changes
git diff
git diff --stat
```

---

### **Common Commit Types**

```bash
feat(scope):    # New feature
fix(scope):     # Bug fix
docs(scope):    # Documentation
style(scope):   # Formatting
refactor(scope): # Code restructure
perf(scope):    # Performance
test(scope):    # Tests
chore(scope):   # Maintenance
```

---

### **Emergency Commands**

```bash
# Undo last commit (before push)
git reset --soft HEAD~1

# Discard all uncommitted changes
git reset --hard HEAD

# Discard specific file changes
git checkout <file>

# View what would be deleted
git clean -n

# Delete untracked files
git clean -f
```

---

## 📖 Additional Resources

- **Conventional Commits:** https://www.conventionalcommits.org/
- **Git Documentation:** https://git-scm.com/doc
- **GitHub Flow:** https://docs.github.com/en/get-started/quickstart/github-flow
- **InsightsLM Contributing Guide:** [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 🆘 Getting Help

**If you're stuck:**

1. Review this guide's [Troubleshooting](#troubleshooting) section
2. Check git status: `git status`
3. Check git log: `git log --oneline -5`
4. Ask for help on GitHub Discussions
5. Open an issue if you found a bug in the workflow

---

**Version:** 1.0  
**Last Updated:** November 4, 2025  
**Status:** ✅ Complete and ready for use
