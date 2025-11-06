from gtts import gTTS
import os

def generate_audio(text: str, save_path: str) -> bool:
    try:
        print(f"Initializing gTTS to generate audio at {save_path}...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(save_path)
        print("Audio file generated successfully.")
        return os.path.exists(save_path)
    except Exception as e:
        print(f"An error occurred during gTTS generation: {e}")
        return False