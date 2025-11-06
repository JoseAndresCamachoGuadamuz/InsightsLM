# InsightsLM User Guide

**Complete Guide to Using InsightsLM Features**

This guide will teach you how to use all of InsightsLM's features, from basic transcription to advanced report generation.

---

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Transcribing Audio/Video](#transcribing-audiovideo)
4. [Viewing and Searching Transcripts](#viewing-and-searching-transcripts)
5. [Generating Summaries](#generating-summaries)
6. [Creating Audio Overviews](#creating-audio-overviews)
7. [Interactive Chat (Q&A)](#interactive-chat-qa)
8. [Custom Reports](#custom-reports)
9. [Settings and Configuration](#settings-and-configuration)
10. [Exporting Content](#exporting-content)
11. [Tips and Best Practices](#tips-and-best-practices)
12. [FAQ](#faq)
13. [Getting Help](#getting-help)

---

## 🚀 **Getting Started**

### **Launching the Application**

1. **Start the backend** (if not already running):
   ```bash
   # In WSL/Linux terminal
   cd ~/InsightsLM/backend
   source venv/bin/activate
   python main.py
   ```

2. **Start the frontend**:
   ```bash
   # In Windows PowerShell / macOS terminal
   cd InsightsLM/frontend
   npm start
   ```

3. **Verify connection:**
   - Look at the bottom status bar
   - Should show "Backend: Connected ✅"
   - If shows "Backend is not running ❌", restart backend

---

## 🖥️ **Interface Overview**

### **Main Window Layout**

```
┌─────────────────────────────────────────────────────────────┐
│  [Upload File] [Paste YouTube URL]              [Settings]  │ ← Control Bar
├─────────────────────────────────────────────────────────────┤
│  [Transcript] [Summary] [Overview] [Chat] [Reports]         │ ← Tab Bar
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                                                              │
│                     Content Area                             │
│                  (Changes based on tab)                      │
│                                                              │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Backend: Connected ✅ | Model: Ollama Mistral              │ ← Status Bar
└─────────────────────────────────────────────────────────────┘
```

### **Five Main Tabs**

1. **Transcript:** View full transcription with timestamps
2. **Summary:** Generate AI summaries in any language
3. **Overview:** Create narrative overviews and audio briefings
4. **Chat:** Ask questions about your content
5. **Reports:** Generate custom reports with templates

---

## 🎤 **Transcribing Audio/Video**

### **Method 1: Upload Local File**

1. **Click "Upload File" button** (top-left)

2. **Select your file:**
   - Supported formats:
     - **Audio:** MP3, WAV, M4A, FLAC, OGG
     - **Video:** MP4, AVI, MOV, MKV, WebM
   - File size: Up to 2GB
   - Duration: 2 minutes to 3 hours (recommended)

3. **Wait for transcription:**
   - Progress bar shows status
   - **Time estimate:**
     - 10-minute audio: ~2-5 minutes
     - 1-hour audio: ~15-30 minutes
     - 2-hour audio: ~30-60 minutes
   - Speed depends on:
     - CPU/GPU power
     - File quality
     - Audio clarity

4. **Transcription complete!**
   - Automatically switches to Transcript tab
   - Shows full text with timestamps
   - Ready for analysis

### **Method 2: Transcribe from YouTube URL**

1. **Click "Paste YouTube URL" button**

2. **Enter YouTube URL:**
   ```
   https://www.youtube.com/watch?v=VIDEO_ID
   ```
   or short form:
   ```
   https://youtu.be/VIDEO_ID
   ```

3. **Application will:**
   - Download audio from YouTube
   - Extract audio track
   - Transcribe content
   - Save to database

4. **Progress indicators:**
   - "Downloading audio..."
   - "Transcribing..."
   - "Processing complete!"

### **Transcription Tips**

✅ **Best Results:**
- Clear audio with minimal background noise
- Single speaker or well-separated voices
- Standard speaking pace
- Audio in supported languages

⚠️ **Challenging Scenarios:**
- Heavy accents (may reduce accuracy)
- Multiple overlapping speakers
- Very low audio quality
- Music or noise-heavy recordings

**Transcription Language:**
- Auto-detected by Whisper
- Supports 90+ languages
- Most accurate with English, Spanish, French, German, Chinese

---

## 📖 **Viewing and Searching Transcripts**

### **Transcript Tab Features**

1. **Full Text View:**
   - Complete transcription displayed
   - Timestamps for each segment (e.g., [00:05:23])
   - Scrollable text area

2. **Search Function:**
   - Press `Ctrl+F` (Windows/Linux) or `Cmd+F` (macOS)
   - Type keyword to find in transcript
   - Use "Find Next" to jump between matches

3. **Copy Text:**
   - Select text with mouse
   - Right-click → Copy
   - Or use `Ctrl+C` / `Cmd+C`

4. **Export Transcript:**
   - Click "Export as .txt" button
   - Choose save location
   - Opens as plain text file

### **Understanding Timestamps**

Format: `[HH:MM:SS]` (Hours:Minutes:Seconds)

Example:
```
[00:00:15] Welcome to today's presentation.
[00:00:22] We'll be discussing three main topics.
[00:05:45] Let's move to the first topic.
```

**Use timestamps to:**
- Jump to specific sections
- Reference exact moments
- Cite sources in reports
- Verify AI-generated citations

---

## 📝 **Generating Summaries**

### **How to Generate a Summary**

1. **Go to Summary tab**

2. **Select output language** (optional):
   - Dropdown menu: English, Spanish, French, German, etc.
   - Leave blank for same language as source

3. **Click "Generate Summary"**

4. **Wait for AI processing** (~10-30 seconds)

5. **Review summary:**
   - Appears below button
   - Formatted with bullet points
   - Highlights key points

### **Summary Customization**

**System Instruction:**
The summary prompt uses:
```
Provide a concise summary of the key points from the following text.
Use bullet points for the main ideas.
```

**Output Language:**
- If you select "Spanish", adds:
  ```
  Write your entire response ONLY in Spanish.
  ```

### **Summary Actions**

1. **Export:**
   - Click "Export as .txt"
   - Save summary to text file

2. **Copy:**
   - Select text
   - Copy to clipboard

3. **Generate New:**
   - Click "Clear" button
   - Select different language
   - Click "Generate Summary" again

4. **View Prompt:**
   - Click "View Prompt" button
   - See exact prompt sent to AI
   - Understand how summary was generated

---

## 🎧 **Creating Audio Overviews**

### **What is an Audio Overview?**

An audio overview is a **podcast-style narrated summary** of your content:
- 2-5 minutes long
- Professional narration (text-to-speech)
- Well-written paragraphs (not bullet points)
- Suitable for listening while commuting

### **How to Generate Audio Overview**

1. **Go to Overview tab**

2. **Select output language** (optional)

3. **Click "Generate Audio Overview"**

4. **AI creates narrative:**
   - Takes 30-60 seconds
   - Generates well-written paragraphs
   - Creates MP3 audio file
   - Displays text and audio player

5. **Listen to overview:**
   - Click play button on audio player
   - Download MP3 for offline listening

### **Overview vs Summary**

| Feature | Summary | Overview |
|---------|---------|----------|
| **Format** | Bullet points | Narrative paragraphs |
| **Purpose** | Quick reading | Listening |
| **Style** | Concise | Conversational |
| **Audio** | No | Yes (MP3) |
| **Length** | Short | 2-5 minutes |

### **Audio Overview Actions**

1. **Play/Pause:** Control audio playback
2. **Download:** Save MP3 file
3. **Export Text:** Save narrative as .txt
4. **Clear:** Remove overview and generate new

---

## 💬 **Interactive Chat (Q&A)**

### **How Chat Works**

InsightsLM uses **RAG (Retrieval-Augmented Generation)**:
1. Your question is analyzed
2. Relevant transcript sections are found (vector search)
3. AI answers based on those sections
4. Provides timestamp citations

### **Asking Questions**

1. **Go to Chat tab**

2. **Type your question:**
   - Be specific: "What were the main arguments?"
   - Ask follow-ups: "Can you elaborate on the second point?"
   - Request details: "What examples were given?"

3. **Click "Send" or press Enter**

4. **View AI response:**
   - Answer appears below
   - Citations show timestamps [00:12:34]
   - Click timestamps to verify (future feature)

### **Example Questions**

**Good Questions:**
```
✅ What are the three main topics discussed?
✅ Can you explain the argument about climate change?
✅ What examples did the speaker provide?
✅ What was the conclusion at the end?
✅ Who are the key people mentioned?
```

**Questions to Avoid:**
```
❌ What do you think about this? (AI only answers from content)
❌ Is this video good? (Subjective, not in content)
❌ What happened after this video? (Beyond the content)
```

### **Chat Features**

1. **Conversation History:**
   - All questions and answers saved
   - Scroll up to see previous exchanges
   - Context maintained across questions

2. **Multiple Queries:**
   - Ask as many questions as you want
   - Each question gets its own "View Prompt" button
   - Follow-up questions use conversation context

3. **Citations:**
   - Every answer includes timestamp references
   - Verify AI responses against original content
   - Check accuracy of information

4. **Clear Chat:**
   - Click "Clear & Reset All" button
   - Removes all chat history
   - Starts fresh conversation

---

## 📊 **Custom Reports**

### **Understanding Report Templates**

Reports use **custom prompts** to analyze content in specific ways.

**Pre-built Templates:**
- **Key Points:** Extract main ideas
- **Action Items:** List actionable steps
- **Study Guide:** Create study materials
- **Meeting Notes:** Structured meeting summary

### **Running a Report**

1. **Go to Reports tab**

2. **View available templates:**
   - Dropdown shows all templates
   - Each has a description

3. **Select a template:**
   - Click dropdown
   - Choose desired report type

4. **Select output language** (optional)

5. **Click "Run Report"**

6. **Wait for generation:**
   - Takes 20-40 seconds
   - Depends on content length

7. **View report:**
   - Appears below button
   - Formatted according to template
   - Includes all requested information

### **Creating Custom Templates**

1. **Click "Create New Template" button**

2. **Fill in template details:**
   - **Name:** "Sentiment Analysis"
   - **Description:** "Analyze emotional tone"
   - **Prompt:**
     ```
     Analyze the sentiment and tone of the speaker.
     Identify positive, negative, and neutral sections.
     Provide examples with timestamps.
     ```

3. **Save template:**
   - Appears in template list
   - Available for all future transcriptions

### **Managing Templates**

- **Edit:** Update template prompt or description
- **Delete:** Remove unused templates
- **Export:** Save template for sharing

### **Report Tips**

✅ **Effective Prompts:**
- Be specific about what you want
- Request structured output (bullet points, tables)
- Ask for examples and citations
- Specify detail level needed

❌ **Avoid:**
- Vague instructions ("Analyze this")
- Multiple unrelated requests in one template
- Very long prompts (keep focused)

---

## ⚙️ **Settings and Configuration**

### **Accessing Settings**

Click "Settings" button (top-right) or press `Ctrl+,` (Cmd+, on macOS)

### **Configuration Sections**

#### **1. AI Model Selection**

**Default AI Model:**
- Choose which LLM to use for summaries, chat, reports
- Options:
  - **Ollama Models:** Local, free, private
  - **OpenAI GPT:** Fast, accurate, paid
  - **Anthropic Claude:** Advanced reasoning, paid
  - **Google Gemini:** Multimodal, paid

**Transcription Model:**
- Always uses Whisper large-v3
- Auto-downloaded on first use
- Runs locally (no internet needed)

#### **2. API Keys**

**OpenAI API Key:**
1. Get key from: https://platform.openai.com/api-keys
2. Paste in Settings
3. Click "Test Connection"
4. ✅ Success or ❌ Error

**Anthropic API Key:**
1. Get key from: https://console.anthropic.com/
2. Paste in Settings
3. Click "Test Connection"

**Google Gemini API Key:**
1. Get key from: https://makersuite.google.com/app/apikey
2. Paste in Settings
3. Click "Test Connection"

**Security:**
- Keys are encrypted using system keychain
- Stored locally on your machine
- Never sent to external servers except provider APIs

#### **3. Data Storage**

**Data Location:**
- Linux/WSL: `~/.local/share/InsightsLM/`
- macOS: `~/Library/Application Support/InsightsLM/`

**Contains:**
- `insightsLM.db` - SQLite database
- `chroma_db/` - Vector embeddings
- `temp_uploads/` - Uploaded files
- `static/audio_overviews/` - Generated MP3s
- `config.json` - Encrypted settings

**Clear Data:**
- Warning: This deletes everything!
- Transcripts, summaries, chat history, reports
- Cannot be undone
- Use only if starting fresh

#### **4. Backend Status**

**Health Check:**
- Shows if backend is running
- Displays backend URL
- Tests API connectivity

**Auto-Start Backend:**
- Windows: Tries to start backend in WSL automatically
- macOS/Linux: Manual start required

---

## 💾 **Exporting Content**

### **Export Options**

All tabs have export capabilities:

#### **Transcript Tab:**
- **Export as .txt:** Plain text file with timestamps
- Location: Choose save location
- Format:
  ```
  [00:00:05] First sentence.
  [00:00:12] Second sentence.
  ```

#### **Summary Tab:**
- **Export as .txt:** Summary with metadata
- Includes:
  - Generation timestamp
  - Model used
  - Output language
  - Summary text

#### **Overview Tab:**
- **Export Text:** Narrative text as .txt
- **Download Audio:** MP3 file of narration

#### **Chat Tab:**
- **Export Chat:** All questions and answers
- **Export as .md:** Markdown format with formatting

#### **Reports Tab:**
- **Export as .txt:** Report text with metadata
- **Export as .md:** Markdown formatted report

### **Export Tips**

✅ **Best Practices:**
- Create dedicated folder for exports
- Use descriptive filenames
- Include date in filename
- Keep original transcript for reference

---

## 💡 **Tips and Best Practices**

### **For Better Transcriptions**

1. **Audio Quality Matters:**
   - Use high-quality recordings when possible
   - Minimize background noise
   - Ensure clear speech

2. **File Preparation:**
   - Trim silence at beginning/end
   - Normalize audio levels
   - Split very long files (>2 hours) into sections

3. **Language Support:**
   - English, Spanish, French, German: Excellent
   - Other languages: Good to Fair
   - Use auto-detection for best results

### **For Better AI Responses**

1. **Model Selection:**
   - **Quick tasks:** Ollama Mistral (local, fast)
   - **Complex analysis:** Claude or GPT-4
   - **Balanced:** GPT-3.5 or Gemini

2. **Question Phrasing:**
   - Be specific and clear
   - Ask one thing at a time
   - Use follow-up questions for depth

3. **Report Templates:**
   - Test and refine templates
   - Save working templates
   - Adjust based on content type

### **Performance Optimization**

1. **Hardware:**
   - GPU: 5-10x faster transcription
   - SSD: Faster database access
   - RAM: 16GB+ for large files

2. **Model Management:**
   - Use Ollama for most tasks (free, fast)
   - Reserve API calls for complex analysis
   - Monitor API usage and costs

3. **File Management:**
   - Delete old projects periodically
   - Clear temporary files
   - Export important content before clearing

---

## ❓ **FAQ**

### **General Questions**

**Q: How accurate is the transcription?**  
A: Whisper large-v3 achieves 90-95% accuracy with clear audio. Accuracy decreases with background noise, accents, or technical jargon.

**Q: Can I use InsightsLM offline?**  
A: Yes for transcription and local LLMs (Ollama). No for cloud APIs (OpenAI, Claude, Gemini).

**Q: What languages are supported?**  
A: Whisper supports 90+ languages. LLM responses quality varies by language.

**Q: How much does it cost?**  
A: InsightsLM is free. API usage costs depend on provider:
- OpenAI: ~$0.002-0.03 per request
- Claude: ~$0.01-0.08 per request
- Gemini: ~$0.001-0.015 per request
- Ollama: Free (runs locally)

### **Technical Questions**

**Q: Why is transcription slow?**  
A: Whisper large-v3 is computationally intensive. Use GPU for 5-10x speedup.

**Q: Can I use multiple GPUs?**  
A: Not currently supported. Whisper uses single GPU.

**Q: How do I update Whisper model?**  
A: Reinstall: `pip install --upgrade openai-whisper`

**Q: Where is data stored?**  
A: `~/.local/share/InsightsLM/` (Linux) or `~/Library/Application Support/InsightsLM/` (macOS)

### **Troubleshooting**

**Q: Backend won't start**  
A: Check [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section.

**Q: Frontend shows "Backend not running"**  
A: Verify backend is running at http://127.0.0.1:8000/docs

**Q: API key errors**  
A: Test connection in Settings. Verify key is valid and has credits.

**Q: Out of memory errors**  
A: Try smaller files, close other applications, or upgrade RAM.

---

## 🆘 **Getting Help**

- **Documentation:** [Setup Guide](SETUP_GUIDE.md), [README](../README.md)
- **Issues:** [GitHub Issues](https://github.com/YOUR-USERNAME/InsightsLM/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR-USERNAME/InsightsLM/discussions)
- **Email:** your.email@example.com

---

**Enjoy using InsightsLM! 🚀**

*Transform your audio into insights*
