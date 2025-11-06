import whisper
import os

print("Loading Whisper model...")
# Using the "base" model. For more accurate timestamps, larger models like "small" or "medium" can be used.
model = whisper.load_model("base")
print("Whisper model loaded.")

def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes the audio from a given file path and returns the full result object.

    Args:
        file_path (str): The path to the audio or video file.

    Returns:
        dict: The full transcription result object from Whisper, including text and segments with timestamps.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")

    print(f"Starting transcription for {file_path}...")
    try:
        # We now return the entire 'result' dictionary
        result = model.transcribe(file_path, fp16=False)
        print("Transcription completed.")
        return result
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return {}