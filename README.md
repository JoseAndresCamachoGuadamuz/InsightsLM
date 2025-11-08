# InsightsLM

**AI-Powered Audio Transcription and Analysis Application**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/JoseAndresCamachoGuadamuz/InsightsLM)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.12.3-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19.2.0-61DAFB.svg)](https://react.dev/)
[![Electron](https://img.shields.io/badge/electron-38.2.2-47848F.svg)](https://www.electronjs.org/)

**Version:** 1.1 (Updated with actual system information)  
**Last Updated:** November 4, 2025

---

## 📖 Overview

InsightsLM is a powerful desktop application that combines state-of-the-art AI technologies to transcribe, analyze, and extract insights from audio content. Whether you're processing meetings, interviews, lectures, or podcasts, InsightsLM provides accurate transcriptions and intelligent analysis using multiple AI providers.

### ✨ Key Features

- **🎙️ Accurate Transcription** - OpenAI Whisper large-v3 model with 99-language support
- **🤖 Multi-Provider AI** - Choose from 104+ models across 4 providers (Ollama, OpenAI, Anthropic, Google Gemini)
- **💬 Interactive Q&A** - Ask questions about your audio content
- **📄 Custom Reports** - Generate reports using customizable templates
- **🔍 Semantic Search** - Find relevant content using vector embeddings
- **🔐 Secure & Private** - All data stored locally with AES-256 encryption
- **📤 Multiple Export Formats** - Export to TXT, MD, DOCX, PDF, JSON
- **🌍 Multi-Language** - Automatic language detection and translation

---

## 🖼️ Screenshots

*(Coming soon - Add screenshots of the application interface)*

---

## 🚀 Quick Start

### Prerequisites

**Frontend (Windows):**
- Windows 10 or later
- Node.js **v22.17.1** or higher
- npm **11.6.2** or higher
- Git

**Backend (WSL2/Linux):**
- WSL2 with Ubuntu 24.04 LTS
- Python **3.12.3** or higher
- pip **24.0** or higher
- CUDA Toolkit (optional, for GPU acceleration)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/JoseAndresCamachoGuadamuz/InsightsLM.git
cd InsightsLM

# 2. Set up backend (in WSL2)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set up frontend (in Windows)
cd ../frontend
npm install

# 4. Start the application
npm start
```

For detailed installation instructions, see [SETUP_GUIDE.md](./docs/SETUP_GUIDE.md).

---

## 💻 Technology Stack

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Electron** | 38.2.2 | Desktop application framework |
| **React** | 19.2.0 | UI library |
| **TypeScript** | 4.5.5 | Type safety and better DX |
| **Vite** | 5.4.21 | Fast build tool |
| **Axios** | 1.12.2 | HTTP client |

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12.3 | Runtime environment |
| **FastAPI** | 0.118.3 | High-performance web framework |
| **OpenAI Whisper** | 20250625 | Speech-to-text transcription |
| **SQLAlchemy** | 2.0.44 | Database ORM |
| **ChromaDB** | 1.1.1 | Vector database for semantic search |
| **Pydantic** | 2.12.0 | Data validation |

### AI Providers

| Provider | Library Version | Models | Features |
|----------|----------------|--------|----------|
| **Ollama** | 0.6.0 | 45+ local models | Free, private, no API key |
| **OpenAI** | 2.3.0 | 21 models (GPT-4o, GPT-3.5) | Best general performance |
| **Anthropic** | 0.69.0 | 9 models (Claude 4, Claude 3.5) | Excellent for analysis |
| **Google Gemini** | 0.8.5 | 29+ models | Large context windows (2M tokens) |

**Total Available Models:** 104+

---

## 📚 Documentation

- **[User Guide](./docs/USER_GUIDE.md)** - How to use InsightsLM
- **[Setup Guide](./docs/SETUP_GUIDE.md)** - Detailed installation instructions
- **[API Reference](./docs/API_REFERENCE.md)** - Backend API documentation (22 endpoints)
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and architecture
- **[Contributing](./docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Code Standards](./docs/CODE_STANDARDS.md)** - Coding and documentation standards

---

## 🎯 Use Cases

### 🎤 **Meeting Transcription**
Automatically transcribe meetings with timestamps, generate summaries, and extract action items.

### 🎓 **Lecture Notes**
Convert recorded lectures into searchable transcripts with key concept extraction and Q&A.

### 🎙️ **Podcast Analysis**
Download and analyze podcast episodes, extract topics, and generate episode summaries.

### 💼 **Interview Processing**
Transcribe interviews, identify themes, and generate comprehensive reports.

### 📱 **Content Creation**
Transcribe audio for blog posts, articles, and social media content.

---

## 🔐 Security & Privacy

InsightsLM prioritizes your data security and privacy:

- **🏠 Local-First** - All data stored on your machine
- **🔒 AES-256 Encryption** - API keys encrypted at rest
- **🚫 No Cloud Storage** - Your audio never leaves your device (except to AI providers you choose)
- **🛡️ Secure IPC** - Isolated frontend-backend communication
- **👤 User Control** - You decide which AI providers to use

---

## 🌟 Key Capabilities

### Transcription
- **Accuracy** - 95%+ accuracy with Whisper large-v3
- **Speed** - 30x real-time with GPU, 1x with CPU
- **Languages** - 99 languages supported
- **Formats** - MP3, WAV, M4A, FLAC, MP4, AVI, MOV, MKV
- **Max Size** - 500MB per file
- **Timestamps** - Word-level timestamp support

### AI Analysis
- **Summarization** - Concise summaries of any length audio
- **Q&A** - Interactive question-answering about content
- **Reports** - Custom reports using templates
- **Audio Overview** - Comprehensive content overviews
- **Semantic Search** - Find relevant segments using natural language

### Export Options
- **TXT** - Plain text format
- **MD** - Markdown for documentation
- **DOCX** - Microsoft Word documents
- **PDF** - Professional PDFs for distribution
- **JSON** - Structured data for integrations

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│         ELECTRON FRONTEND                │
│  React (19.2.0) + TypeScript (4.5.5)    │
│  Main Process (824 lines)                │
│  App Component (1,848 lines)             │
└──────────────┬───────────────────────────┘
               │ HTTP REST API (localhost:8000)
               │
┌──────────────▼───────────────────────────┐
│         FASTAPI BACKEND                  │
│  Python (3.12.3) + FastAPI (0.118.3)    │
│  22 API Endpoints (911 lines)            │
│  ├─ Transcription Service (Whisper)     │
│  ├─ LLM Service (Multi-provider)         │
│  ├─ Vector DB Service (ChromaDB)         │
│  ├─ Config Service (AES-256)             │
│  └─ Export Service (Multiple formats)    │
└──────────────┬───────────────────────────┘
               │
    ┌──────────┴──────────┬───────────────┐
    │                     │               │
┌───▼───┐         ┌──────▼──────┐   ┌───▼────┐
│SQLite │         │  ChromaDB   │   │ Whisper│
│Database│         │ (11MB)      │   │large-v3│
│(780KB)│         └─────────────┘   └────────┘
└───────┘

External AI Providers:
┌─────────┬──────────┬───────────┬─────────┐
│ Ollama  │ OpenAI   │ Anthropic │ Google  │
│ (Local) │ (Cloud)  │ (Cloud)   │(Cloud)  │
└─────────┴──────────┴───────────┴─────────┘
```

For detailed architecture information, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## 📊 Project Statistics

**Codebase:**
- Frontend: ~2,900 lines of TypeScript/TSX
- Backend: ~1,400 lines of Python
- Total: ~4,300 lines of code

**Dependencies:**
- Frontend: 25 npm packages
- Backend: 85 Python packages

**Features:**
- 22 API endpoints
- 104+ AI models supported
- 7 backend services
- 5 export formats
- 99 languages supported

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

**Development Setup:**
```bash
# Frontend development (Windows)
cd frontend
npm run start  # Hot reload enabled

# Backend development (WSL2)
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Coding Standards:**
- Frontend: TypeScript with TSDoc comments
- Backend: Python with Google-style docstrings
- See [CODE_STANDARDS.md](./docs/CODE_STANDARDS.md) for details

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - Best-in-class speech recognition
- **FastAPI** - Modern, high-performance Python web framework
- **Electron** - Cross-platform desktop applications
- **React** - Powerful UI library
- **ChromaDB** - Simple, effective vector database
- **Ollama** - Local AI model inference
- All the amazing open-source contributors

---

## 🛠️ Development Tools

This application was developed with coding assistance from AI tools, including:

- **Claude** (Anthropic) - Code architecture and implementation
- **ChatGPT** (OpenAI) - Problem-solving and debugging
- **Google Gemini** (Google) - Code review and optimization
- **Perplexity** (Perplexity AI) - Research and documentation

These tools assisted with code generation, documentation, debugging, and implementation guidance. All design decisions, architecture choices, and final code review were performed by the human author.

---

## 📞 Support

- **Documentation:** [docs/](./docs/)
- **Issues:** [GitHub Issues](https://github.com/JoseAndresCamachoGuadamuz/InsightsLM/issues)
- **Email:** joseandrescamachoguadamuz@gmail.com

---

## 🗺️ Roadmap

### Version 1.1 (Current)
- ✅ Multi-provider AI support (104 models)
- ✅ Dynamic model loading
- ✅ Enhanced error handling
- ✅ User-friendly error messages

### Version 1.2 (Planned - Q1 2026)
- ⏳ Speaker diarization (who said what)
- ⏳ Real-time transcription
- ⏳ Audio editing capabilities
- ⏳ Batch processing

### Version 2.0 (Planned - Q2 2026)
- ⏳ Cloud sync (optional)
- ⏳ Mobile app (React Native)
- ⏳ Collaborative features
- ⏳ Advanced analytics dashboard

---

## ⭐ Star History

If you find InsightsLM useful, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=JoseAndresCamachoGuadamuz/InsightsLM&type=Date)](https://star-history.com/#JoseAndresCamachoGuadamuz/InsightsLM&Date)

---

## 📸 Demo

*(Coming soon - Add GIF or video demo)*

---

## 👤 Author

**José Andrés Camacho Guadamuz**

- 🌐 GitHub: [@JoseAndresCamachoGuadamuz](https://github.com/JoseAndresCamachoGuadamuz)
- 📧 Email: [joseandrescamachoguadamuz@gmail.com](mailto:joseandrescamachoguadamuz@gmail.com)
- 💼 LinkedIn: [linkedin.com/in/jose-andres-camacho-guadamuz](https://linkedin.com/in/jose-andres-camacho-guadamuz/)

---

**Built with ❤️ using AI and open-source technologies**

**Version:** 1.1  
**Last Updated:** November 4, 2025  
**Status:** ✅ Production-Ready - Updated with actual system information
