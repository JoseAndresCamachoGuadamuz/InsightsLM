import os
import shutil
import uuid
import logging  # STEP 6B: Added for enhanced error logging
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  # REQUIREMENT 5.4: Added for API testing responses
from sqlalchemy.orm import Session
from typing import List, Dict

# STEP 6B: Set up logging for error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local imports from our application's modules
from database.database import create_db_and_tables, get_db
from database.models import Project, Source, Transcription, Template
from services.transcription_service import transcribe_audio
from services.vector_db_service import add_transcript_to_db, query_db
from services.llm_service import (
    generate_response, 
    test_api_connection,  # REQUIREMENT 5.4: API testing
    get_ollama_models,    # STEP 2: Model discovery
    get_openai_models,    # STEP 2: Model discovery
    get_anthropic_models, # STEP 2: Model discovery
    get_google_models,    # STEP 2: Model discovery
    get_all_available_models  # STEP 2: Model discovery
)
from services.downloader_service import download_audio
from services.tts_service import generate_audio
from services import export_service
from schemas import (
    QueryRequest, UrlRequest, SummarizeRequest, TemplateCreate,
    TemplateUpdate, TemplateResponse, ReportRequest, ExportRequest
)
from services.config_service import load_config, save_config, encrypt_key, decrypt_key

# --- Configuration & Directory Setup ---
# Load configuration and define all data paths based on it
config = load_config()
DATA_STORAGE_PATH = config.get("data_storage_path", ".")
UPLOAD_DIRECTORY = os.path.join(DATA_STORAGE_PATH, "temp_uploads")
STATIC_DIRECTORY = os.path.join(DATA_STORAGE_PATH, "static")
AUDIO_OVERVIEW_DIRECTORY = os.path.join(STATIC_DIRECTORY, "audio_overviews")
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(AUDIO_OVERVIEW_DIRECTORY, exist_ok=True)


# --- Language Detection Helper ---
def detect_language(text: str) -> str:
    """
    Detect the primary language of the text using simple heuristics.
    Returns a language name suitable for LLM prompts.
    """
    # Take first 500 characters for detection
    sample = text[:500].lower()

    # Count language-specific indicators
    spanish_indicators = ['el ', 'la ', 'los ', 'las ', 'de ', 'que ', 'es ', 'un ', 'una ', 'por ', 'para ', 'con ', 'en ', 'del ']
    french_indicators = ['le ', 'la ', 'les ', 'de ', 'des ', 'un ', 'une ', 'je ', 'tu ', 'il ', 'nous ', 'vous ', 'ils ', 'et ', 'est ', 'dans ']
    german_indicators = ['der ', 'die ', 'das ', 'den ', 'dem ', 'des ', 'ein ', 'eine ', 'und ', 'ich ', 'ist ', 'nicht ', 'mit ', 'für ']
    english_indicators = ['the ', 'a ', 'an ', 'is ', 'are ', 'was ', 'were ', 'and ', 'or ', 'but ', 'in ', 'on ', 'at ', 'to ', 'for ']

    spanish_count = sum(sample.count(indicator) for indicator in spanish_indicators)
    french_count = sum(sample.count(indicator) for indicator in french_indicators)
    german_count = sum(sample.count(indicator) for indicator in german_indicators)
    english_count = sum(sample.count(indicator) for indicator in english_indicators)

    # Determine which language has the most indicators
    counts = {
        'Spanish': spanish_count,
        'French': french_count,
        'German': german_count,
        'English': english_count
    }

    detected_language = max(counts, key=counts.get)

    # Require minimum threshold to avoid false positives
    if counts[detected_language] < 3:
        detected_language = 'English'  # Default to English if uncertain

    print(f"Language detection: {detected_language} (scores: {counts})")
    return detected_language


