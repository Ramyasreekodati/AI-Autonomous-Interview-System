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
        DETERMINISTIC PHASE 4 INTEGRATION ENGINE
        Fuses technical merit (Phase 2) and proctoring signals (Phase 3).
        """
        # 1. INTERVIEW SCORE (Avg of Phase 2 Scores)
        if not evaluations:
            avg_tech = 0.0
        else:
            tech_scores = [float(ev.get('score', 0)) for ev in evaluations.values() if isinstance(ev, dict)]
            if not tech_scores:
                avg_tech = 0.0
            else:
                # Convert 0-10 scale to 0-100 scale
                avg_tech = round((sum(tech_scores) / (len(tech_scores) * 10)) * 100, 1)

        # 2. BEHAVIOR SCORE (Strict Weights: High -30, Medium -15, Low -5)
        behavior = 100
        for a in alerts:
            sev = a.get('severity', 'low').lower()
            if sev == "high": behavior -= 30
            elif sev == "medium": behavior -= 15
            else: behavior -= 5
        behavior = max(0, behavior)

        # 3. RISK ANALYSIS (Strict Thresholds: HIGH < 40, MEDIUM 40-70, LOW > 70)
        risk = "HIGH" if behavior < 40 else "MEDIUM" if behavior <= 70 else "LOW"

        # 4. FINAL DECISION ENGINE (Rule-Based Matrix)
        if avg_tech >= 80 and risk == "LOW":
            decision = "SELECTED"
        elif avg_tech < 50 or risk == "HIGH":
            decision = "REJECTED"
        else:
            decision = "REVIEW"

        # 5. DETERMINISTIC JUSTIFICATION (No AI Hallucination)
        justification = (
            f"Candidate achieved a merit score of {avg_tech}% with a {risk.lower()} behavioral risk level. "
            f"System recorded {len(alerts)} proctoring signals during the audit."
        )

        # 6. STRICT JSON OUTPUT (No extra keys)
        return {
            "interview_score": avg_tech,
            "behavior_score": behavior,
            "risk_level": risk,
            "alerts": alerts,
            "final_decision": decision,
            "justification": justification
        }

ai_engine = AIEngine()
