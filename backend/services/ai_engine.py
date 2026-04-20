import google.generativeai as genai
import os
import re
import json
import time
import datetime
import streamlit as st

class AIEngine:
    def __init__(self):
        # API Key Retrieval (Streamlit Secrets -> Environment)
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            st.error("Missing Gemini API Key. Please configure GEMINI_API_KEY in Streamlit Secrets.")
            st.stop()
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def transcribe_audio(self, audio_bytes):
        """
        Transcribe audio bytes using Gemini 1.5 Flash.
        """
        try:
            # Wrap bytes for Gemini
            audio_part = {
                "mime_type": "audio/wav",
                "data": audio_bytes
            }
            prompt = "Transcribe the following audio precisely. Return ONLY the transcription text."
            response = self.model.generate_content([prompt, audio_part])
            return response.text.strip()
        except Exception as e:
            return f"Transcription Error: {str(e)}"

    @st.cache_data
    def generate_questions_cached(_self, role, skills, difficulty, count):
        """
        MASTER PROMPT 1: QUESTION GENERATION (PHASE 1)
        """
        try:
            prompt = f"""
            You are a senior technical interviewer.
            Generate high-quality interview questions.

            INPUT:
            Role: {role}
            Skills: {skills}
            Difficulty: {difficulty}
            Number of questions: {count}

            RULES:
            - Questions must be realistic and industry-level
            - Mix conceptual and practical questions
            - Avoid generic questions
            - Do NOT repeat
            - Keep questions clear and concise

            OUTPUT:
            Return ONLY a numbered list of questions.
            """
            
            response = _self.model.generate_content(prompt)
            lines = [l.split('.', 1)[-1].strip() for l in response.text.strip().split('\n') if l.strip() and '.' in l]
            
            # BIAS AUDIT (REGEX LAYER)
            questions = [q for q in lines if not re.search(r'\b(he|she|him|her|his|hers)\b', q, re.I)]
            
            if not questions:
                return [f"Explain your approach to {skills[0]} at a {difficulty} level."]
            return questions[:count]
        except Exception:
            return [f"What are the core principles of {skills[0]} in a production environment?"]

    def evaluate_answer(self, question, answer):
        """
        MASTER PROMPT 2: EVALUATION ENGINE (PHASE 2 - STRICT)
        """
        clean_answer = answer.strip()
        
        # DETERMINISTIC GUARD (PHASE 2 REQUIREMENT)
        if not clean_answer or len(clean_answer) < 5 or re.match(r'^[a-zA-Z0-9\s]{1,5}$', clean_answer):
            return {
                "score": 0.0, 
                "keywords_matched": [], 
                "missing_concepts": ["Valid technical answer required"],
                "strengths": [], 
                "weaknesses": ["Invalid or insufficient answer"]
            }

        prompt = f"""
        You are a STRICT TECHNICAL INTERVIEW EVALUATOR.
        You MUST evaluate ONLY based on the given answer.

        INPUT
        Question: {question}
        Answer: {clean_answer}

        STRICT RULES:
        - DO NOT assume anything beyond the answer
        - DO NOT hallucinate
        - DO NOT add external knowledge
        - DO NOT output anything outside JSON
        
        OUTPUT FORMAT (STRICT JSON):
        {{
        "score": 0-10,
        "keywords_matched": [],
        "missing_concepts": [],
        "strengths": [],
        "weaknesses": []
        }}

        VALIDATION RULES:
        If answer is empty or meaningless: score = 0, weaknesses = ["Invalid or insufficient answer"]
        keywords_matched MUST come from answer.
        RETURN ONLY VALID JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
                # Ensure all 5 keys exist
                required = ["score", "keywords_matched", "missing_concepts", "strengths", "weaknesses"]
                if all(k in eval_data for k in required):
                    return eval_data
        except Exception:
            pass
        
        # DETERMINISTIC FALLBACK
        return {
            "score": 1.0 if len(clean_answer) > 20 else 0.0, 
            "keywords_matched": [], 
            "missing_concepts": ["Audit Failure"], 
            "strengths": [], 
            "weaknesses": ["System Fallback Mode Active"]
        }

    def generate_follow_up(self, question, answer):
        """
        MASTER PROMPT 3: FOLLOW-UP QUESTION (PHASE 5 - UX BOOST)
        """
        try:
            prompt = f"""
            You are an AI interviewer continuing a live interview.
            Based on the candidate’s previous answer, generate ONE follow-up question.

            INPUT:
            Question: {question}
            Answer: {answer}

            RULES:
            - Ask a deeper or clarifying question
            - Keep it relevant to the answer
            - Do NOT repeat the same question
            - Keep it short and professional

            OUTPUT:
            Return ONLY one question.
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "Can you elaborate more on the technical challenges mentioned in your answer?"

    @staticmethod
    def generate_final_result(evaluations, alerts):
        """
        PHASE 4: DETERMINISTIC SYNTHESIS (RULE-BASED)
        Fuses merit (Phase 2) and integrity (Phase 3).
        """
        if not evaluations:
            avg_tech = 0.0
        else:
            tech_scores = [float(ev.get('score', 0)) for ev in evaluations.values() if isinstance(ev, dict)]
            avg_tech = round((sum(tech_scores) / (len(tech_scores) * 10)) * 100, 1) if tech_scores else 0.0
        
        behavior = 100
        for a in alerts:
            sev = a.get('severity', 'low').lower()
            if sev == "high": behavior -= 30
            elif sev == "medium": behavior -= 15
            else: behavior -= 5
        behavior = max(0, behavior)
        
        risk = "HIGH" if behavior < 40 else "MEDIUM" if behavior <= 70 else "LOW"
        
        # Decision Matrix
        if avg_tech >= 80 and risk == "LOW":
            decision = "SELECTED"
        elif avg_tech < 50 or risk == "HIGH":
            decision = "REJECTED"
        else:
            decision = "REVIEW"
        
        return {
            "interview_score": avg_tech, 
            "behavior_score": behavior, 
            "risk_level": risk,
            "alerts": alerts, 
            "final_decision": decision, 
            "justification": f"Candidate merit evaluated at {avg_tech}% with a {risk.lower()} behavioral risk profile."
        }

ai_engine = AIEngine()