# REQUIREMENT 3: Audio Filename Sanitization Helper
def sanitize_filename_for_audio(file_path: str) -> str:
    """
    REQUIREMENT 3: Extract and sanitize filename from Source.file_path for audio overview naming.

    Args:
        file_path: Full path like "/path/to/uuid_OriginalFilename.mp4"

    Returns:
        Sanitized filename like "SanitizedFilename" (without extension)

    Processing Rules:
    - Extract filename after last underscore
    - Remove file extension
    - Strip spaces, hyphens, underscores, parentheses
    - Preserve original case
    - Truncate to max 30 characters
    """
    try:
        # Extract filename from full path
        filename_with_ext = os.path.basename(file_path)

        # Extract original filename after the UUID (after last underscore)
        if '_' in filename_with_ext:
            # Split by underscore and take everything after the first part (UUID)
            parts = filename_with_ext.split('_', 1)
            if len(parts) > 1:
                original_filename = parts[1]
            else:
                original_filename = filename_with_ext
        else:
            original_filename = filename_with_ext

        # Remove file extension
        name_without_ext = os.path.splitext(original_filename)[0]

        # Apply sanitization rules
        sanitized = name_without_ext

        # Remove spaces
        sanitized = sanitized.replace(' ', '')

        # Remove hyphens
        sanitized = sanitized.replace('-', '')

        # Remove underscores
        sanitized = sanitized.replace('_', '')

        # Remove parentheses
        sanitized = sanitized.replace('(', '').replace(')', '')

        # Preserve original case, truncate to max 30 characters
        sanitized = sanitized[:30]

        # Fallback to "Audio" if result is empty
        if not sanitized:
            sanitized = "Audio"

        return sanitized

    except Exception as e:
        print(f"Error sanitizing filename from {file_path}: {e}")
        return "Audio"  # Safe fallback


def extract_original_filename(file_path: str) -> str:
    """
    Extract original filename from file_path that has format: {uuid}_{original_filename}

    Args:
        file_path: Full path like "/path/to/uuid_OriginalFilename.mp4"

    Returns:
        Original filename like "OriginalFilename.mp4"
    """
    try:
        filename_with_ext = os.path.basename(file_path)

        # Extract original filename after the UUID (after first underscore)
        if '_' in filename_with_ext:
            parts = filename_with_ext.split('_', 1)
            if len(parts) > 1:
                return parts[1]

        # Fallback to full filename if no underscore found
        return filename_with_ext

    except Exception as e:
        print(f"Error extracting filename from {file_path}: {e}")
        return os.path.basename(file_path)


# --- Application Initialization ---

# This function runs once when the application starts up
async def startup_event():
    print("Starting up...")
    create_db_and_tables()
    db = next(get_db())
    if not db.query(Project).filter(Project.id == 1).first():
        db.add(Project(id=1, name="Default Project"))
        db.commit()
    db.close()
    print("Startup complete. Default project created.")

app = FastAPI(title="InsightsLM Backend", on_startup=[startup_event])

# Mount static directory to serve generated files like audio overviews
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")

# Configure CORS to allow the frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# --- Core Helper Function ---

def process_and_save_file(file_on_disk_path: str, original_filename: str, db: Session) -> dict:
    """
    The main workflow for processing a file after it's on disk.
    This includes renaming, transcribing, and saving to all databases.

    Returns a dictionary with source_id, transcription_id, and file_path.
    """
    # Rename the file with a UUID prefix
    uuid_prefix = str(uuid.uuid4())
    final_filename = f"{uuid_prefix}_{original_filename}"
    final_file_path = os.path.join(UPLOAD_DIRECTORY, final_filename)
    shutil.move(file_on_disk_path, final_file_path)

    # Transcribe the audio
    transcription_result = transcribe_audio(final_file_path)
    if not transcription_result or not transcription_result.get("text"):
        raise HTTPException(status_code=500, detail="Transcription failed or returned no text.")
    full_text = transcription_result["text"]

    # Insert the source into our relational database
    source = Source(file_path=final_file_path, project_id=1)
    db.add(source)
    db.commit()
    db.refresh(source)

    # Insert the transcription
    transcription = Transcription(full_text=full_text, source_id=source.id)
    db.add(transcription)
    db.commit()
    db.refresh(transcription)

    # Add the transcript to our vector database (ChromaDB) for future query/RAG use
    add_transcript_to_db(source.id, transcription_result)

    return {
        "source_id": source.id,
        "transcription_id": transcription.id,
        "transcription": full_text,  # Add the actual transcription text for frontend
        "file_path": final_file_path
    }


# --- API Endpoints ---

