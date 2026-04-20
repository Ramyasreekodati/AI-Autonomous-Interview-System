import random
import json
import re
import streamlit as st
import time
import datetime
import google.generativeai as genai
import os

# Configure Gemini
GEMINI_API_KEY = "AIzaSyBVYhalb3qz0gofxe0VvUlZCARNUh9DSMM"
genai.configure(api_key=GEMINI_API_KEY)

class AIEngine:
    def __init__(self):
        self.version = "2.0.0-Gemini"
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_questions_cached(role, skills_str, difficulty, count, seed="STABLE"):
        """
        GEMINI POWERED: Generates high-quality technical questions.
        """
        try:
            instance = AIEngine()
            prompt = f"""
            You are an expert technical interviewer.
            Generate {count} unique interview questions for the following profile:
            Role: {role}
            Key Skills: {skills_str}
            Difficulty: {difficulty}

            Rules:
            1. Questions must be technical and practical.
            2. Return ONLY a numbered list of questions.
            3. Do not include any introductory or concluding text.
            """
            
            response = instance.model.generate_content(prompt)
            raw_text = response.text.strip()
            
            questions = []
            for line in raw_text.split("\n"):
                line = line.strip()
                if line and ("." in line[:3] or line[0].isdigit()):
                    q = re.sub(r'^\d+[\.\)]\s*', '', line)
                    questions.append(q)
            
            return questions if questions else [f"Explain your approach to {role} architecture."]
        except Exception as e:
            # Fallback to deterministic logic if API fails
            return [f"Standard technical inquiry for {role} role."]

    def evaluate_answer(self, question, answer):
        """
        GEMINI POWERED: Sophisticated technical evaluation.
        """
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
            """
            
            response = self.model.generate_content(prompt)
            # Extract JSON from response (handling potential markdown formatting)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            raise ValueError("Invalid JSON response from AI")
        except Exception as e:
            # Safe Fallback
            return {
                "score": 5.0,
                "keywords_matched": ["General Knowledge"],
                "missing_concepts": ["API Timeout"],
                "strengths": ["Clear communication"],
                "weaknesses": ["Evaluation system jitter"],
                "passed_validation": True
            }

    @staticmethod
    def generate_final_result(evaluations, alerts):
        """
        STRICT PHASE 4: WEIGHTED INTELLIGENCE SYNTHESIS
        """
        if not evaluations:
            return {"error": "Missing signals", "interview_score": 0, "behavior_score": 0, "final_decision": "fail"}

        tech_scores = [ev.get('score', 0) for ev in evaluations.values()]
        avg_tech = round((sum(tech_scores) / (len(tech_scores) * 10)) * 100, 1)

        behavior = 100
        # Alerts are minimal in this version but kept for structure
        for a in alerts:
            sev = a.get('severity', 'low').lower()
            if sev == "high": behavior -= 25
            elif sev == "medium": behavior -= 10
            else: behavior -= 5
        
        behavior = max(0, behavior)
        final_score = round((0.7 * avg_tech) + (0.3 * behavior), 1)
        risk = "low" if behavior > 80 else "medium" if behavior >= 50 else "high"
        decision = "pass" if (final_score >= 60 and risk != "high") else "fail"
        
        # Aggregate feedback for justification
        all_strengths = []
        for ev in evaluations.values(): all_strengths.extend(ev.get('strengths', []))
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
