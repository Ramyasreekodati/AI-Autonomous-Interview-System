import random
import json
import re
import streamlit as st
import time
import datetime
import google.generativeai as genai
import os

# Configure Gemini
# Prioritize Streamlit Secrets, then environment variables
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or "AIzaSyBVYhalb3qz0gofxe0VvUlZCARNUh9DSMM"
genai.configure(api_key=GEMINI_API_KEY)

class AIEngine:
    def __init__(self):
        self.version = "2.1.0-Stable"
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_questions_cached(self, role, skills_str, difficulty, count, seed="STABLE"):
        """
        GEMINI POWERED: Generates high-quality technical questions with improved prompting, parsing, and retries.
        """
        max_retries = 3
        fallback_questions = [
            f"Explain your approach to {role} architecture.",
            f"Describe a challenging project you worked on related to {role}.",
            f"How do you stay updated with the latest trends in {skills_str}?",
            f"Describe your process for debugging complex issues in {role} projects.",
            f"What are the most critical security considerations in your work?"
        ]
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                You are a professional technical interviewer.
                Generate {count} interview questions for:
                Role: {role}
                Skills: {skills_str}
                Difficulty: {difficulty}

                Also ensure:
                - Questions test real-world knowledge
                - Mix theory + scenario-based
                - Avoid repetition
                - Return ONLY the questions, one per line.
                - Do not include numbers, introductory or concluding text.
                """
                
                response = self.model.generate_content(prompt)
                raw_text = response.text.strip()
                
                # Safer parsing: split lines and filter empty ones
                questions = [line.strip() for line in raw_text.split("\n") if line.strip()]
                
                # If AI still included numbers, clean them up
                clean_questions = []
                for q in questions:
                    q = re.sub(r'^\d+[\.\)]\s*', '', q)
                    clean_questions.append(q)
                
                if clean_questions:
        # API Key Retrieval (Streamlit Secrets -> Environment)
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Fallback for local dev if needed, but production MUST have it
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            st.error("Missing Gemini API Key. Please configure GEMINI_API_KEY in Streamlit Secrets.")
            st.stop()
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

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
