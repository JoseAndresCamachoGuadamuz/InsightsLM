# Code Documentation Standards

**InsightsLM Coding and Documentation Style Guide**

**Version:** 1.1 (Updated with new log.ts module)  
**Last Updated:** November 4, 2025

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Python Documentation](#-python-documentation)
3. [TypeScript/JavaScript Documentation](#-typescriptjavascript-documentation)
4. [React Component Documentation](#-react-component-documentation)
5. [Comment Guidelines](#-comment-guidelines)
6. [Tools and Validation](#-tools-and-validation)
7. [Documentation Checklist](#-documentation-checklist)
8. [Additional Resources](#-additional-resources)

---

## 🎯 Overview

This document defines the documentation standards for InsightsLM. Proper documentation:
- Improves code maintainability
- Helps new contributors understand the codebase
- Generates automatic API documentation
- Reduces bugs through clear interfaces

**Key Principles:**
- **Clarity** - Write for humans, not just compilers
- **Completeness** - Document parameters, returns, and exceptions
- **Consistency** - Follow the same format throughout
- **Examples** - Provide usage examples for complex functions

---

## 🐍 Python Documentation

### Module-Level Documentation

Every Python file should start with a module docstring:

```python
"""
LLM Service Module

This module provides integration with multiple AI language model providers
including Ollama, OpenAI, Anthropic (Claude), and Google Gemini.

Features:
- Dynamic model discovery
- Provider-specific error handling
- Streaming text generation support
- Automatic retry logic

Example:
    >>> from services.llm_service import generate_text
    >>> response = generate_text("Hello", "ollama/llama3.2", config)
    >>> print(response)
    "Hello! How can I help you today?"

Author: Your Name
Created: October 2025
"""
```

---

### Function Documentation

Use **Google-style docstrings** for all functions:

```python
def transcribe_audio(file_path: str, language: str = "auto") -> dict:
    """
    Transcribe audio file using OpenAI Whisper model.
    
    This function processes an audio file through the Whisper large-v3 model
    to generate a transcript with word-level timestamps. It automatically
    detects the language if not specified.
    
    Args:
        file_path: Absolute path to the audio file to transcribe.
                   Supported formats: MP3, WAV, M4A, FLAC, OGG
        language: Language code (ISO 639-1) or "auto" for automatic detection.
                  Examples: "en", "es", "fr", "auto"
                  Default is "auto".
    
    Returns:
        Dictionary containing transcription results:
            text (str): Full transcript text
            segments (list): List of segment dictionaries with:
                - id (int): Segment ID
                - start (float): Start timestamp in seconds
                - end (float): End timestamp in seconds
                - text (str): Segment text
            language (str): Detected or specified language code
            duration (float): Audio duration in seconds
    
    Raises:
        FileNotFoundError: If the audio file doesn't exist at the specified path
        WhisperError: If transcription fails due to corrupt audio or model error
        ValueError: If language code is invalid
        
    Example:
        >>> result = transcribe_audio("/path/to/audio.mp3", "en")
        >>> print(result['text'])
        "This is the full transcript of the audio file..."
        >>> print(len(result['segments']))
        42
    
    Note:
        - Large files (>30MB) may take several minutes to process
        - GPU acceleration significantly improves performance (30x faster)
        - The Whisper model is loaded only once and cached for reuse
        - Temp files are automatically cleaned up after processing
    
    See Also:
        download_audio_from_url: For transcribing from URLs
        export_transcription: For exporting results to various formats
    """
    # Implementation...
```

---

### Class Documentation

Document classes with comprehensive docstrings:

```python
class ConfigService:
    """
    Configuration management service with encryption support.
    
    This service handles all application configuration including API keys,
    model selections, and provider settings. API keys are automatically
    encrypted using AES-256 before storage.
    
    Attributes:
        config_path (str): Path to the configuration file
        encryption_key (bytes): Master encryption key (32 bytes)
    
    Example:
        >>> service = ConfigService()
        >>> service.save_config({"openai_api_key": "sk-..."})
        >>> config = service.load_config()
        >>> print(config['default_provider'])
        "ollama"
    
    Note:
        The encryption key is generated once and stored separately from
        the configuration file for security.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration service.
        
        Args:
            config_path: Optional path to config file. If None, uses default
                        location: ~/.local/share/InsightsLM/config.json
        """
        pass
```

---

### Type Hints

Always use type hints for better IDE support and documentation:

```python
from typing import List, Dict, Optional, Union, Any

def get_models(
    provider: str,
    include_deprecated: bool = False
) -> List[Dict[str, Union[str, int]]]:
    """
    Get available models for a specific provider.
    
    Args:
        provider: Provider name ("ollama", "openai", "anthropic", "google")
        include_deprecated: Whether to include deprecated models
    
    Returns:
        List of model dictionaries, each containing:
            - model_key (str): Full model identifier
            - name (str): Human-readable model name
            - context_length (int): Maximum context window size
    """
    pass
```

---

### Error Documentation

Document all exceptions that can be raised:

```python
def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to disk with API key encryption.
    
    Args:
        config: Configuration dictionary to save
    
    Raises:
        PermissionError: If config file is not writable
        EncryptionError: If API key encryption fails
        ValidationError: If config contains invalid values
        
    Example:
        >>> save_config({"default_provider": "ollama"})
    """
    pass
```

---

## 📜 TypeScript/JavaScript Documentation

### TSDoc Format

Use **TSDoc** for all exported functions and classes:

```typescript
/**
 * Upload and transcribe an audio file using the backend API
 * 
 * This function sends an audio file to the backend for transcription using
 * OpenAI Whisper. It handles file validation, upload progress, and error
 * handling.
 * 
 * @param formData - FormData containing the audio file
 * @param onProgress - Optional callback for upload progress updates
 * @returns Promise resolving to transcription result
 * 
 * @example
 * ```typescript
 * const formData = new FormData();
 * formData.append('file', audioFile);
 * 
 * const result = await uploadAndTranscribe(formData, (progress) => {
 *   console.log(`Upload: ${progress}%`);
 * });
 * 
 * console.log(result.data.transcription.text);
 * console.log(`Source ID: ${result.data.source_id}`);
 * ```
 * 
 * @throws {AxiosError} If upload fails or backend is unreachable
 * @throws {ValidationError} If file format is not supported
 * 
 * @remarks
 * Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC, MP4, AVI, MOV, MKV
 * Maximum file size: 500MB
 * 
 * @see {@link transcribeFromUrl} for URL-based transcription
 * @see {@link getSummary} for generating summaries
 */
export const uploadAndTranscribe = async (
  formData: FormData,
  onProgress?: (progress: number) => void
): Promise<AxiosResponse<TranscriptionResult>> => {
  return axios.post(`${BASE_URL}/upload/`, formData, {
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentComplete = (progressEvent.loaded / progressEvent.total) * 100;
        onProgress(Math.round(percentComplete));
      }
    }
  });
};
```

---

### Interface Documentation

Document all exported interfaces:

```typescript
/**
 * Configuration object for LLM providers
 * 
 * @remarks
 * API keys are never stored in plain text. They are encrypted with AES-256
 * before being saved to disk.
 */
interface Config {
  /** Base URL for Ollama API (default: http://localhost:11434) */
  ollama_base_url: string;
  
  /** Encrypted Ollama API key (may be empty for local use) */
  ollama_api_key_encrypted: string;
  
  /** Encrypted OpenAI API key (format: sk-proj-...) */
  openai_api_key_encrypted: string;
  
  /** Selected OpenAI model (e.g., "gpt-4o", "gpt-3.5-turbo") */
  openai_model: string;
  
  /** Encrypted Anthropic API key (format: sk-ant-...) */
  anthropic_api_key_encrypted: string;
  
  /** Selected Anthropic model (e.g., "claude-sonnet-4") */
  anthropic_model: string;
  
  /** Encrypted Google API key */
  google_api_key_encrypted: string;
  
  /** Selected Google Gemini model (e.g., "gemini-1.5-pro") */
  google_model: string;
  
  /** Default AI provider to use ("ollama", "openai", "anthropic", "google") */
  default_provider: "ollama" | "openai" | "anthropic" | "google";
}
```

---

### Type Annotations

Always use explicit types:

```typescript
/**
 * Fetch configuration from backend
 * 
 * @returns Promise resolving to current configuration
 * @throws {AxiosError} If backend is unreachable
 */
export const getConfig = (): Promise<AxiosResponse<Config>> => {
  return axios.get<Config>(`${BASE_URL}/config/`);
};

// ❌ Bad - No type safety
export const getConfig = (): Promise<any> => {
  return axios.get(`${BASE_URL}/config/`);
};
```

---

### Enum Documentation

Document enum values:

```typescript
/**
 * Export file format options
 */
enum ExportFormat {
  /** Plain text format (.txt) */
  TXT = 'txt',
  
  /** Markdown format (.md) - Good for GitHub */
  MD = 'md',
  
  /** Microsoft Word format (.docx) - Best for editing */
  DOCX = 'docx',
  
  /** PDF format (.pdf) - Best for distribution */
  PDF = 'pdf',
  
  /** JSON format (.json) - Best for API integration */
  JSON = 'json'
}
```

---

## ⚛️ React Component Documentation

### Functional Components

Document all props and behavior:

```typescript
interface AudioPlayerProps {
  /** Audio file URL or path to play */
  src: string;
  
  /** Callback fired when playback time changes */
  onTimeUpdate?: (currentTime: number) => void;
  
  /** Callback fired when seeking to a specific timestamp */
  onSeek?: (timestamp: number) => void;
  
  /** Whether player should start playing automatically */
  autoPlay?: boolean;
  
  /** Show or hide the volume control */
  showVolumeControl?: boolean;
}

/**
 * Audio player component with timeline and playback controls
 * 
 * Features:
 * - Play/pause/seek functionality
 * - Timeline with clickable timestamps
 * - Volume control
 * - Keyboard shortcuts (space = play/pause, arrow keys = seek)
 * 
 * @param props - Component properties
 * @returns Audio player component
 * 
 * @example
 * ```tsx
 * <AudioPlayer
 *   src="/audio/meeting.mp3"
 *   onTimeUpdate={(time) => console.log(`Current: ${time}s`)}
 *   onSeek={(time) => console.log(`Seeking to: ${time}s`)}
 *   autoPlay={false}
 *   showVolumeControl={true}
 * />
 * ```
 * 
 * @remarks
 * Keyboard shortcuts:
 * - Space: Play/Pause
 * - Left Arrow: Rewind 5 seconds
 * - Right Arrow: Forward 5 seconds
 * - M: Mute/Unmute
 */
const AudioPlayer: React.FC<AudioPlayerProps> = ({
  src,
  onTimeUpdate,
  onSeek,
  autoPlay = false,
  showVolumeControl = true
}) => {
  // Component implementation...
};
```

---

### Custom Hooks

Document custom React hooks:

```typescript
/**
 * Custom hook for managing audio transcription state
 * 
 * Handles file upload, transcription progress, and result retrieval.
 * 
 * @returns Transcription state and control functions
 * 
 * @example
 * ```tsx
 * const {
 *   isTranscribing,
 *   progress,
 *   transcription,
 *   startTranscription,
 *   error
 * } = useTranscription();
 * 
 * const handleFile = async (file: File) => {
 *   await startTranscription(file);
 *   console.log(transcription?.text);
 * };
 * ```
 */
const useTranscription = () => {
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [transcription, setTranscription] = useState<TranscriptionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const startTranscription = async (file: File) => {
    // Implementation...
  };
  
  return {
    isTranscribing,
    progress,
    transcription,
    startTranscription,
    error
  };
};
```

---

## 💬 Comment Guidelines

### When to Comment

**DO comment:**
- Complex algorithms or logic
- Non-obvious design decisions
- Workarounds for bugs or limitations
- TODOs and FIXMEs
- Performance-critical code
- Security-related code

**DON'T comment:**
- Obvious code (e.g., `// Increment i` for `i++`)
- Code that can be made self-explanatory with better names
- Redundant information already in docstrings

---

### Inline Comments

```python
# Good - Explains WHY, not WHAT
# Use binary search here because the segments list is sorted by timestamp
# and can be very large (10,000+ segments for long audio files)
segment_index = binary_search(segments, target_timestamp)

# Bad - Obvious what it does
# Get the segment index
segment_index = binary_search(segments, target_timestamp)
```

---

### TODO/FIXME Format

```python
# TODO(username): Add support for speaker diarization
# Requires: py-webrtcvad library
# Estimated effort: 2-3 days
# Priority: Medium

# FIXME(username): Memory leak when processing large files (>2GB)
# Temporary workaround: Split file into chunks
# Issue: #123

# HACK(username): Workaround for Whisper timestamp bug
# Remove this when whisper-1.5.0 is released
# Reference: https://github.com/openai/whisper/issues/456
```

---

### Logging Module Documentation

**NEW: log.ts module conventions**

```typescript
/**
 * Logging utility module for cross-platform terminal output
 * 
 * This module provides consistent logging across different environments
 * (PowerShell, WSL, CMD) by handling CRLF/LF line ending differences.
 * 
 * Features:
 * - Automatic line ending detection
 * - Platform-specific formatting
 * - Consistent output across Windows and Linux terminals
 * 
 * @example
 * ```typescript
 * import { logInfo, logError } from './log';
 * 
 * logInfo('Backend', 'Server started on port 8000');
 * logError('Frontend', 'Failed to connect to backend');
 * ```
 */

/**
 * Log an informational message
 * 
 * @param prefix - Message prefix (e.g., "Backend", "Frontend")
 * @param message - Message to log
 */
export function logInfo(prefix: string, message: string): void {
  // Implementation...
}

/**
 * Log an error message
 * 
 * @param prefix - Message prefix
 * @param message - Error message
 * @param error - Optional error object
 */
export function logError(
  prefix: string,
  message: string,
  error?: Error
): void {
  // Implementation...
}
```

---

## 🛠️ Tools and Validation

### Python Tools

**Black** (code formatter):
```bash
# Format all Python files
black .

# Check without modifying
black --check .
```

**flake8** (linter):
```bash
# Lint all Python files
flake8 .

# With specific config
flake8 --max-line-length=100 --ignore=E203,W503 .
```

**mypy** (type checker):
```bash
# Type check all files
mypy main.py services/

# Strict mode
mypy --strict main.py
```

**Sphinx** (documentation generator):
```bash
# Generate HTML documentation
sphinx-build -b html docs/ docs/_build/
```

---

### TypeScript/JavaScript Tools

**ESLint** (linter):
```powershell
# Lint all files
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

**Prettier** (formatter):
```powershell
# Format all files
npx prettier --write "src/**/*.{ts,tsx,js,jsx}"
```

**TypeDoc** (documentation generator):
```powershell
# Generate documentation
npx typedoc --out docs src/
```

---

### IDE Configuration

**VS Code Settings (`.vscode/settings.json`):**

```json
{
  "editor.formatOnSave": true,
  "editor.rulers": [100, 120],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "typescript.tsdk": "node_modules/typescript/lib",
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ]
}
```

---

## ✅ Documentation Checklist

Before submitting code, ensure:

- [ ] All public functions have docstrings
- [ ] All parameters are documented with types
- [ ] Return values are documented
- [ ] Exceptions are documented
- [ ] Examples are provided for complex functions
- [ ] Comments explain WHY, not WHAT
- [ ] TODOs include username and context
- [ ] No spelling errors in documentation
- [ ] Code passes linting (flake8/ESLint)
- [ ] Code is formatted (Black/Prettier)

---

## 📚 Additional Resources

**Python:**
- PEP 257: Docstring Conventions
- Google Python Style Guide
- Sphinx Documentation

**TypeScript:**
- TSDoc Specification
- TypeScript Handbook
- JSDoc Reference

**React:**
- React TypeScript Cheatsheet
- React Documentation Best Practices

---

**Version:** 1.1  
**Last Updated:** November 4, 2025  
**Status:** ✅ Updated with log.ts module documentation standards
