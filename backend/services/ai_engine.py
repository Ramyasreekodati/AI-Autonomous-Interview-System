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
    def generate_questions_cached(role, skills_str, difficulty, count, seed="STABLE"):
        """
        GEMINI POWERED: Generates high-quality technical questions with improved prompting, parsing, and retries.
        """
        instance = AIEngine()
        max_retries = 3
        
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
                
                response = instance.model.generate_content(prompt)
                raw_text = response.text.strip()
                
                # Safer parsing: split lines and filter empty ones
                questions = [line.strip() for line in raw_text.split("\n") if line.strip()]
                
                # If AI still included numbers, clean them up
                clean_questions = []
                for q in questions:
                    q = re.sub(r'^\d+[\.\)]\s*', '', q)
                    clean_questions.append(q)
                
                if clean_questions:
                    return clean_questions[:count]
            except Exception as e:
                if attempt == max_retries - 1:
                    return [f"Describe a challenging project you worked on related to {role}."]
                time.sleep(1) # Wait before retry
        
        return [f"Explain your approach to {role} architecture."]

    def evaluate_answer(self, question, answer):
        """
        GEMINI POWERED: Sophisticated technical evaluation with robust JSON parsing and retries.
        """
        default_response = {
            "score": 5.0,
            "keywords_matched": ["General Knowledge"],
            "strengths": ["Communicated response"],
            "weaknesses": ["System fallback triggered"],
            "missing_concepts": ["API Detail"],
            "passed_validation": True
        }
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                prompt = f"""
                As a Senior Technical Auditor, evaluate this interview response:
                Question: {question}
                Candidate Answer: {answer}

                Provide a JSON response with exactly these fields:
                - score: (float between 0 and 10)
                - keywords_matched: (list of strings)
                - strengths: (list of strings)
                - weaknesses: (list of strings)
                - missing_concepts: (list of strings)
                - passed_validation: (boolean)
                
                Return ONLY the JSON.
                """
                
                response = self.model.generate_content(prompt)
                
                # Improved JSON extraction
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass # try again
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return default_response
                time.sleep(1)
        
        return default_response

    @staticmethod
    def generate_final_result(evaluations, alerts):
        """
        WEIGHTED INTELLIGENCE SYNTHESIS
        """
        if not evaluations:
            return {"error": "Missing signals", "interview_score": 0, "behavior_score": 0, "final_decision": "fail"}

        tech_scores = [ev.get('score', 0) for ev in evaluations.values()]
        avg_tech = round((sum(tech_scores) / (len(tech_scores) * 10)) * 100, 1)

        behavior = 100
        # Alerts are minimal in this version
        for a in alerts:
            sev = a.get('severity', 'low').lower()
            if sev == "high": behavior -= 25
            elif sev == "medium": behavior -= 10
            else: behavior -= 5
        
        behavior = max(0, behavior)
        final_score = round((0.7 * avg_tech) + (0.3 * behavior), 1)
        risk = "low" if behavior > 80 else "medium" if behavior >= 50 else "high"
        decision = "pass" if (final_score >= 60 and risk != "high") else "fail"
        
        all_strengths = []
        for ev in evaluations.values(): 
            if isinstance(ev, dict):
                all_strengths.extend(ev.get('strengths', []))
        
        justification = f"Merit: {final_score}%. Key Strength: {all_strengths[0] if all_strengths else 'Direct communication'}."
        
        return {
            "interview_score": avg_tech,
            "behavior_score": behavior,
            "final_score": final_score,
            "risk_level": risk,
            "final_decision": decision,
            "justification": justification
        }

ai_engine = AIEngine()