# REQUIREMENT 5.4: Health check endpoint for frontend to verify backend is running
@app.get("/health", summary="Health check endpoint")
def health_check():
    """
    Simple health check endpoint that returns 200 OK if backend is running.
    Used by frontend to verify backend availability.
    """
    return {"status": "ok"}


# REQUIREMENT 5.4: API Testing Endpoints
@app.get("/test-api/status", summary="Test all API connections and return comprehensive status")
def get_api_status():
    """
    Test connections to all API providers and return aggregated results.
    This endpoint actually calls the test functions for each provider.

    Returns:
        Dictionary with 'results' (individual test results) and 'summary' (aggregate stats)
    """
    providers = ['ollama', 'openai', 'anthropic', 'google']
    results = {}

    # Test each provider
    for provider in providers:
        results[provider] = test_api_connection(provider)

    # Calculate summary statistics
    working_providers = sum(1 for r in results.values() if r['success'])
    failed_providers = len(providers) - working_providers

    return {
        "results": results,
        "summary": {
            "total_providers": len(providers),
            "working_providers": working_providers,
            "failed_providers": failed_providers
        }
    }

@app.post("/test-api/{provider}", summary="Test API connection for a specific provider")
def test_provider_connection(provider: str):
    """
    Test the connection to a specific LLM provider.
    Validates that the API key works and the provider is accessible.

    Args:
        provider: One of 'ollama', 'openai', 'anthropic', 'google'

    Returns:
        Success/failure status with details
    """
    valid_providers = ['ollama', 'openai', 'anthropic', 'google']
    if provider not in valid_providers:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Invalid provider. Must be one of: {', '.join(valid_providers)}",
                "provider": provider
            }
        )

    # Call the test function from llm_service
    result = test_api_connection(provider)

    # Return appropriate status code
    status_code = 200 if result["success"] else 400
    return JSONResponse(status_code=status_code, content=result)


# STEP 2: Model Discovery Endpoints
@app.get("/models/ollama", summary="Get available Ollama models")
def get_ollama_models_endpoint():
    """
    Returns a list of locally installed Ollama models.
    Returns empty list if Ollama is not running or has no models.
    
    Response format:
    [
        {
            "key": "ollama_mistral",
            "label": "Ollama: Mistral",
            "provider": "ollama"
        },
        ...
    ]
    """
    try:
        models = get_ollama_models()
        return {
            "models": models,
            "count": len(models),
            "provider": "ollama"
        }
    except ValueError as e:
        # STEP 6B: User-friendly error from llm_service (expected)
        # These are actionable messages like "Ollama is not running..."
        logger.info(f"Ollama provider error: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "ollama",
            "error": str(e)
        }
    except Exception as e:
        # STEP 6B: Unexpected error - log for debugging
        logger.error(f"Unexpected error in Ollama endpoint: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "ollama",
            "error": "Ollama service temporarily unavailable. Please try again."
        }

@app.get("/models/openai", summary="Get available OpenAI models")
def get_openai_models_endpoint():
    """
    Returns a list of OpenAI models accessible with the configured API key.
    Returns empty list if API key is not configured or invalid.
    
    Response format:
    [
        {
            "key": "openai_gpt_4o",
            "label": "OpenAI: GPT-4o",
            "provider": "openai",
            "model_id": "gpt-4o"
        },
        ...
    ]
    """
    try:
        models = get_openai_models()
        return {
            "models": models,
            "count": len(models),
            "provider": "openai"
        }
    except ValueError as e:
        # STEP 6B: User-friendly error from llm_service (expected)
        # These are actionable messages like "OpenAI API key is invalid..."
        logger.info(f"OpenAI provider error: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "openai",
            "error": str(e)
        }
    except Exception as e:
        # STEP 6B: Unexpected error - log for debugging
        logger.error(f"Unexpected error in OpenAI endpoint: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "openai",
            "error": "OpenAI service temporarily unavailable. Please try again."
        }

