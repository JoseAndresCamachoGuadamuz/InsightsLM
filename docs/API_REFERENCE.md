# API Reference

**InsightsLM Backend API Documentation**

**Version:** 1.1 (Updated with actual endpoint information)  
**Base URL:** `http://localhost:8000`  
**Last Updated:** November 4, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Health & Testing](#health--testing)
   - [Models](#models)
   - [Transcription](#transcription)
   - [Templates](#templates)
   - [Analysis](#analysis)
   - [Export & Configuration](#export--configuration)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Code Examples](#code-examples)
7. [Additional Resources](#additional-resources)

---

## 🎯 Overview

The InsightsLM backend provides a RESTful API built with **FastAPI 0.118.3** running on **Python 3.12.3**. The API handles:
- Audio transcription using OpenAI Whisper
- AI-powered content analysis (4 providers)
- Template management
- Report generation
- Export functionality
- Configuration management

**Total Endpoints:** 22  
**Server:** Uvicorn 0.37.0 (ASGI)  
**Documentation:** Available at `http://localhost:8000/docs` (Swagger UI)

---

## 🔐 Authentication

**Current Implementation:** No authentication required (localhost-only)

The API is designed to run locally and is accessible only from `http://localhost`. All requests from the Electron frontend are trusted.

**Future Enhancement:** API key authentication for remote deployments

---

## 📡 API Endpoints

### **Health & Testing** (3 endpoints)

#### 1. **Health Check**

**Endpoint:** `GET /health`  
**Summary:** Health check endpoint  
**Description:** Verify backend is running and responsive

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-04T16:24:12Z"
}
```

**Status Codes:**
- `200 OK` - Backend is healthy
- `503 Service Unavailable` - Backend is not ready

**Example:**
```bash
curl http://localhost:8000/health
```

---

#### 2. **Test All API Connections**

**Endpoint:** `GET /test-api/status`  
**Summary:** Test all API connections and return comprehensive status  
**Description:** Tests connectivity to all configured AI providers (Ollama, OpenAI, Anthropic, Google Gemini)

**Response:**
```json
{
  "ollama": {
    "available": true,
    "models_count": 45,
    "base_url": "http://localhost:11434",
    "error": null
  },
  "openai": {
    "available": true,
    "models_count": 21,
    "error": null
  },
  "anthropic": {
    "available": false,
    "models_count": 0,
    "error": "Invalid API key"
  },
  "google": {
    "available": true,
    "models_count": 29,
    "error": null
  }
}
```

**Status Codes:**
- `200 OK` - Test completed (check individual provider status)

**Example:**
```typescript
const response = await api.getAllApiStatus();
console.log(response.data);
```

---

#### 3. **Test Single Provider**

**Endpoint:** `POST /test-api/{provider}`  
**Summary:** Test API connection for a specific provider  
**Parameters:**
- `provider` (path) - Provider name: `ollama`, `openai`, `anthropic`, or `google`

**Response:**
```json
{
  "provider": "openai",
  "available": true,
  "models_count": 21,
  "message": "Connection successful",
  "error": null
}
```

**Status Codes:**
- `200 OK` - Test completed
- `400 Bad Request` - Invalid provider name
- `500 Internal Server Error` - Test failed

**Example:**
```bash
curl -X POST http://localhost:8000/test-api/openai
```

---

### **Models** (5 endpoints)

#### 4. **Get Ollama Models**

**Endpoint:** `GET /models/ollama`  
**Summary:** Get available Ollama models  
**Description:** Returns list of locally available Ollama models

**Response:**
```json
{
  "provider": "ollama",
  "models": [
    {
      "model_key": "ollama/llama3.2",
      "name": "Llama 3.2",
      "context_length": 128000
    },
    {
      "model_key": "ollama/qwen2.5:latest",
      "name": "Qwen 2.5",
      "context_length": 32000
    }
  ],
  "count": 45,
  "available": true,
  "error": null
}
```

**Status Codes:**
- `200 OK` - Models retrieved successfully
- `503 Service Unavailable` - Ollama not running

**Example:**
```typescript
const response = await api.getOllamaModels();
const models = response.data.models;
```

---

#### 5. **Get OpenAI Models**

**Endpoint:** `GET /models/openai`  
**Summary:** Get available OpenAI models  
**Description:** Returns list of OpenAI models accessible with configured API key

**Response:**
```json
{
  "provider": "openai",
  "models": [
    {
      "model_key": "openai/gpt-4o",
      "name": "GPT-4o",
      "context_length": 128000
    },
    {
      "model_key": "openai/gpt-4o-mini",
      "name": "GPT-4o Mini",
      "context_length": 128000
    },
    {
      "model_key": "openai/gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "context_length": 16000
    }
  ],
  "count": 21,
  "available": true,
  "error": null
}
```

**Status Codes:**
- `200 OK` - Models retrieved
- `401 Unauthorized` - Invalid API key
- `500 Internal Server Error` - API error

---

#### 6. **Get Anthropic Models**

**Endpoint:** `GET /models/anthropic`  
**Summary:** Get available Anthropic models  
**Description:** Returns list of Anthropic Claude models

**Response:**
```json
{
  "provider": "anthropic",
  "models": [
    {
      "model_key": "anthropic/claude-sonnet-4",
      "name": "Claude Sonnet 4",
      "context_length": 200000
    },
    {
      "model_key": "anthropic/claude-opus-4",
      "name": "Claude Opus 4",
      "context_length": 200000
    },
    {
      "model_key": "anthropic/claude-3-5-sonnet-20241022",
      "name": "Claude 3.5 Sonnet",
      "context_length": 200000
    }
  ],
  "count": 9,
  "available": true,
  "error": null
}
```

---

#### 7. **Get Google Gemini Models**

**Endpoint:** `GET /models/google`  
**Summary:** Get available Google Gemini models  
**Description:** Returns list of Google Gemini models

**Response:**
```json
{
  "provider": "google",
  "models": [
    {
      "model_key": "google/gemini-1.5-pro",
      "name": "Gemini 1.5 Pro",
      "context_length": 2000000
    },
    {
      "model_key": "google/gemini-1.5-flash",
      "name": "Gemini 1.5 Flash",
      "context_length": 1000000
    }
  ],
  "count": 29,
  "available": true,
  "error": null
}
```

---

#### 8. **Get All Models**

**Endpoint:** `GET /models/all`  
**Summary:** Get all available models from all providers  
**Description:** Aggregates models from all configured providers

**Response:**
```json
{
  "ollama": {
    "provider": "ollama",
    "models": [...],
    "count": 45,
    "available": true
  },
  "openai": {
    "provider": "openai",
    "models": [...],
    "count": 21,
    "available": true
  },
  "anthropic": {
    "provider": "anthropic",
    "models": [...],
    "count": 9,
    "available": true
  },
  "google": {
    "provider": "google",
    "models": [...],
    "count": 29,
    "available": true
  },
  "total_models": 104
}
```

**Example:**
```typescript
const response = await api.getAllModels();
const totalModels = response.data.total_models; // 104
```

---

### **Transcription** (4 endpoints)

#### 9. **Upload File**

**Endpoint:** `POST /upload/`  
**Summary:** Upload a file and process it  
**Description:** Upload an audio/video file for transcription

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file` (required) - Audio/video file

**Supported Formats:**
- Audio: MP3, WAV, M4A, FLAC, OGG, AAC
- Video: MP4, AVI, MOV, MKV (audio extracted)

**Response:**
```json
{
  "source_id": 123,
  "title": "Meeting Recording.mp3",
  "filename": "Meeting Recording.mp3",
  "file_size": 5242880,
  "duration": 300.5,
  "language": "en",
  "transcription": {
    "text": "Full transcript text...",
    "segments": [
      {
        "id": 0,
        "start": 0.0,
        "end": 5.2,
        "text": "Hello and welcome to the meeting."
      },
      {
        "id": 1,
        "start": 5.2,
        "end": 12.8,
        "text": "Today we'll discuss the quarterly results."
      }
    ]
  },
  "created_at": "2025-11-04T16:24:12Z"
}
```

**Status Codes:**
- `200 OK` - File processed successfully
- `400 Bad Request` - Invalid file format
- `413 Payload Too Large` - File too large (>500MB)
- `500 Internal Server Error` - Transcription failed

**Example:**
```typescript
const formData = new FormData();
formData.append('file', audioFile);

const response = await api.uploadAndTranscribe(formData);
const sourceId = response.data.source_id;
```

---

#### 10. **Download from URL**

**Endpoint:** `POST /download/`  
**Summary:** Download a file from a URL and process it  
**Description:** Download audio from URL (supports YouTube, podcasts, etc.) and transcribe

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:** Same as `/upload/` endpoint

**Supported URLs:**
- YouTube videos
- Direct audio file URLs
- Podcast RSS feeds
- SoundCloud
- Many other platforms (via yt-dlp)

**Status Codes:**
- `200 OK` - Download and processing successful
- `400 Bad Request` - Invalid URL
- `404 Not Found` - URL not accessible
- `500 Internal Server Error` - Download or transcription failed

**Example:**
```typescript
const response = await api.transcribeFromUrl('https://example.com/audio.mp3');
```

---

#### 11. **List Sources**

**Endpoint:** `GET /sources/`  
**Summary:** List all sources  
**Description:** Get all transcribed audio sources

**Query Parameters:**
- `limit` (optional) - Maximum number of results (default: 100)
- `offset` (optional) - Number of results to skip (default: 0)

**Response:**
```json
{
  "sources": [
    {
      "id": 123,
      "title": "Meeting Recording.mp3",
      "filename": "Meeting Recording.mp3",
      "duration": 300.5,
      "language": "en",
      "created_at": "2025-11-04T16:24:12Z"
    },
    {
      "id": 122,
      "title": "Interview.mp3",
      "filename": "Interview.mp3",
      "duration": 1800.0,
      "language": "en",
      "created_at": "2025-11-03T10:15:30Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**Example:**
```bash
curl http://localhost:8000/sources/?limit=10&offset=0
```

---

#### 12. **Get Transcription**

**Endpoint:** `GET /sources/{source_id}/transcription/`  
**Summary:** Get the transcription for a source  
**Parameters:**
- `source_id` (path, required) - Source ID

**Response:**
```json
{
  "source_id": 123,
  "title": "Meeting Recording.mp3",
  "transcription": {
    "text": "Full transcript...",
    "segments": [
      {
        "id": 0,
        "start": 0.0,
        "end": 5.2,
        "text": "Segment text..."
      }
    ]
  },
  "language": "en",
  "duration": 300.5
}
```

**Status Codes:**
- `200 OK` - Transcription retrieved
- `404 Not Found` - Source not found

---

### **Templates** (4 endpoints)

#### 13. **Get All Templates**

**Endpoint:** `GET /templates/`  
**Summary:** Get all templates  
**Description:** Retrieve all custom report templates

**Response:**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "Executive Summary",
      "prompt_text": "Provide a concise executive summary of the key points...",
      "language": "en",
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Action Items",
      "prompt_text": "Extract all action items and tasks mentioned...",
      "language": "en",
      "created_at": "2025-11-02T14:30:00Z",
      "updated_at": "2025-11-02T14:30:00Z"
    }
  ],
  "count": 2
}
```

**Status Codes:**
- `200 OK` - Templates retrieved

---

#### 14. **Create Template**

**Endpoint:** `POST /templates/`  
**Summary:** Create a new template  
**Description:** Create a custom report template

**Request:**
```json
{
  "name": "Meeting Notes",
  "prompt_text": "Summarize this meeting transcript with: 1) Key discussion points, 2) Decisions made, 3) Action items",
  "language": "en"
}
```

**Response:**
```json
{
  "id": 3,
  "name": "Meeting Notes",
  "prompt_text": "Summarize this meeting transcript...",
  "language": "en",
  "created_at": "2025-11-04T16:30:00Z",
  "updated_at": "2025-11-04T16:30:00Z"
}
```

**Status Codes:**
- `201 Created` - Template created
- `400 Bad Request` - Invalid request body
- `409 Conflict` - Template name already exists

**Example:**
```typescript
const response = await api.createTemplate(
  'Meeting Notes',
  'Summarize this meeting...',
  'en'
);
```

---

#### 15. **Update Template**

**Endpoint:** `PUT /templates/{template_id}`  
**Summary:** Update a template  
**Parameters:**
- `template_id` (path, required) - Template ID

**Request:**
```json
{
  "name": "Updated Template Name",
  "prompt_text": "Updated prompt text...",
  "language": "en"
}
```

**Response:** Updated template object (same as create response)

**Status Codes:**
- `200 OK` - Template updated
- `404 Not Found` - Template not found
- `409 Conflict` - New name conflicts with existing template

---

#### 16. **Delete Template**

**Endpoint:** `DELETE /templates/{template_id}`  
**Summary:** Delete a template  
**Parameters:**
- `template_id` (path, required) - Template ID

**Response:** 204 No Content

**Status Codes:**
- `204 No Content` - Template deleted successfully
- `404 Not Found` - Template not found

**Example:**
```typescript
await api.deleteTemplate(3);
```

---

### **Analysis** (4 endpoints)

#### 17. **Generate Report**

**Endpoint:** `POST /report/`  
**Summary:** Generate a report for a source using a template  
**Description:** Apply a template to generate a custom report

**Request:**
```json
{
  "source_id": 123,
  "template_id": 1,
  "model_key": "ollama/llama3.2"
}
```

**Response:**
```json
{
  "report_id": 456,
  "source_id": 123,
  "template_id": 1,
  "content": "Executive Summary:\n\nKey Points:\n1. Project is on track...\n2. Budget remains within allocated limits...",
  "model_used": "ollama/llama3.2",
  "generated_at": "2025-11-04T16:35:00Z"
}
```

**Status Codes:**
- `200 OK` - Report generated
- `400 Bad Request` - Invalid request
- `404 Not Found` - Source or template not found
- `500 Internal Server Error` - AI generation failed

**Example:**
```typescript
const response = await api.runReport(123, 1, 'ollama/llama3.2');
const report = response.data.content;
```

---

#### 18. **Generate Summary**

**Endpoint:** `POST /summarize/`  
**Summary:** Generate a summary for a source  
**Description:** Create an AI-powered summary of the transcription

**Request:**
```json
{
  "source_id": 123,
  "model_key": "openai/gpt-4o",
  "max_length": 500
}
```

**Response:**
```json
{
  "source_id": 123,
  "summary": "This meeting discussed the Q4 financial results, which exceeded expectations by 15%. The team reviewed the successful product launch and decided to expand marketing efforts in Q1.",
  "model_used": "openai/gpt-4o",
  "word_count": 32,
  "generated_at": "2025-11-04T16:40:00Z"
}
```

**Status Codes:**
- `200 OK` - Summary generated
- `400 Bad Request` - Invalid request
- `404 Not Found` - Source not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - AI generation failed

**Example:**
```typescript
const response = await api.getSummary(123, 'openai/gpt-4o');
const summary = response.data.summary;
```

---

#### 19. **Ask Question (Chat)**

**Endpoint:** `POST /query/`  
**Summary:** Ask a question about a source  
**Description:** Interactive Q&A about the transcription content

**Request:**
```json
{
  "source_id": 123,
  "query": "What were the main action items discussed in the meeting?",
  "model_key": "anthropic/claude-sonnet-4"
}
```

**Response:**
```json
{
  "source_id": 123,
  "query": "What were the main action items discussed in the meeting?",
  "answer": "The main action items discussed were:\n\n1. John to prepare Q4 financial presentation by Friday\n2. Sarah to schedule follow-up meeting with clients\n3. Team to review and approve the new marketing proposal by end of week",
  "model_used": "anthropic/claude-sonnet-4",
  "confidence": 0.95,
  "generated_at": "2025-11-04T16:45:00Z"
}
```

**Status Codes:**
- `200 OK` - Answer generated
- `400 Bad Request` - Invalid request or empty query
- `404 Not Found` - Source not found
- `500 Internal Server Error` - AI query failed

**Example:**
```typescript
const response = await api.postQuery(
  123,
  'What were the key decisions made?',
  'anthropic/claude-sonnet-4'
);
```

---

#### 20. **Generate Audio Overview**

**Endpoint:** `POST /audio-overview/`  
**Summary:** Generate an audio overview for a source  
**Description:** Create a comprehensive audio overview using AI

**Request:**
```json
{
  "source_id": 123,
  "model_key": "google/gemini-1.5-pro",
  "include_speakers": true
}
```

**Response:**
```json
{
  "source_id": 123,
  "overview": {
    "title": "Q4 Financial Review Meeting",
    "duration": "5 minutes 30 seconds",
    "summary": "Meeting to review Q4 financial performance...",
    "topics": [
      "Financial Results",
      "Product Launch Review",
      "Q1 Planning"
    ],
    "speakers": 3,
    "key_points": [
      "Revenue exceeded targets by 15%",
      "Product launch was successful",
      "Expanding marketing budget for Q1"
    ]
  },
  "model_used": "google/gemini-1.5-pro",
  "generated_at": "2025-11-04T16:50:00Z"
}
```

**Status Codes:**
- `200 OK` - Overview generated
- `400 Bad Request` - Invalid request
- `404 Not Found` - Source not found
- `500 Internal Server Error` - Generation failed

**Example:**
```typescript
const response = await api.getAudioOverview(123, 'google/gemini-1.5-pro');
const overview = response.data.overview;
```

---

### **Export & Configuration** (3 endpoints)

#### 21. **Export Content**

**Endpoint:** `POST /export/`  
**Summary:** Export content to a file  
**Description:** Export transcription, summary, or report to various formats

**Request:**
```json
{
  "source_id": 123,
  "content_type": "transcription",
  "format": "docx",
  "include_timestamps": true
}
```

**Parameters:**
- `source_id` (required) - Source ID
- `content_type` (required) - `transcription`, `summary`, or `report`
- `format` (required) - `txt`, `md`, `docx`, `pdf`, or `json`
- `include_timestamps` (optional) - Include timestamps (default: false)
- `report_id` (optional) - Required if content_type is `report`

**Response:**
```json
{
  "file_path": "/tmp/exports/meeting_transcript_20251104.docx",
  "file_size": 45678,
  "format": "docx",
  "download_url": "http://localhost:8000/static/exports/meeting_transcript_20251104.docx"
}
```

**Supported Formats:**

| Format | Extension | Use Case |
|--------|-----------|----------|
| **TXT** | .txt | Plain text, simple sharing |
| **Markdown** | .md | GitHub, documentation |
| **Word** | .docx | Business reports, editing |
| **PDF** | .pdf | Final distribution, printing |
| **JSON** | .json | API integration, data processing |

**Status Codes:**
- `200 OK` - Export successful
- `400 Bad Request` - Invalid format or content type
- `404 Not Found` - Source not found
- `500 Internal Server Error` - Export failed

**Example:**
```typescript
const response = await api.exportContent({
  source_id: 123,
  content_type: 'transcription',
  format: 'docx',
  include_timestamps: true
});

const downloadUrl = response.data.download_url;
```

---

#### 22. **Get Configuration**

**Endpoint:** `GET /config/`  
**Summary:** Get the current application configuration  
**Description:** Retrieve encrypted configuration (API keys are redacted)

**Response:**
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

**Note:** API keys are never returned in plain text. They're stored encrypted with AES-256.

**Status Codes:**
- `200 OK` - Configuration retrieved

---

#### 23. **Update Configuration**

**Endpoint:** `PUT /config/`  
**Summary:** Update the application configuration  
**Description:** Update API keys, models, and other settings

**Request:**
```json
{
  "openai_api_key": "sk-proj-...",
  "openai_model": "gpt-4o",
  "anthropic_api_key": "sk-ant-...",
  "default_provider": "openai"
}
```

**Note:** API keys are automatically encrypted before storage

**Response:** 204 No Content

**Status Codes:**
- `204 No Content` - Configuration updated successfully
- `400 Bad Request` - Invalid configuration
- `500 Internal Server Error` - Encryption or save failed

**Example:**
```typescript
await api.updateConfig({
  openai_api_key: 'sk-proj-...',
  default_provider: 'openai'
});
```

---

## ⚠️ Error Handling

### **Error Response Format**

All errors follow a consistent format:

```json
{
  "detail": {
    "error": "Error type",
    "message": "User-friendly error message",
    "suggestion": "Actionable suggestion for fixing the error",
    "provider": "openai",
    "code": "API_KEY_INVALID"
  }
}
```

### **Common Error Codes**

| HTTP Status | Error Code | Description | Solution |
|------------|------------|-------------|----------|
| 400 | `INVALID_REQUEST` | Malformed request body | Check request schema |
| 401 | `API_KEY_INVALID` | Invalid AI provider API key | Verify API key in settings |
| 404 | `SOURCE_NOT_FOUND` | Source doesn't exist | Check source_id |
| 404 | `TEMPLATE_NOT_FOUND` | Template doesn't exist | Check template_id |
| 413 | `FILE_TOO_LARGE` | File exceeds size limit | Compress or split file |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| 500 | `TRANSCRIPTION_FAILED` | Whisper error | Check audio format |
| 500 | `AI_GENERATION_FAILED` | AI provider error | Check provider status |
| 503 | `SERVICE_UNAVAILABLE` | Backend service down | Restart backend |

### **Provider-Specific Errors**

**Ollama:**
```json
{
  "error": "OLLAMA_UNAVAILABLE",
  "message": "Could not connect to Ollama",
  "suggestion": "Start Ollama with: ollama serve"
}
```

**OpenAI:**
```json
{
  "error": "OPENAI_API_KEY_INVALID",
  "message": "Invalid OpenAI API key",
  "suggestion": "Get your API key from: https://platform.openai.com/api-keys"
}
```

**Anthropic:**
```json
{
  "error": "ANTHROPIC_RATE_LIMIT",
  "message": "Rate limit exceeded",
  "suggestion": "Wait 60 seconds and try again"
}
```

**Google:**
```json
{
  "error": "GOOGLE_QUOTA_EXCEEDED",
  "message": "API quota exceeded",
  "suggestion": "Check your quota at: https://console.cloud.google.com/"
}
```

---

## 🚦 Rate Limiting

**Current Implementation:** No rate limiting (local use only)

**Recommended Limits for Production:**
- `/upload/`: 10 requests per hour
- `/download/`: 20 requests per hour
- `/summarize/`, `/query/`: 100 requests per hour
- `/models/*`, `/config/`: No limit

**AI Provider Limits:**
- **OpenAI:** 3,500 requests/min (tier-based)
- **Anthropic:** 50 requests/min (free tier)
- **Google Gemini:** 15 requests/min (free tier)
- **Ollama:** No limit (local)

---

## 💻 Code Examples

### **TypeScript (Frontend)**

**Complete Upload and Analyze Workflow:**

```typescript
import * as api from './services/api';

async function processAudio(file: File) {
  try {
    // 1. Upload and transcribe
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadResponse = await api.uploadAndTranscribe(formData);
    const sourceId = uploadResponse.data.source_id;
    
    console.log('Transcription:', uploadResponse.data.transcription.text);
    
    // 2. Generate summary
    const summaryResponse = await api.getSummary(sourceId, 'openai/gpt-4o');
    console.log('Summary:', summaryResponse.data.summary);
    
    // 3. Ask questions
    const queryResponse = await api.postQuery(
      sourceId,
      'What are the main topics discussed?',
      'openai/gpt-4o'
    );
    console.log('Answer:', queryResponse.data.answer);
    
    // 4. Export to Word
    const exportResponse = await api.exportContent({
      source_id: sourceId,
      content_type: 'transcription',
      format: 'docx',
      include_timestamps: true
    });
    
    // Download the file
    window.open(exportResponse.data.download_url, '_blank');
    
  } catch (error) {
    if (error.response?.data?.detail) {
      console.error('Error:', error.response.data.detail.message);
      console.error('Suggestion:', error.response.data.detail.suggestion);
    }
  }
}
```

---

### **Python (Direct API Calls)**

**Example: Upload and Query:**

```python
import requests

BASE_URL = "http://localhost:8000"

def process_audio(file_path: str):
    # 1. Upload file
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload/", files=files)
        response.raise_for_status()
        data = response.json()
        source_id = data['source_id']
        
    print(f"Transcription: {data['transcription']['text']}")
    
    # 2. Generate summary
    summary_response = requests.post(
        f"{BASE_URL}/summarize/",
        json={
            "source_id": source_id,
            "model_key": "ollama/llama3.2"
        }
    )
    summary = summary_response.json()['summary']
    print(f"Summary: {summary}")
    
    # 3. Ask question
    query_response = requests.post(
        f"{BASE_URL}/query/",
        json={
            "source_id": source_id,
            "query": "What were the action items?",
            "model_key": "ollama/llama3.2"
        }
    )
    answer = query_response.json()['answer']
    print(f"Answer: {answer}")

# Usage
process_audio("/path/to/audio.mp3")
```

---

### **cURL Examples**

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Upload File:**
```bash
curl -X POST http://localhost:8000/upload/ \
  -F "file=@meeting.mp3"
```

**Get All Models:**
```bash
curl http://localhost:8000/models/all
```

**Generate Summary:**
```bash
curl -X POST http://localhost:8000/summarize/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": 123,
    "model_key": "ollama/llama3.2"
  }'
```

**Test API Connection:**
```bash
curl -X POST http://localhost:8000/test-api/openai
```

**Update Configuration:**
```bash
curl -X PUT http://localhost:8000/config/ \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "sk-proj-...",
    "default_provider": "openai"
  }'
```

---

## 📚 Additional Resources

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Source Code:**
- Backend: `~/InsightsLM/backend/main.py` (911 lines)
- Schemas: `~/InsightsLM/backend/schemas.py`
- Services: `~/InsightsLM/backend/services/`

**Related Documentation:**
- [Architecture Document](./ARCHITECTURE.md)
- [Setup Guide](./SETUP_GUIDE.md)
- [User Guide](./USER_GUIDE.md)

---

**API Version:** 1.1  
**Last Updated:** November 4, 2025  
**Status:** ✅ Production-Ready - All 22 endpoints verified and documented
