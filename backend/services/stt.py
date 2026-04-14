import os
from pydub import AudioSegment
import whisper
import torch

class STTService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("base", device=self.device)

    def transcribe(self, audio_file_path):
        # Whisper handles webm/mp4 directly but let's be safe
        result = self.model.transcribe(audio_file_path)
        return result["text"]

stt_service = STTService()