@app.get("/models/anthropic", summary="Get available Anthropic models")
def get_anthropic_models_endpoint():
    """
    Returns a list of Anthropic Claude models.
    Returns empty list if API key is not configured.
    
    Response format:
    [
        {
            "key": "claude_3_5_sonnet",
            "label": "Anthropic: Claude 3.5 Sonnet",
            "provider": "anthropic",
            "model_id": "claude-3-5-sonnet-20240620"
        },
        ...
    ]
    """
    try:
        models = get_anthropic_models()
        return {
            "models": models,
            "count": len(models),
            "provider": "anthropic"
        }
    except ValueError as e:
        # STEP 6B: User-friendly error from llm_service (expected)
        # These are actionable messages like "Anthropic API key is invalid..."
        logger.info(f"Anthropic provider error: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "anthropic",
            "error": str(e)
        }
    except Exception as e:
        # STEP 6B: Unexpected error - log for debugging
        logger.error(f"Unexpected error in Anthropic endpoint: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "anthropic",
            "error": "Anthropic service temporarily unavailable. Please try again."
        }

@app.get("/models/google", summary="Get available Google Gemini models")
def get_google_models_endpoint():
    """
    Returns a list of Google Gemini models accessible with the configured API key.
    Returns empty list if API key is not configured or invalid.
    
    Response format:
    [
        {
            "key": "gemini_gemini_2_5_pro",
            "label": "Google: Gemini 2.5 Pro",
            "provider": "google",
            "model_id": "gemini-2.5-pro"
        },
        ...
    ]
    """
    try:
        models = get_google_models()
        return {
            "models": models,
            "count": len(models),
            "provider": "google"
        }
    except ValueError as e:
        # STEP 6B: User-friendly error from llm_service (expected)
        # These are actionable messages like "Google Gemini API key is invalid..."
        logger.info(f"Google provider error: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "google",
            "error": str(e)
        }
    except Exception as e:
        # STEP 6B: Unexpected error - log for debugging
        logger.error(f"Unexpected error in Google endpoint: {e}")
        return {
            "models": [],
            "count": 0,
            "provider": "google",
            "error": "Google Gemini service temporarily unavailable. Please try again."
        }

@app.get("/models/all", summary="Get all available models from all providers")
def get_all_models_endpoint():
    """
    Returns a comprehensive list of all available models from all providers.
    Aggregates results from Ollama, OpenAI, Anthropic, and Google Gemini.
    
    This is the main endpoint used by the frontend to populate model dropdowns.
    Always returns a valid response (empty list if no models available).
    
    STEP 6C-2: Now includes provider_errors for better frontend error display.
    
    Response format:
    {
        "models": [
            {"key": "ollama_mistral", "label": "Ollama: Mistral", "provider": "ollama"},
            {"key": "openai_gpt_4o", "label": "OpenAI: GPT-4o", "provider": "openai"},
            ...
        ],
        "count": 102,
        "providers": {
            "ollama": 0,
            "openai": 58,
            "anthropic": 3,
            "google": 41
        },
        "provider_errors": {
            "ollama": "Ollama is not running. Please start Ollama to use local models.",
            "openai": "OpenAI API key is invalid. Please check your key in Settings."
        } (optional, only present if providers have errors)
    }
    """
    try:
        # STEP 6C-2: get_all_available_models() now returns dict with models and provider_errors
        result = get_all_available_models()
        
        # Handle both old (list) and new (dict) return formats for backward compatibility
        if isinstance(result, dict):
            models = result.get("models", [])
            provider_errors = result.get("provider_errors")
        else:
            # Backward compatibility: if it returns a list (shouldn't happen after 6C-1)
            models = result
            provider_errors = None
        
        # Calculate provider breakdown
        provider_counts = {}
        for model in models:
            provider = model.get('provider', 'unknown')
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        # Build response
        response = {
            "models": models,
            "count": len(models),
            "providers": provider_counts
        }
        
        # STEP 6C-2: Include provider_errors if present
        if provider_errors:
            response["provider_errors"] = provider_errors
        
        return response
    except Exception as e:
        # Return empty list on error (graceful degradation)
        return {
            "models": [],
            "count": 0,
            "providers": {},
            "error": str(e)
        }


