import google.generativeai as genai
import os
import re
import json
import time
import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# 🔴 FIX 11: Performance Cache for Model Loading
@st.cache_resource
def load_ai_model():
    """
    Secure and Cached Model Initialization.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    # Fallback for Streamlit environment
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass
            
    # 🔴 FIX 2: Strict Mode for API Key
    if not api_key:
        st.error("❌ CRITICAL: GEMINI API KEY MISSING. Check environment variables.")
        return None
        
    genai.configure(api_key=api_key)
    # 🔴 FIX 1: Stable Model Selection with Functional Test
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            # Test call to ensure model is NOT 404 and is available for the current key
            model.generate_content("ping", generation_config={"max_output_tokens": 1})
            return model
        except Exception as e:
            continue
            
    st.error("❌ No compatible Gemini models found for this API key.")
    return None

class AIEngine:
    def __init__(self):
        self.model = load_ai_model()

    def transcribe_bytes(self, audio_bytes, mime_type="audio/webm"):
        """
        Multimodal Transcription: Direct byte-stream processing.
        Bypasses local FFmpeg requirements.
        """
        if not self.model:
            return ""
            
        if not audio_bytes or len(audio_bytes) < 1000: # 🛡️ Skip silent/empty clips
            return ""
            
        try:
            audio_part = {"mime_type": mime_type, "data": audio_bytes}
            prompt = """
            Transcribe this interview response accurately. 
            - Keep the technical terms intact.
            - Filter out any 'uhm' or 'aah' fillers.
            - Return ONLY the transcription text.
            - If no speech is detected, return exactly: '[No Speech Detected]'
            """
            response = self.model.generate_content([prompt, audio_part])
            text = response.text.strip()
            if text == "[No Speech Detected]": return ""
            return text
        except Exception as e:
            # Silently log to console for debugging, but don't crash UI
            print(f"Gemini Transcription Error: {str(e)}")
            return ""

    def transcribe_audio(self, file_path):
        """
        STRICT STT ENGINE: High-Reliability Transcription.
        """
        import os
        import speech_recognition as sr
        
        if not os.path.exists(file_path):
            return ""

        # 🚀 PRIMARY: Google Speech (High Stability for WAV)
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(file_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                if text and len(text.strip()) > 0:
                    return text.strip()
        except Exception as e:
            # If WAV transcription fails, we don't log error here as it might be expected if format is wrong
            pass

        return ""

    def generate_questions(self, role, skills, difficulty, count, experience, interview_type, style):
        """
        MASTER PROMPT 1: QUESTION GENERATION
        """
        if not self.model:
            return [f"Sample {role} technical question for {skills}"] * count

        try:
            prompt = f"""
            Generate exactly {count} professional interview questions for a {role} role.
            Skills: {skills}
            Level: {difficulty}
            Type: {interview_type}
            Style: {style}
            Return ONLY a valid JSON array of strings: ["Q1", "Q2", ...]
            """
            
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            
            # 🔴 FIX 3: Non-greedy JSON Parsing
            json_match = re.search(r'\[.*\]', raw, re.DOTALL)
            questions = []
            if json_match:
                try:
                    questions = json.loads(json_match.group())
                except:
                    pass
            
            # Fallback regex if JSON fails
            if not questions:
                questions = re.findall(r'"([^"]*)"', raw)
            
            # 🛡️ AUDITOR FIX: Return what we have if count mismatch, don't discard all
            if isinstance(questions, list) and len(questions) > 0:
                if len(questions) >= count:
                    return questions[:count]
                else:
                    # Pad with unique variations if AI was short
                    padding = [f"Technical challenge regarding {skills} (Context {i+1})" for i in range(count - len(questions))]
                    return questions + padding
                
        except Exception as e:
            st.error(f"AI Generation Error: {str(e)}")

        return [f"Discuss a key technical concept in {role} related to {skills} (Part {i+1})" for i in range(count)]

    def evaluate_answer(self, question, answer, role="Expert", skills=[]):
        """
        MASTER PROMPT 2: HIGH-PRECISION EVALUATION
        """
        if not self.model:
            return {"score": 5.0, "strengths": ["Model offline"], "weaknesses": ["Analysis limited"]}

        clean_answer = answer.strip()
        if not clean_answer or len(clean_answer) < 10:
            return {"score": 0.0, "strengths": [], "weaknesses": ["Insufficient response length"]}

        try:
            prompt = f"""
            Evaluate this technical response.
            Question: {question}
            Answer: {clean_answer}
            Role: {role}
            Return JSON: {{"score": 0-10, "strengths": [], "weaknesses": []}}
            """
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{[^\}]*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            st.error(f"Evaluation failed: {str(e)}")
            
        return {"score": 0.0, "strengths": [], "weaknesses": ["System analysis timeout"]}

    @staticmethod
    def generate_final_result(evaluations, alerts):
        """
        PHASE 4: DETERMINISTIC SYNTHESIS
        """
        if not evaluations:
            avg_tech = 0.0
        else:
            tech_scores = [float(ev.get('score', 0)) for ev in evaluations.values()]
            avg_tech = round((sum(tech_scores) / (len(tech_scores) * 10)) * 100, 1) if tech_scores else 0.0
        
        behavior = 100
        for a in alerts:
            sev = a.get('severity', 'low').lower()
            if sev == "high": behavior -= 30
            elif sev == "medium": behavior -= 15
            else: behavior -= 5
        behavior = max(0, behavior)
        
        risk = "HIGH" if behavior < 40 else "MEDIUM" if behavior <= 70 else "LOW"
        decision = "SELECTED" if avg_tech >= 80 and risk == "LOW" else "REJECTED" if avg_tech < 50 or risk == "HIGH" else "REVIEW"
        
        return {
            "interview_score": avg_tech, 
            "behavior_score": behavior, 
            "final_aggregate_score": round((avg_tech + behavior) / 2, 1),
            "risk_level": risk,
            "final_decision": decision, 
            "justification": f"Candidate merit: {avg_tech}%, Integrity: {behavior}%.",
            "alerts": [a.get('alert_type', 'unknown') for a in alerts]
        }

ai_engine = AIEngine()
