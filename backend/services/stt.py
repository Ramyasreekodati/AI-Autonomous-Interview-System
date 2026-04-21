import os
import speech_recognition as sr

class STTService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe(self, audio_path):
        """
        PRODUCTION STT ENGINE: High-Reliability File Processing.
        """
        if not audio_path or not os.path.exists(audio_path):
            return ""

        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio_data)
        except Exception as e:
            return f"STT Error: {str(e)}"

stt_service = STTService()
