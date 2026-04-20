import os
import time

class STTService:
    def __init__(self):
        self._model = None

    def transcribe(self, audio_data):
        """
        LIGHTWEIGHT STT (Cloud Optimized)
        Currently disabled to keep build size small.
        """
        if audio_data is None:
            return ""

        return "Speech-to-Text is currently in 'Safe Mode'. Please type your response below."

stt_service = STTService()
