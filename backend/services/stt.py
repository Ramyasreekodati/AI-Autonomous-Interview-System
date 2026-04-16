import os
import time

class STTService:
    def __init__(self):
        self._model = None

    def transcribe(self, audio_data):
        """
        PHASE 5: REAL STT IMPLEMENTATION
        Transcribes audio using OpenAI Whisper.
        """
        if audio_data is None:
            return ""

        try:
            import whisper
            if self._model is None:
                # Load lightweight base model for CPU performance
                self._model = whisper.load_model("base")
            
            # Save audio data to temporary file for whisper processing
            temp_filename = f"temp_audio_{int(time.time())}.wav"
            with open(temp_filename, "wb") as f:
                f.write(audio_data.read())
            
            # Transcribe
            result = self._model.transcribe(temp_filename)
            
            # Cleanup
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
            return result.get("text", "").strip()
        except Exception as e:
            return f"Transcription Error: {str(e)}"

stt_service = STTService()
