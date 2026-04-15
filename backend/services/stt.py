import os
from pydub import AudioSegment
import whisper
import torch

class STTService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                print(f"Loading Whisper model (base) on {self.device}...")
                self._model = whisper.load_model("base", device=self.device)
            except Exception as e:
                print(f"Error loading Whisper: {e}")
                self._model = "FAILED"
        return self._model if self._model != "FAILED" else None

    def transcribe(self, audio_file_path):
        model = self.model
        if not model:
            return "STT Model not available"
        result = model.transcribe(audio_file_path)
        return result["text"]

stt_service = STTService()
