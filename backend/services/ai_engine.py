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
                    return clean_questions[:count]
            except Exception:
                if attempt == max_retries - 1:
                    return (fallback_questions * 2)[:count] # Ensure correct count
                time.sleep(1) # Wait before retry
        
        return (fallback_questions * 2)[:count]

    def evaluate_answer(self, question, answer):
        """
        UPGRADED PHASE 2: Controlled AI Evaluation with deterministic guards.
        """
        clean_answer = answer.strip()
        
        # 1. DETERMINISTIC PRE-VALIDATION (Rule-Based)
        if not clean_answer or len(clean_answer) < 5 or re.match(r'^[a-zA-Z0-9\s]{1,5}$', clean_answer):
            return {
                "score": 0.0,
                "keywords_matched": [],
                "missing_concepts": ["Valid technical explanation required"],
                "strengths": [],
                "weaknesses": ["Invalid or insufficient answer"]
            }

        # 2. CONTROLLED GEMINI LAYER (Ultra-Strong Prompt)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # ULTRA-STRONG PROMPT IMPLEMENTED
                prompt = f"""
                You are a STRICT TECHNICAL INTERVIEW EVALUATOR.
                You MUST evaluate the candidate's answer based ONLY on the given question and answer.

                🚨 STRICT RULES
                - DO NOT assume anything outside the answer
                - DO NOT add extra knowledge
                - DO NOT hallucinate
                - DO NOT include any text outside JSON
                
                🎯 TASK
                Question: {question}
                Answer: {clean_answer}

                📊 OUTPUT FORMAT (STRICT JSON ONLY)
                {{
                "score": number (0-10),
                "keywords_matched": [list of words found in answer],
                "missing_concepts": [important concepts not present],
                "strengths": [based ONLY on answer],
                "weaknesses": [based ONLY on answer]
                }}

                ⚠️ VALIDATION RULES
                If answer is empty OR meaningless: score = 0, weaknesses = ["Invalid or insufficient answer"]
                keywords_matched MUST come ONLY from answer text.
                Return ONLY VALID JSON.
                """
                
                response = self.model.generate_content(prompt)
                
                # 3. JSON EXTRACTION (Regex Guard)
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        eval_data = json.loads(json_match.group())
                        
                        # 4. STRUCTURAL VALIDATION (Schema Guard)
                        required = ["score", "keywords_matched", "missing_concepts", "strengths", "weaknesses"]
                        if all(k in eval_data for k in required):
                            # Ensure deterministic types
                            return {
                                "score": float(eval_data["score"]),
                                "keywords_matched": list(eval_data["keywords_matched"]),
                                "missing_concepts": list(eval_data["missing_concepts"]),
                                "strengths": list(eval_data["strengths"]),
                                "weaknesses": list(eval_data["weaknesses"])
                            }
                    except (json.JSONDecodeError, ValueError):
                        pass # try again
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue

        # 5. DETERMINISTIC FALLBACK ENGINE (Failure Guard)
        fallback_score = 1.0 if len(clean_answer) > 20 else 0.0
        return {
            "score": fallback_score,
            "keywords_matched": [],
            "missing_concepts": ["Deep technical audit could not be performed"],
            "strengths": ["Length is sufficient" if len(clean_answer) > 20 else "Direct response"],
            "weaknesses": ["Automated system fallback triggered"]
        }

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