@app.post("/upload/", summary="Upload a file and process it")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(temp_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = process_and_save_file(temp_file_path, file.filename, db)
    return result

@app.post("/download/", summary="Download a file from a URL and process it")
def download_and_process(request: UrlRequest, db: Session = Depends(get_db)):
    # STEP 29 FIX: Added UPLOAD_DIRECTORY as second argument to download_audio()
    downloaded_path = download_audio(request.url, UPLOAD_DIRECTORY)
    if not downloaded_path:
        raise HTTPException(status_code=400, detail="Failed to download the media.")
    original_filename = os.path.basename(downloaded_path)
    result = process_and_save_file(downloaded_path, original_filename, db)
    return result

@app.get("/sources/", response_model=List[dict], summary="List all sources")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return [{"id": s.id, "original_filename": extract_original_filename(s.file_path), "file_path": s.file_path} for s in sources]

@app.get("/sources/{source_id}/transcription/", summary="Get the transcription for a source")
def get_transcription(source_id: int, db: Session = Depends(get_db)):
    transcription = db.query(Transcription).filter(Transcription.source_id == source_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"full_text": transcription.full_text}

# --- Templates Endpoints ---
@app.get("/templates/", response_model=List[TemplateResponse], summary="Get all templates")
def get_templates(db: Session = Depends(get_db)):
    templates = db.query(Template).all()
    return templates

@app.post("/templates/", response_model=TemplateResponse, summary="Create a new template")
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    new_template = Template(name=template.name, prompt_text=template.prompt_text)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@app.put("/templates/{template_id}", response_model=TemplateResponse, summary="Update a template")
def update_template(template_id: int, template: TemplateUpdate, db: Session = Depends(get_db)):
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found.")
    if template.name is not None:
        db_template.name = template.name
    if template.prompt_text is not None:
        db_template.prompt_text = template.prompt_text
    db.commit()
    db.refresh(db_template)
    return db_template

@app.delete("/templates/{template_id}", status_code=204, summary="Delete a template")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found.")
    db.delete(db_template)
    db.commit()
    return

@app.post("/report/", summary="Generate a report for a source using a template")
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    transcription = db.query(Transcription).filter(Transcription.source_id == request.source_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Source not found.")
    template = db.query(Template).filter(Template.id == request.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found.")

    # Auto-detect language from transcription
    detected_language = detect_language(transcription.full_text)
    language_instruction = f"""Write your response in {detected_language}.

"""

    full_prompt = f"{language_instruction}{template.prompt_text}\n\n---\n\n{transcription.full_text}"
    report_text = generate_response(full_prompt, model_key=request.model_key)
    return {"report_text": report_text, "prompt": full_prompt}

@app.post("/summarize/", summary="Generate a summary for a source")
def summarize_source(request: SummarizeRequest, db: Session = Depends(get_db)):
    transcription = db.query(Transcription).filter(Transcription.source_id == request.source_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Source not found.")

    # FIXED: Auto-detect language and generate summary in the same language
    detected_language = detect_language(transcription.full_text)

    prompt = f"""Please provide a concise summary of the key points from the following text. Use bullet points for the main ideas.

Write your summary in {detected_language}.

---

{transcription.full_text}"""

    summary = generate_response(prompt, model_key=request.model_key)
    return {"summary": summary, "prompt": prompt}

@app.post("/query/", summary="Ask a question about a source")
def query_source(request: QueryRequest):
    context_chunks_with_metadata = query_db(query_text=request.query_text, source_id=request.source_id)
    if not context_chunks_with_metadata:
        return {"answer": "Could not find relevant information.", "citations": []}
    context_for_prompt = "\n---\n".join([chunk['text'] for chunk in context_chunks_with_metadata])
    prompt = f"Based ONLY on the following context, answer the user's question.\n\nCONTEXT:\n{context_for_prompt}\n\nQUESTION:\n{request.query_text}"
    answer = generate_response(prompt, model_key=request.model_key)
    return {"answer": answer, "citations": context_chunks_with_metadata, "prompt": prompt}

@app.post("/audio-overview/", summary="Generate an audio overview for a source")
def create_audio_overview(request: SummarizeRequest, db: Session = Depends(get_db)):
    # Get transcription (existing logic)
    transcription = db.query(Transcription).filter(Transcription.source_id == request.source_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Source not found.")

    # REQUIREMENT 3: Get source to extract filename for meaningful audio naming
    source = db.query(Source).filter(Source.id == request.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source record not found.")

    # Auto-detect language and generate overview (existing logic)
    detected_language = detect_language(transcription.full_text)

    prompt = f"""Generate a narrative overview of the following text. Write it as a series of well-written paragraphs with concatenated ideas, suitable for a short audio briefing. Do not use bullet points or numbered lists.

Write your overview in {detected_language}.

---

{transcription.full_text}"""

    summary_text = generate_response(prompt, model_key=request.model_key)
    if not summary_text:
        raise HTTPException(status_code=500, detail="Failed to generate summary text.")

    # REQUIREMENT 3: Generate meaningful filename using sanitized original filename
    sanitized_filename = sanitize_filename_for_audio(source.file_path)
    audio_filename = f"overview_{request.source_id}_{sanitized_filename}.mp3"
    audio_save_path = os.path.join(AUDIO_OVERVIEW_DIRECTORY, audio_filename)

    # Generate audio file (existing logic)
    success = generate_audio(summary_text, audio_save_path)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to generate audio file.")

    # Return audio URL (existing logic)
    audio_url = f"/static/audio_overviews/{audio_filename}"
    return {"audio_url": audio_url, "summary_text": summary_text, "prompt": prompt}

@app.post("/export/", summary="Export content to a file")
def export_content(request: ExportRequest, db: Session = Depends(get_db)):
    """
    Export content to a downloadable file.

    NEW BEHAVIOR: If request includes 'content' field, exports that directly.
    This allows exporting exactly what's displayed on screen.

    FALLBACK: If no content provided, generates content from database (old behavior).
    """
    source = db.query(Source).filter(Source.id == request.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source document not found.")

    content = ""
    is_markdown = request.format == 'md'
    media_type = "text/markdown; charset=utf-8" if is_markdown else "text/plain; charset=utf-8"

    # Set default filename
    filename_prefix = request.content_type
    filename = f"{filename_prefix}_{request.source_id}.{request.format}"

    # For reports, always generate custom filename with template name
    if request.content_type == 'report':
        if not request.template_id:
            raise HTTPException(status_code=400, detail="Template ID is required for report export.")
        template = db.query(Template).filter(Template.id == request.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found.")
        sanitized_template_name = "".join(c for c in template.name if c.isalnum() or c in ('_')).rstrip()
        filename = f"report_{sanitized_template_name}_{request.source_id}.{request.format}"

    # Check if content is provided in request (from frontend)
    provided_content = getattr(request, 'content', None)

    if provided_content:
        # Use the provided content from frontend
        content = export_service.format_provided_content(
            provided_content,
            request.content_type,
            is_markdown
        )
    else:
        # FALLBACK: Generate content (old behavior)
        if request.content_type == 'transcript':
            if not source.transcription:
                raise HTTPException(status_code=404, detail="Transcription not found.")

            if is_markdown:
                transcription_result = transcribe_audio(source.file_path)
                content = export_service.format_transcript_md(transcription_result)
            else:
                content = source.transcription.full_text

        elif request.content_type in ['summary', 'overview']:
            if not source.transcription:
                raise HTTPException(status_code=404, detail="Transcription not found.")
            if request.content_type == 'summary':
                content = export_service.generate_and_format_summary(source.transcription, request.model_key, is_markdown)
            else: # overview
                content = export_service.generate_and_format_overview(source.transcription, request.model_key, is_markdown)

        elif request.content_type == 'report':
            if not source.transcription:
                raise HTTPException(status_code=404, detail="Transcription not found.")
            # Template was already fetched above for filename generation
            template = db.query(Template).filter(Template.id == request.template_id).first()
            content = export_service.generate_and_format_report(source.transcription, template, request.model_key, is_markdown)

    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return Response(content=content, media_type=media_type, headers=headers)


# --- DEBUG HELPER FUNCTION ---
def mask_api_key(key: str) -> str:
    """Safely mask API key for logging."""
    if not key:
        return "<empty>"
    if len(key) <= 4:
        return "*" * len(key)
    return f"{key[:4]}...{key[-2:]} (length: {len(key)})"


# --- Configuration Endpoints ---
@app.get("/config/", response_model=Dict, summary="Get the current application configuration")
def get_config():
    current_config = load_config()
    current_config["api_keys"]["openai"] = decrypt_key(current_config["api_keys"].get("openai", ""))
    current_config["api_keys"]["anthropic"] = decrypt_key(current_config["api_keys"].get("anthropic", ""))
    current_config["api_keys"]["google"] = decrypt_key(current_config["api_keys"].get("google", ""))
    return current_config

@app.put("/config/", status_code=204, summary="Update the application configuration")
def update_config(updated_config: Dict):
    """
    Update application configuration with comprehensive debug logging.
    Safely masks API keys in all log output.
    """
    print("=" * 70)
    print(f"[DEBUG main.py] update_config() endpoint called")
    print("=" * 70)

    # Log what was received
    print(f"[DEBUG main.py] Received config structure:")
    print(f"[DEBUG main.py]   - Top-level keys: {list(updated_config.keys())}")
    print(f"[DEBUG main.py]   - Contains 'default_model': {'default_model' in updated_config}")
    print(f"[DEBUG main.py]   - Contains 'api_keys': {'api_keys' in updated_config}")
    print(f"[DEBUG main.py]   - Contains 'data_storage_path': {'data_storage_path' in updated_config}")

    # Check default_model
    if "default_model" in updated_config:
        print(f"[DEBUG main.py] default_model received: '{updated_config['default_model']}'")

    # Check api_keys with SAFE masking
    if "api_keys" in updated_config:
        print(f"[DEBUG main.py] API Keys section found:")
        api_keys = updated_config['api_keys']

        # Check structure
        if isinstance(api_keys, dict):
            print(f"[DEBUG main.py]   - api_keys is a dict with keys: {list(api_keys.keys())}")

            # Log each provider safely
            for provider in ["openai", "anthropic", "google"]:
                if provider in api_keys:
                    raw_value = api_keys[provider]
                    masked_value = mask_api_key(raw_value)
                    print(f"[DEBUG main.py]   - {provider}: {masked_value}")
                else:
                    print(f"[DEBUG main.py]   - {provider}: <not in request>")
        else:
            print(f"[DEBUG main.py]   - WARNING: api_keys is not a dict! Type: {type(api_keys)}")
            print(f"[DEBUG main.py]   - Value: {api_keys}")
    else:
        print(f"[DEBUG main.py] WARNING: No 'api_keys' in updated_config!")
        print(f"[DEBUG main.py] Full config received: {updated_config}")

    print("-" * 70)
    print(f"[DEBUG main.py] Starting config update process...")

    # Load current config
    print(f"[DEBUG main.py] Step 1: Loading current config...")
    current_config = load_config()
    print(f"[DEBUG main.py]   - Current config loaded successfully")

    # Update default_model
    if "default_model" in updated_config:
        print(f"[DEBUG main.py] Step 2: Updating default_model...")
        current_config["default_model"] = updated_config["default_model"]
        print(f"[DEBUG main.py]   - default_model updated to: '{updated_config['default_model']}'")

    # Update and encrypt API keys
    if "api_keys" in updated_config:
        print(f"[DEBUG main.py] Step 3: Processing API keys...")

        for provider in ["openai", "anthropic", "google"]:
            plaintext_key = updated_config["api_keys"].get(provider, "")

            if plaintext_key:
                print(f"[DEBUG main.py]   - Encrypting {provider} key: {mask_api_key(plaintext_key)}")
                encrypted_key = encrypt_key(plaintext_key)

                if encrypted_key:
                    current_config["api_keys"][provider] = encrypted_key
                    print(f"[DEBUG main.py]   - ✓ {provider} encrypted successfully (length: {len(encrypted_key)})")
                else:
                    print(f"[DEBUG main.py]   - ✗ {provider} encryption FAILED (returned empty string)")
                    current_config["api_keys"][provider] = ""
            else:
                print(f"[DEBUG main.py]   - {provider} key is empty, skipping encryption")
                current_config["api_keys"][provider] = ""
    else:
        print(f"[DEBUG main.py] Step 3: SKIPPED - No api_keys in request")

    # Save config
    print(f"[DEBUG main.py] Step 4: Saving updated config...")
    save_config(current_config)
    print(f"[DEBUG main.py]   - Config saved successfully")

    print("=" * 70)
    print(f"[DEBUG main.py] update_config() completed successfully")
    print("=" * 70)

    return