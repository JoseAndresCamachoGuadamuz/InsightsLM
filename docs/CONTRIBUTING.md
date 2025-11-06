# Contributing to InsightsLM

Thank you for your interest in contributing to InsightsLM! This document provides guidelines for contributing to the project effectively.

**Version:** 1.1 (Updated with actual development requirements)  
**Last Updated:** November 4, 2025

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Commit Message Guidelines](#commit-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Testing](#testing)
8. [Documentation](#documentation)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect:

- **Respectful communication** in all interactions
- **Constructive feedback** focused on improving the code
- **Collaborative problem-solving** to achieve project goals
- **Recognition and appreciation** of all contributions

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting remarks, or personal attacks
- Publishing private information without consent
- Other conduct inappropriate in a professional setting

---

## 🚀 Getting Started

### Prerequisites

**For Backend Development:**
- Python **3.12.3** or higher
- pip **24.0** or higher
- Virtual environment support (venv)
- WSL2 (Windows users) or Linux/macOS
- Git
- GPU support (optional, improves Whisper performance)

**For Frontend Development:**
- Node.js **v22.17.1** or higher
- npm **11.6.2** or higher
- Windows, macOS, or Linux
- Git
- Code editor (VS Code recommended)

---

### Fork and Clone

1. **Fork the repository** on GitHub (click "Fork" button)

2. **Clone your fork** locally:
```bash
git clone https://github.com/YOUR_USERNAME/InsightsLM.git
cd InsightsLM
```

3. **Add upstream remote:**
```bash
git remote add upstream https://github.com/original/InsightsLM.git
git fetch upstream
```

---

### Development Setup

#### **Backend Setup (WSL2/Linux):**

```bash
cd ~/InsightsLM/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Verify installation
python3 --version  # Should show Python 3.12.3 or higher
pip list | grep -E "fastapi|whisper"
```

#### **Frontend Setup (Windows/macOS/Linux):**

```powershell
cd InsightsLM/frontend

# Install dependencies
npm install

# Install development tools (if not included)
npm install --save-dev eslint @typescript-eslint/eslint-plugin

# Verify installation
node --version  # Should show v22.17.1 or higher
npm --version   # Should show 11.6.2 or higher
```

---

## 🔄 Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/bug-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

---

### 2. Make Your Changes

**Backend Development:**

```bash
# Start backend with auto-reload
cd ~/InsightsLM/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development:**

```powershell
# Start with hot reload
cd InsightsLM\frontend
npm start
```

**Key files to know:**

**Backend:** (Python)
- `main.py` (911 lines) - API routes and application setup
- `services/config_service.py` (22KB) - Configuration and encryption
- `services/llm_service.py` (29KB) - Multi-provider AI integration
- `services/transcription_service.py` (1.1KB) - Whisper integration
- `database/models.py` (1.7KB) - Database models
- `schemas.py` - Pydantic request/response schemas

**Frontend:** (TypeScript/React)
- `src/main.ts` (824 lines) - Electron main process
- `src/App.tsx` (1,848 lines) - Main React application
- `src/services/api.ts` (211 lines) - Backend API client
- `src/preload.ts` (30 lines) - Preload script
- `src/log.ts` - Logging utilities

---

### 3. Follow Coding Standards

See [CODE_STANDARDS.md](./CODE_STANDARDS.md) for detailed coding standards.

**Quick Reference:**

**Python:**
- Follow PEP 8
- Use Google-style docstrings
- Type hints for all functions
- Black for code formatting
- Maximum line length: 100 characters

**TypeScript:**
- Use TSDoc comments
- Explicit types (avoid `any`)
- ESLint rules enforced
- Prettier for formatting
- Maximum line length: 120 characters

---

### 4. Run Tests

**Backend Tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_llm_service.py
```

**Frontend Tests:**

```powershell
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- App.test.tsx
```

---

### 5. Lint and Format

**Backend:**

```bash
# Format code with Black
black .

# Check with flake8
flake8 .

# Type check with mypy
mypy main.py services/
```

**Frontend:**

```powershell
# Lint TypeScript
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

---

### 6. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git add .
git commit -m "feat(backend): add support for new AI provider"
```

See [Commit Guidelines](#commit-guidelines) for details.

---

### 7. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
```

---

## 💻 Coding Standards

### Python (Backend)

#### **1. Code Style**
- Follow **PEP 8** style guide
- Use **Black** for automatic formatting
- Maximum line length: **100 characters**
- Use **4 spaces** for indentation
- Use **snake_case** for variables and functions
- Use **PascalCase** for class names

#### **2. Docstrings**
Use **Google-style docstrings**:

```python
def transcribe_audio(file_path: str, language: str = "auto") -> dict:
    """
    Transcribe audio file using Whisper model.
    
    This function processes an audio file through the Whisper large-v3 model
    to generate a transcript with timestamps for each segment.
    
    Args:
        file_path: Absolute path to the audio file to transcribe
        language: Language code (ISO 639-1) or "auto" for auto-detection.
                  Default is "auto".
    
    Returns:
        Dictionary containing:
            - text (str): Full transcript text
            - segments (list): List of segment dictionaries
            - language (str): Detected/specified language code
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
        WhisperError: If transcription fails
        
    Example:
        >>> result = transcribe_audio("/path/to/audio.mp3", "en")
        >>> print(result['text'])
        "This is the transcript..."
    
    Note:
        Large files (>30MB) may take several minutes to process.
    """
    # Implementation...
```

#### **3. Type Hints**
Always use type hints:

```python
from typing import List, Dict, Optional

def get_sources(limit: int = 100, offset: int = 0) -> List[Dict[str, any]]:
    """Get list of sources."""
    pass
```

#### **4. Error Handling**
Provide clear, user-friendly error messages:

```python
try:
    result = api_call()
except APIKeyError as e:
    raise HTTPException(
        status_code=401,
        detail={
            "error": "API_KEY_INVALID",
            "message": "Your OpenAI API key is invalid or expired.",
            "suggestion": "Get a new API key from: https://platform.openai.com/api-keys",
            "provider": "openai"
        }
    )
```

---

### TypeScript (Frontend)

#### **1. Code Style**
- Use **ESLint** configuration
- Maximum line length: **120 characters**
- Use **2 spaces** for indentation
- Use **camelCase** for variables and functions
- Use **PascalCase** for components and classes

#### **2. TSDoc Comments**
Document exported functions and components:

```typescript
/**
 * Upload and transcribe an audio file
 * 
 * @param file - Audio file to transcribe
 * @returns Promise resolving to transcription result
 * 
 * @example
 * ```typescript
 * const formData = new FormData();
 * formData.append('file', audioFile);
 * const result = await uploadAndTranscribe(formData);
 * console.log(result.data.transcription.text);
 * ```
 * 
 * @throws {AxiosError} If upload or transcription fails
 */
export const uploadAndTranscribe = async (
  formData: FormData
): Promise<AxiosResponse<TranscriptionResult>> => {
  return axios.post(`${BASE_URL}/upload/`, formData);
};
```

#### **3. React Components**
Document component props:

```typescript
interface AudioPlayerProps {
  /** Audio file URL to play */
  src: string;
  /** Callback when playback time changes */
  onTimeUpdate?: (currentTime: number) => void;
  /** Whether player is initially playing */
  autoPlay?: boolean;
}

/**
 * Audio player component with timeline and controls
 * 
 * @param props - Component properties
 * @returns Audio player component
 */
const AudioPlayer: React.FC<AudioPlayerProps> = ({ src, onTimeUpdate, autoPlay = false }) => {
  // Implementation...
};
```

#### **4. Type Safety**
Avoid `any`, use explicit types:

```typescript
// ❌ Bad
function processData(data: any): any {
  return data.value;
}

// ✅ Good
interface DataItem {
  value: string;
  timestamp: number;
}

function processData(data: DataItem): string {
  return data.value;
}
```

---

## 📝 Commit Guidelines

### Commit Message Format

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature change or bug fix)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling

### Examples

**Feature:**
```
feat(backend): add Anthropic Claude 4 support

- Add Claude 4 models to llm_service.py
- Update model discovery endpoint
- Add integration tests
```

**Bug Fix:**
```
fix(frontend): resolve audio player seek bug

The audio player wasn't properly seeking to clicked timestamps.
Fixed by updating the time update handler to respect manual seeks.

Fixes #123
```

**Documentation:**
```
docs(setup): update Python version requirement

Update SETUP_GUIDE.md to reflect Python 3.12.3 requirement
based on actual system information extraction.
```

**Refactoring:**
```
refactor(backend): extract config encryption to separate module

Move encryption logic from config_service.py to new crypto_utils.py
for better separation of concerns and testability.
```

---

## 🔍 Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main branch

---

### PR Template

Use this template for your pull request:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran and how to reproduce

## Screenshots (if applicable)
Add screenshots showing the changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] All tests pass locally
```

---

### Review Process

1. **Automated checks** run (tests, linting)
2. **Code review** by maintainer(s)
3. **Requested changes** (if any)
4. **Final approval**
5. **Merge** into main branch

**Expected review time:** 2-5 business days

---

## 🧪 Testing

### Backend Testing

**Test Structure:**
```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_llm_service.py
│   ├── test_transcription_service.py
│   ├── test_config_service.py
│   └── test_api_endpoints.py
```

**Run tests:**
```bash
# All tests
pytest

# Specific test file
pytest tests/test_llm_service.py

# With coverage
pytest --cov=. --cov-report=html
```

**Writing tests:**
```python
import pytest
from services.llm_service import generate_text

def test_generate_text_ollama():
    """Test text generation with Ollama provider."""
    response = generate_text(
        prompt="Hello, world!",
        model_key="ollama/llama3.2",
        config=test_config
    )
    assert response is not None
    assert len(response) > 0
```

---

### Frontend Testing

**Test Structure:**
```
frontend/
├── src/
│   ├── App.test.tsx
│   ├── services/
│   │   └── api.test.ts
│   └── components/
│       └── AudioPlayer.test.tsx
```

**Run tests:**
```powershell
# All tests
npm test

# Watch mode
npm test -- --watch

# With coverage
npm test -- --coverage
```

**Writing tests:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import AudioPlayer from './AudioPlayer';

test('AudioPlayer plays audio when button clicked', () => {
  render(<AudioPlayer src="/test-audio.mp3" />);
  
  const playButton = screen.getByRole('button', { name: /play/i });
  fireEvent.click(playButton);
  
  expect(playButton).toHaveTextContent('Pause');
});
```

---

## 📚 Documentation

### What to Document

**Code-level documentation:**
- All public APIs and functions
- Complex algorithms or logic
- Non-obvious design decisions
- Known limitations or edge cases

**User-facing documentation:**
- New features (USER_GUIDE.md)
- Setup changes (SETUP_GUIDE.md)
- API changes (API_REFERENCE.md)
- Architecture updates (ARCHITECTURE.md)

---

### Documentation Standards

See [CODE_STANDARDS.md](./CODE_STANDARDS.md) for complete documentation standards.

**Key principles:**
- Clear and concise language
- Examples for complex concepts
- Keep documentation in sync with code
- Use diagrams where helpful

---

## 🌟 Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit history

**Types of contributions we value:**
- Code contributions
- Bug reports
- Feature suggestions
- Documentation improvements
- Testing and QA
- Design and UX feedback
- Community support

---

## 📞 Getting Help

**Questions about contributing?**
- Open a [GitHub Discussion](https://github.com/yourusername/InsightsLM/discussions)
- Check existing [Issues](https://github.com/yourusername/InsightsLM/issues)
- Read the [Documentation](./docs/)
- Email: dev@insightslm.com

---

## 📄 License

By contributing to InsightsLM, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to InsightsLM!** 🎉

**Version:** 1.1  
**Last Updated:** November 4, 2025  
**Status:** ✅ Updated with actual development requirements (Python 3.12.3, Node.js 22.17.1, React 19.2.0)
