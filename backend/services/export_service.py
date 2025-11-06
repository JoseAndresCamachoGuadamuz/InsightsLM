from sqlalchemy.orm import Session
from database.models import Transcription, Template
from services.llm_service import generate_response

def _format_time(seconds: float) -> str:
    """A helper function to format seconds into a MM:SS string."""
    if seconds is None:
        return "00:00"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def format_transcript_md(transcription_result: dict) -> str:
    """
    Formats a full transcription result from Whisper into a Markdown string.

    Args:
        transcription_result: The full dictionary returned by the transcribe_audio service.

    Returns:
        A Markdown formatted string with timestamps for each segment.
    """
    lines = [f"# Transcription\n"]
    segments = transcription_result.get('segments', [])
    for segment in segments:
        start_time = _format_time(segment.get('start'))
        lines.append(f"**[{start_time}]** {segment.get('text', '').strip()}")
    return "\n".join(lines)

def format_transcript_txt(transcription_result: dict) -> str:
    """
    Formats a full transcription result from Whisper into a plain text string.

    Args:
        transcription_result: The full dictionary returned by the transcribe_audio service.

    Returns:
        The plain text of the transcription.
    """
    return transcription_result.get('text', 'No text found.')

def format_provided_content(content: str, content_type: str, as_markdown: bool) -> str:
    """
    Formats provided content (from frontend) with appropriate headers.
    This allows exporting exactly what's displayed on screen.

    Args:
        content: The text content to format.
        content_type: Type of content ('transcript', 'summary', 'overview', 'report').
        as_markdown: If True, formats with markdown header.

    Returns:
        The formatted content string.
    """
    if not content:
        return "No content provided."
    
    # Clean up any leading/trailing whitespace
    content = content.strip()
    
    if not as_markdown:
        # Plain text - return as-is
        return content
    
    # Markdown - add appropriate header based on type
    headers = {
        'transcript': '# Transcription',
        'summary': '# Summary',
        'overview': '# Overview',
        'report': '# Report'
    }
    
    header = headers.get(content_type, '# Document')
    return f"{header}\n\n{content}"

def generate_and_format_summary(transcription: Transcription, model_key: str, as_markdown: bool) -> str:
    """
    Generates a bullet-point summary from a transcription and formats it.

    Args:
        transcription: The SQLAlchemy Transcription object.
        model_key: The AI model to use for generation.
        as_markdown: If True, formats the output as Markdown.

    Returns:
        The formatted summary string.
    """
    prompt = f"Please provide a concise summary of the key points from the following text. Use bullet points for the main ideas.\n\n---\n\n{transcription.full_text}"
    summary = generate_response(prompt, model_key=model_key)
    if as_markdown:
        return f"# Summary\n\n{summary}"
    return summary

def generate_and_format_overview(transcription: Transcription, model_key: str, as_markdown: bool) -> str:
    """
    Generates a narrative overview from a transcription and formats it.

    Args:
        transcription: The SQLAlchemy Transcription object.
        model_key: The AI model to use for generation.
        as_markdown: If True, formats the output as Markdown.

    Returns:
        The formatted overview string.
    """
    prompt = f"Generate a narrative overview of the following text. Write it as a series of well-written paragraphs with concatenated ideas, suitable for a short audio briefing. Do not use bullet points or numbered lists.\n\n---\n\n{transcription.full_text}"
    overview = generate_response(prompt, model_key=model_key)
    if as_markdown:
        return f"# Overview\n\n{overview}"
    return overview

def generate_and_format_report(transcription: Transcription, template: Template, model_key: str, as_markdown: bool) -> str:
    """
    Generates a custom report from a transcription and a template, then formats it.

    Args:
        transcription: The SQLAlchemy Transcription object.
        template: The SQLAlchemy Template object.
        model_key: The AI model to use for generation.
        as_markdown: If True, formats the output as Markdown.

    Returns:
        The formatted report string.
    """
    language_instruction = ""
    if template.language and template.language != "Does Not Apply":
        language_instruction = f"Please write the response in {template.language}.\n\n"
    
    full_prompt = f"{language_instruction}{template.prompt_text}\n\n---\n\n{transcription.full_text}"
    report_text = generate_response(full_prompt, model_key=model_key)
    
    if as_markdown:
        return f"# Report: {template.name}\n\n{report_text}"
    return report_text