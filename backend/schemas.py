from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal

# --- Analysis Schemas ---

# Used for the /query/ endpoint
class QueryRequest(BaseModel):
    source_id: int
    query_text: str
    model_key: Optional[str] = "ollama_mistral"

# Used for /summarize/ and /audio-overview/ endpoints
class SummarizeRequest(BaseModel):
    source_id: int
    model_key: Optional[str] = "ollama_mistral"


# --- Transcription Schema ---

# Used for the /transcribe-url/ endpoint
class UrlRequest(BaseModel):
    url: str


# --- Template & Report Schemas ---

# Used when creating a new template via POST /templates/
class TemplateCreate(BaseModel):
    name: str
    prompt_text: str
    language: str

# Used when updating a template via PUT /templates/{id}
class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    prompt_text: Optional[str] = None
    language: Optional[str] = None

# Used as the response model for returning template data
class TemplateResponse(TemplateCreate):
    id: int

    # Pydantic v2 configuration to allow mapping from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)

# Used for the /report/ endpoint
class ReportRequest(BaseModel):
    source_id: int
    template_id: int
    model_key: Optional[str] = "ollama_mistral"


# --- Export Schema ---

# Used for the /export/ endpoint
class ExportRequest(BaseModel):
    source_id: int
    # Defines the specific types of content that can be exported
    content_type: Literal['transcript', 'summary', 'overview', 'report']
    # Defines the allowed export formats
    format: Literal['txt', 'md']
    # Optional fields needed for specific content types
    template_id: Optional[int] = None
    model_key: Optional[str] = "ollama_mistral"
    # NEW: Optional content field - if provided, exports this exact content
    # This allows exporting exactly what's displayed on screen
    content: Optional[str] = None