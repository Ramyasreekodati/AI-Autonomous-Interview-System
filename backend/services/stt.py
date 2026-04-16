import os
import time

class STTService:
    def __init__(self):
        self.model = None
        
    def _load_model(self):
        if self.model is None:
            try:
                import whisper
                # Use "base" or "tiny" for performance on CPUs
                self.model = whisper.load_model("base")
            except Exception as e:
                print(f"Whisper Load Error: {e}")
                
    def transcribe(self, audio_path):
        """
        Transcribes audio file to text using OpenAI Whisper.
        """
        self._load_model()
        if self.model is None:
            return "Transcript not available: Model load failed."
            
        try:
            result = self.model.transcribe(audio_path)
            return result.get("text", "").strip()
        except Exception as e:
            return f"Transcription Error: {str(e)}"

stt_service = STTService()
