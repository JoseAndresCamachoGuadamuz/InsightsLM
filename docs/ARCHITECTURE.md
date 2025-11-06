# System Architecture

**InsightsLM - AI-Powered Audio Transcription and Analysis Platform**

**Document Version:** 1.1 (Updated with actual system information)  
**Last Updated:** November 4, 2025  
**Status:** Production-Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Technology Stack](#technology-stack)
5. [Component Architecture](#component-architecture)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
8. [Security Architecture](#security-architecture)
9. [Deployment Architecture](#deployment-architecture)
10. [Design Decisions](#design-decisions)

---

## 🎯 System Overview

InsightsLM is a hybrid desktop application that combines:
- **Electron-based frontend** (Windows) for cross-platform UI
- **FastAPI backend** (WSL2/Linux) for AI processing
- **Local-first architecture** with encrypted data storage
- **Multi-provider AI** support (Ollama, OpenAI, Anthropic, Google Gemini)

### Key Capabilities
- Audio transcription using OpenAI Whisper
- AI-powered content analysis and summarization
- Custom report generation with templates
- Semantic search with vector embeddings
- Multi-provider AI model selection
- Secure API key management

---

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
- Frontend: UI/UX and user interactions
- Backend: AI processing, data management, API integration

### 2. **Security First**
- AES-256 encryption for API keys
- Isolated backend process
- No sensitive data in frontend code

### 3. **Local-First**
- All data stored locally
- No cloud dependency (except AI providers)
- User owns their data

### 4. **Modularity**
- Service-oriented backend architecture
- Reusable React components
- Clear API boundaries

### 5. **Extensibility**
- Easy to add new AI providers
- Template system for custom reports
- Plugin-ready architecture

---

## 🔄 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WINDOWS ENVIRONMENT                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     ELECTRON FRONTEND                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  Main Process│  │   Renderer   │  │   Preload    │    │ │
│  │  │   (main.ts)  │  │   (React)    │  │  (preload.ts)│    │ │
│  │  │   824 lines  │  │  App.tsx     │  │   30 lines   │    │ │
│  │  │              │  │  1,848 lines │  │              │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │ │
│  │         │                 │                 │              │ │
│  │         └─────────────────┼─────────────────┘              │ │
│  │                          │                                 │ │
│  │                    IPC Bridge                              │ │
│  └────────────────────────────┼──────────────────────────────┘ │
│                               │                                 │
│                        HTTP/REST API                            │
│                        (localhost:8000)                         │
└───────────────────────────────┼─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                      WSL2/LINUX ENVIRONMENT                      │
│  ┌────────────────────────────┴──────────────────────────────┐ │
│  │                     FASTAPI BACKEND                        │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌─────────────────────────────────┐   │ │
│  │  │   main.py    │  │         Services Layer          │   │ │
│  │  │  911 lines   │  │  ┌─────────────────────────┐    │   │ │
│  │  │              │  │  │ config_service.py       │    │   │ │
│  │  │ API Routes   │  │  │ (22KB - API keys,       │    │   │ │
│  │  │ (22 endpoints)│ │  │  encryption, settings)  │    │   │ │
│  │  │              │  │  ├─────────────────────────┤    │   │ │
│  │  │ Request      │  │  │ llm_service.py          │    │   │ │
│  │  │ Validation   │  │  │ (29KB - Multi-provider  │    │   │ │
│  │  │              │  │  │  AI integration)        │    │   │ │
│  │  │ Error        │  │  ├─────────────────────────┤    │   │ │
│  │  │ Handling     │  │  │ transcription_service.py│    │   │ │
│  │  │              │  │  │ (1.1KB - Whisper)       │    │   │ │
│  │  └──────┬───────┘  │  ├─────────────────────────┤    │   │ │
│  │         │          │  │ vector_db_service.py    │    │   │ │
│  │         │          │  │ (5KB - ChromaDB)        │    │   │ │
│  │         │          │  ├─────────────────────────┤    │   │ │
│  │         │          │  │ export_service.py       │    │   │ │
│  │         │          │  │ (4.9KB - File exports)  │    │   │ │
│  │         │          │  ├─────────────────────────┤    │   │ │
│  │         │          │  │ downloader_service.py   │    │   │ │
│  │         │          │  │ (1.2KB - URL downloads) │    │   │ │
│  │         │          │  ├─────────────────────────┤    │   │ │
│  │         │          │  │ tts_service.py          │    │   │ │
│  │         │          │  │ (454 bytes - gTTS)      │    │   │ │
│  │         │          │  └─────────────────────────┘    │   │ │
│  │         │          └─────────────────────────────────┘   │ │
│  │         │                                                 │ │
│  │         ├──────────────────┬──────────────────┐          │ │
│  │         │                  │                  │          │ │
│  │   ┌─────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐   │ │
│  │   │  Database  │   │   Vector    │   │  AI Models  │   │ │
│  │   │  (SQLite)  │   │   Database  │   │  (Whisper)  │   │ │
│  │   │            │   │  (ChromaDB) │   │             │   │ │
│  │   │ models.py  │   │             │   │ large-v3    │   │ │
│  │   │ database.py│   │ Embeddings  │   │             │   │ │
│  │   └────────────┘   └─────────────┘   └─────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           External AI Providers (via APIs)             │ │
│  │  ┌─────────┐  ┌─────────┐  ┌───────────┐  ┌────────┐ │ │
│  │  │ Ollama  │  │ OpenAI  │  │ Anthropic │  │ Google │ │ │
│  │  │ (Local) │  │         │  │  Claude   │  │ Gemini │ │ │
│  │  └─────────┘  └─────────┘  └───────────┘  └────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

             ┌────────────────────────────────────┐
             │      Local File System Storage     │
             │  ~/.local/share/InsightsLM/       │
             │  ├── insightslm.db (780KB)        │
             │  ├── chroma_db/ (11MB)            │
             │  ├── config.json (4KB, encrypted) │
             │  ├── temp_uploads/                │
             │  └── static/                      │
             └────────────────────────────────────┘
```

---

## 💻 Technology Stack

### **Frontend (Windows)**

| Technology | Version | Purpose | Lines of Code |
|-----------|---------|---------|---------------|
| **Electron** | 38.2.2 | Desktop app framework | - |
| **React** | 19.2.0 | UI library | 1,848 (App.tsx) |
| **TypeScript** | 4.5.5 | Type safety | ~2,900 total |
| **Vite** | 5.4.21 | Build tool | - |
| **Axios** | 1.12.2 | HTTP client | 211 (api.ts) |
| **Node.js** | 22.17.1 | Runtime | - |
| **npm** | 11.6.2 | Package manager | - |

**Key Files:**
- `main.ts` (824 lines) - Electron main process
- `App.tsx` (1,848 lines) - Main React application
- `api.ts` (211 lines) - Backend API client
- `preload.ts` (30 lines) - Preload script for IPC
- `log.ts` (new) - Logging utilities
- `renderer.tsx` (10 lines) - React entry point

### **Backend (WSL2/Linux)**

| Technology | Version | Purpose | Size/Lines |
|-----------|---------|---------|------------|
| **Python** | 3.12.3 | Runtime | - |
| **FastAPI** | 0.118.3 | Web framework | 911 (main.py) |
| **Uvicorn** | 0.37.0 | ASGI server | - |
| **Pydantic** | 2.12.0 | Data validation | - |
| **SQLAlchemy** | 2.0.44 | Database ORM | - |
| **OpenAI Whisper** | 20250625 | Speech-to-text | - |
| **ChromaDB** | 1.1.1 | Vector database | - |
| **sentence-transformers** | 5.1.1 | Text embeddings | - |

**AI Provider SDKs:**
- **ollama** 0.6.0 - Local AI models
- **openai** 2.3.0 - GPT models
- **anthropic** 0.69.0 - Claude models
- **google-generativeai** 0.8.5 - Gemini models

**Audio Processing:**
- **ffmpeg-python** 0.2.0 - Audio conversion
- **yt-dlp** 2025.10.22 - URL downloads
- **gTTS** 2.5.4 - Text-to-speech

**Security:**
- **pycryptodome** 3.23.0 - Encryption (AES-256)

**Key Files:**
- `main.py` (911 lines) - FastAPI application with 22 endpoints
- `config_service.py` (22KB) - Configuration and encryption
- `llm_service.py` (29KB) - Multi-provider AI integration
- `vector_db_service.py` (5KB) - Semantic search
- `transcription_service.py` (1.1KB) - Whisper integration
- `export_service.py` (4.9KB) - Export formats
- `downloader_service.py` (1.2KB) - URL downloads
- `tts_service.py` (454 bytes) - Text-to-speech
- `models.py` (1.7KB) - Database models
- `database.py` (1.5KB) - Database connection
- `schemas.py` - Pydantic request/response models

---

## 🧩 Component Architecture

### **Frontend Components**

#### **1. Main Process (main.ts - 824 lines)**
**Responsibilities:**
- Create and manage browser windows
- Handle backend lifecycle (spawn, health checks, port management)
- IPC communication with renderer
- System tray and menu management
- Auto-update functionality

**Key Functions:**
```typescript
createWindow()           // Create main application window
startBackend()          // Start FastAPI backend server
healthCheck()           // Verify backend availability
handleDeepLink()        // Handle custom protocol URLs
createApplicationMenu() // Platform-specific menus
```

#### **2. Renderer Process (App.tsx - 1,848 lines)**
**Responsibilities:**
- User interface rendering
- State management
- File upload handling
- Real-time updates (transcription, analysis)
- Settings management
- Audio playback controls

**State Management:**
```typescript
// Transcription state
const [transcriptionId, setTranscriptionId] = useState<number | null>(null);
const [segments, setSegments] = useState<TranscriptSegment[]>([]);
const [isLoading, setIsLoading] = useState(false);

// Settings state
const [llmConfig, setLlmConfig] = useState<Config | null>(null);
const [availableModels, setAvailableModels] = useState<ModelsResponse | null>(null);

// UI state
const [activeTab, setActiveTab] = useState<string>('chat');
const [error, setError] = useState<string>('');
```

**Component Sections:**
- Audio player with timeline
- Transcript display with timestamp navigation
- Chat interface for Q&A
- Summary generation
- Template management
- Report generation
- Settings panel
- Export options

#### **3. API Service (api.ts - 211 lines)**
**Responsibilities:**
- HTTP client for backend communication
- Request/response type definitions
- Error handling and retries
- Port configuration

**Exported Functions:** (25 total)
```typescript
// Transcription
uploadAndTranscribe()
transcribeFromUrl()

// Analysis
getSummary()
postQuery()
getAudioOverview()
runReport()

// Templates
getTemplates()
createTemplate()
updateTemplate()
deleteTemplate()

// Configuration
getConfig()
updateConfig()
testApiConnection()
getAllApiStatus()

// Models
getOllamaModels()
getOpenAIModels()
getAnthropicModels()
getGoogleModels()
getAllModels()

// Export
exportContent()
```

#### **4. Preload Script (preload.ts - 30 lines)**
**Responsibilities:**
- Bridge between main and renderer processes
- Secure IPC exposure
- Context isolation

#### **5. Logging Module (log.ts - NEW)**
**Responsibilities:**
- Cross-platform log formatting
- CRLF/LF detection and normalization
- Consistent logging across PowerShell and WSL

---

### **Backend Components**

#### **1. Main Application (main.py - 911 lines)**
**Responsibilities:**
- FastAPI app initialization
- CORS configuration
- Request routing (22 endpoints)
- Error handling and logging
- Dependency injection
- Static file serving

**API Endpoint Categories:**
```python
# Health & Testing (3 endpoints)
GET  /health
GET  /test-api/status
POST /test-api/{provider}

# Models (5 endpoints)
GET /models/ollama
GET /models/openai
GET /models/anthropic
GET /models/google
GET /models/all

# Transcription (4 endpoints)
POST /upload/
POST /download/
GET  /sources/
GET  /sources/{source_id}/transcription/

# Templates (4 endpoints)
GET    /templates/
POST   /templates/
PUT    /templates/{template_id}
DELETE /templates/{template_id}

# Analysis (4 endpoints)
POST /report/
POST /summarize/
POST /query/
POST /audio-overview/

# Export & Config (2 endpoints)
POST /export/
GET  /config/
PUT  /config/
```

#### **2. Configuration Service (config_service.py - 22KB)**
**Responsibilities:**
- Load/save encrypted configuration
- API key encryption/decryption (AES-256)
- Master key generation and storage
- Provider credential management
- Default configuration setup

**Key Functions:**
```python
load_config()              # Load and decrypt config
save_config()              # Encrypt and save config
encrypt_api_key()          # AES-256 encryption
decrypt_api_key()          # AES-256 decryption
get_master_key()           # Retrieve encryption key
generate_master_key()      # Create new master key
test_ollama_connection()   # Test Ollama availability
test_openai_connection()   # Test OpenAI API
test_anthropic_connection()# Test Anthropic API
test_google_connection()   # Test Google Gemini API
get_all_api_status()       # Test all providers
```

**Configuration Schema:**
```python
{
    "ollama_base_url": "http://localhost:11434",
    "ollama_api_key_encrypted": "...",
    "openai_api_key_encrypted": "...",
    "openai_model": "gpt-4o",
    "anthropic_api_key_encrypted": "...",
    "anthropic_model": "claude-sonnet-4",
    "google_api_key_encrypted": "...",
    "google_model": "gemini-1.5-pro",
    "default_provider": "ollama"
}
```

#### **3. LLM Service (llm_service.py - 29KB)**
**Responsibilities:**
- Multi-provider AI model integration
- Dynamic model discovery
- Text generation with streaming
- Provider-specific error handling
- Token usage tracking

**Supported Providers:**
- **Ollama** (local models) - 45+ models
- **OpenAI** (GPT-3.5, GPT-4) - 21 models
- **Anthropic** (Claude 3, Claude 4) - 9 models
- **Google** (Gemini 1.5) - 29+ models

**Key Functions:**
```python
get_ollama_models()        # Discover available Ollama models
get_openai_models()        # List OpenAI models
get_anthropic_models()     # List Anthropic models
get_google_models()        # List Google Gemini models
get_all_models()           # Aggregate all providers
generate_text()            # Generate AI response
generate_text_with_provider() # Provider-specific generation
```

**Error Handling:**
- API key validation
- Rate limiting detection
- Network error recovery
- User-friendly error messages

#### **4. Transcription Service (transcription_service.py - 1.1KB)**
**Responsibilities:**
- OpenAI Whisper integration
- Audio transcription with timestamps
- Language detection
- Segment extraction

**Key Functions:**
```python
transcribe_audio(file_path: str, language: str = "auto") -> dict
```

**Output Format:**
```python
{
    "text": "Full transcript...",
    "segments": [
        {
            "start": 0.0,
            "end": 5.2,
            "text": "Segment text..."
        },
        ...
    ],
    "language": "en"
}
```

#### **5. Vector Database Service (vector_db_service.py - 5KB)**
**Responsibilities:**
- ChromaDB integration
- Text embedding generation
- Semantic search
- Collection management

**Key Functions:**
```python
add_to_vector_db()         # Store embeddings
query_vector_db()          # Semantic search
delete_from_vector_db()    # Remove embeddings
```

#### **6. Export Service (export_service.py - 4.9KB)**
**Responsibilities:**
- Multi-format export (TXT, MD, DOCX, PDF, JSON)
- Template-based formatting
- File generation

**Supported Formats:**
- **TXT** - Plain text
- **MD** - Markdown
- **DOCX** - Microsoft Word
- **PDF** - Portable Document Format
- **JSON** - Structured data

#### **7. Downloader Service (downloader_service.py - 1.2KB)**
**Responsibilities:**
- URL audio download
- YouTube video extraction
- Format conversion

**Key Functions:**
```python
download_audio_from_url(url: str) -> str
```

#### **8. TTS Service (tts_service.py - 454 bytes)**
**Responsibilities:**
- Text-to-speech conversion
- gTTS integration
- Audio file generation

**Key Functions:**
```python
text_to_speech(text: str, output_path: str, language: str = 'en')
```

---

## 🔄 Data Flow

### **1. Audio Transcription Flow**

```
User Uploads Audio File
         │
         ▼
┌─────────────────────┐
│  Frontend (App.tsx) │
│  File validation    │
└──────────┬──────────┘
           │ HTTP POST /upload/
           ▼
┌─────────────────────────┐
│  Backend (main.py)      │
│  Route: /upload/        │
│  - Save to temp_uploads │
│  - Validate file        │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Transcription Service      │
│  - Load Whisper large-v3    │
│  - Transcribe audio         │
│  - Extract segments         │
│  - Detect language          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Database (SQLite)          │
│  - Insert Source record     │
│  - Store transcription      │
│  - Save metadata            │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Vector DB Service          │
│  - Generate embeddings      │
│  - Store in ChromaDB        │
│  - Index for search         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────┐
│  Response to Frontend│
│  - source_id         │
│  - transcription     │
│  - segments          │
│  - language          │
└─────────────────────┘
```

### **2. AI Analysis Flow (Summary, Chat, Report)**

```
User Requests Analysis
         │
         ▼
┌─────────────────────┐
│  Frontend (App.tsx) │
│  - Select model     │
│  - Enter query/     │
│    template         │
└──────────┬──────────┘
           │ HTTP POST /summarize/ or /query/ or /report/
           ▼
┌─────────────────────────┐
│  Backend (main.py)      │
│  Route handler          │
│  - Validate source_id   │
│  - Validate model_key   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Database Service           │
│  - Fetch transcription      │
│  - Load template (if report)│
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Vector DB Service          │
│  (Optional - for context)   │
│  - Semantic search          │
│  - Retrieve relevant chunks │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  LLM Service                │
│  - Parse model_key          │
│  - Select provider          │
│  - Build prompt             │
│  - Call AI API              │
│  - Stream response          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────┐
│  Response to Frontend│
│  - AI-generated text │
│  - Streaming updates │
└─────────────────────┘
```

### **3. Configuration Update Flow**

```
User Updates Settings
         │
         ▼
┌─────────────────────┐
│  Frontend (App.tsx) │
│  Settings Panel     │
│  - Enter API keys   │
│  - Select models    │
│  - Test connections │
└──────────┬──────────┘
           │ HTTP PUT /config/
           ▼
┌─────────────────────────┐
│  Backend (main.py)      │
│  Route: /config/        │
│  - Validate config      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Config Service             │
│  - Encrypt API keys         │
│    (AES-256)                │
│  - Generate master key      │
│    (if first time)          │
│  - Save to config.json      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  File System                │
│  ~/.local/share/InsightsLM/ │
│  ├── config.json (encrypted)│
│  └── .encryption_key        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────┐
│  Response to Frontend│
│  - Success/failure   │
└─────────────────────┘
```

---

## 🗄️ Database Design

### **SQLite Database**

**Location:** `~/.local/share/InsightsLM/insightslm.db`  
**Size:** ~780KB  
**ORM:** SQLAlchemy 2.0.44

#### **Tables**

**1. sources**
```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500),
    filename VARCHAR(500),
    filepath VARCHAR(1000),
    file_size INTEGER,
    duration FLOAT,
    language VARCHAR(10),
    transcription_text TEXT,
    transcription_segments JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Store uploaded/downloaded audio files and their transcriptions

**2. templates**
```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) UNIQUE NOT NULL,
    prompt_text TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Store custom report templates

**3. reports** (potential future table)
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES sources(id),
    template_id INTEGER REFERENCES templates(id),
    content TEXT,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Cache generated reports

#### **Entity-Relationship Diagram**

```
┌──────────────────┐         ┌──────────────────┐
│    sources       │         │    templates     │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ title            │         │ name (UNIQUE)    │
│ filename         │         │ prompt_text      │
│ filepath         │         │ language         │
│ file_size        │         │ created_at       │
│ duration         │         │ updated_at       │
│ language         │         └──────────────────┘
│ transcription    │                │
│ segments (JSON)  │                │
│ created_at       │                │
│ updated_at       │                │
└────────┬─────────┘                │
         │                          │
         │  ┌────────────────────┐  │
         └──│     reports        │──┘
            ├────────────────────┤
            │ id (PK)            │
            │ source_id (FK)     │
            │ template_id (FK)   │
            │ content            │
            │ model_used         │
            │ created_at         │
            └────────────────────┘
```

---

### **ChromaDB (Vector Database)**

**Location:** `~/.local/share/InsightsLM/chroma_db/`  
**Size:** ~11MB  
**Version:** 1.1.1

#### **Collections**

**transcription_chunks**
```python
{
    "documents": ["Transcript segment text..."],
    "embeddings": [[0.123, 0.456, ...]],  # 384-dimensional vectors
    "metadatas": [{
        "source_id": 123,
        "segment_index": 0,
        "start_time": 0.0,
        "end_time": 5.2,
        "speaker": "Speaker 1"
    }],
    "ids": ["source_123_segment_0"]
}
```

**Purpose:** Enable semantic search across transcriptions

**Embedding Model:** sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)

---

## 🔒 Security Architecture

### **1. API Key Encryption**

**Algorithm:** AES-256-CBC  
**Library:** pycryptodome 3.23.0

```python
# Encryption Flow
User enters API key
    ↓
Generate/Load master key (32 bytes)
    ↓
Derive encryption key using PBKDF2
    ↓
Encrypt API key with AES-256
    ↓
Store in config.json (encrypted)
```

**Master Key Storage:**
- Location: `~/.local/share/InsightsLM/.encryption_key`
- Permissions: `600` (owner read/write only)
- Generated once on first configuration

**Configuration File:**
- Location: `~/.local/share/InsightsLM/config.json`
- Permissions: `644` (owner read/write, others read)
- Contains only encrypted API keys

### **2. IPC Security (Electron)**

**Context Isolation:** Enabled  
**Node Integration:** Disabled in renderer  
**Preload Script:** Whitelisted APIs only

```typescript
// preload.ts exposes only safe APIs
contextBridge.exposeInMainWorld('electronAPI', {
    setBackendPort: (port: number) => ipcRenderer.send('set-backend-port', port),
    // No filesystem or process access exposed
});
```

### **3. File System Security**

**Temp Uploads:**
- Location: `~/.local/share/InsightsLM/temp_uploads/`
- Auto-cleanup after processing
- Random UUID filenames

**Static Files:**
- Served only from designated directory
- No directory traversal allowed
- Proper MIME type validation

### **4. Network Security**

**CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*"],  # Only local frontend
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Backend Binding:**
- Listens on `0.0.0.0:8000` (all interfaces)
- Only accessible via localhost (WSL2 networking)

---

## 🚀 Deployment Architecture

### **Development Environment**

```
┌─────────────────────────────────────────┐
│          Developer Machine              │
│  ┌────────────────────────────────────┐ │
│  │         Windows 10 Pro             │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │    Frontend Development      │  │ │
│  │  │  npm run start               │  │ │
│  │  │  (Hot reload enabled)        │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │       WSL2 (Ubuntu 24.04)          │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │    Backend Development       │  │ │
│  │  │  uvicorn main:app --reload   │  │ │
│  │  │  (Auto-reload enabled)       │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### **Production Build**

```
┌─────────────────────────────────────────┐
│        Electron Forge Build             │
│  ┌────────────────────────────────────┐ │
│  │  npm run make                      │ │
│  │  ├── Windows (.exe installer)     │ │
│  │  ├── macOS (.dmg)                 │ │
│  │  ├── Linux (.deb, .rpm)           │ │
│  │  └── Portable (.zip)              │ │
│  └────────────────────────────────────┘ │
│                                         │
│  Backend bundled with:                  │
│  ├── Python runtime                     │
│  ├── Virtual environment                │
│  ├── All dependencies                   │
│  └── Whisper model (large-v3)          │
└─────────────────────────────────────────┘
```

**Build Output:**
- Installers for Windows, macOS, Linux
- Self-contained executables
- Auto-update capable (Squirrel)

---

## 🤔 Design Decisions

### **1. Why Hybrid Architecture (Electron + FastAPI)?**

**Decision:** Separate frontend (Electron) from backend (FastAPI)

**Rationale:**
- **Performance:** Heavy AI processing doesn't block UI
- **Flexibility:** Can run backend on different machine/GPU server
- **Isolation:** Security boundary between UI and AI APIs
- **Development:** Independent frontend/backend development
- **Testing:** Easier to test API endpoints

**Trade-offs:**
- More complex than single-process app
- Requires backend lifecycle management
- Network communication overhead (minimal on localhost)

---

### **2. Why WSL2 for Backend?**

**Decision:** Run backend in WSL2 (Linux) instead of native Windows

**Rationale:**
- **GPU Support:** Better CUDA/PyTorch support in Linux
- **Performance:** Whisper runs faster on Linux
- **Dependencies:** Easier to install Python packages
- **Consistency:** Production-like environment
- **Tools:** Better CLI tools (ffmpeg, yt-dlp)

**Trade-offs:**
- Requires WSL2 installation
- Slightly more complex setup
- Windows-only deployment (currently)

---

### **3. Why SQLite + ChromaDB?**

**Decision:** Use SQLite for structured data, ChromaDB for vector search

**Rationale:**
- **SQLite:**
  - No server required
  - Single file database
  - Fast for small-medium datasets
  - Built-in Python support
  
- **ChromaDB:**
  - Lightweight vector database
  - No separate server needed
  - Easy integration with sentence-transformers
  - Excellent semantic search performance

**Trade-offs:**
- Not suitable for massive datasets (>10GB)
- No built-in replication/clustering
- Good enough for desktop application

---

### **4. Why Multi-Provider AI?**

**Decision:** Support 4 AI providers instead of single vendor

**Rationale:**
- **Choice:** Users select model based on needs
- **Cost:** Ollama is free, others are paid
- **Privacy:** Local models (Ollama) keep data private
- **Capability:** Different models excel at different tasks
- **Resilience:** Fallback if one provider is down

**Supported Providers:**
1. **Ollama** - Local, free, privacy-focused
2. **OpenAI** - GPT-4, best general performance
3. **Anthropic** - Claude, excellent for analysis
4. **Google Gemini** - Large context windows

---

### **5. Why AES-256 Encryption for API Keys?**

**Decision:** Encrypt API keys at rest with AES-256

**Rationale:**
- **Security:** Protect API keys from unauthorized access
- **Best Practice:** Industry standard encryption
- **Compliance:** Meets security requirements
- **Master Key:** Securely stored separately

**Implementation:**
```python
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

def encrypt_api_key(api_key: str, master_key: bytes) -> str:
    salt = get_random_bytes(16)
    key = PBKDF2(master_key, salt, dkLen=32)
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(api_key.encode(), AES.block_size))
    return base64.b64encode(salt + cipher.iv + ciphertext).decode()
```

---

### **6. Why React Over Vue/Angular?**

**Decision:** Use React for frontend UI

**Rationale:**
- **Ecosystem:** Largest component library ecosystem
- **Performance:** Virtual DOM is fast enough
- **Popularity:** Easier to find developers/resources
- **Integration:** Works well with Electron
- **TypeScript:** Excellent TypeScript support

---

### **7. Why Whisper large-v3?**

**Decision:** Use OpenAI Whisper large-v3 model for transcription

**Rationale:**
- **Accuracy:** Best open-source transcription model
- **Languages:** Supports 99 languages
- **Speed:** Fast enough with GPU (30x real-time)
- **Cost:** Free, open-source
- **Timestamps:** Provides word-level timestamps

**Trade-offs:**
- Large model (~3GB)
- Requires GPU for good performance
- CPU transcription is slow (~1x real-time)

---

## 🔮 Future Architectural Considerations

### **Potential Enhancements**

1. **Microservices Split**
   - Separate transcription service
   - Separate AI analysis service
   - Better scalability

2. **Cloud Sync**
   - Optional cloud backup
   - Multi-device sync
   - Shared templates

3. **Plugin System**
   - Third-party integrations
   - Custom AI providers
   - Export format plugins

4. **Real-time Collaboration**
   - Multi-user editing
   - Shared workspaces
   - Live transcription

5. **Mobile Clients**
   - React Native mobile app
   - Shared backend
   - Cloud sync required

6. **Advanced Analytics**
   - Sentiment analysis
   - Speaker diarization
   - Topic modeling
   - Trend analysis

---

## 📚 References

**Frontend:**
- Electron Documentation: https://www.electronjs.org/docs
- React Documentation: https://react.dev
- TypeScript Handbook: https://www.typescriptlang.org/docs

**Backend:**
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLAlchemy Documentation: https://docs.sqlalchemy.org
- ChromaDB Documentation: https://docs.trychroma.com

**AI/ML:**
- OpenAI Whisper: https://github.com/openai/whisper
- Ollama: https://ollama.ai
- Anthropic Claude: https://www.anthropic.com/claude
- Google Gemini: https://ai.google.dev

---

**Document Version:** 1.1  
**Last Updated:** November 4, 2025  
**Status:** ✅ Production-Ready - Updated with actual system information
