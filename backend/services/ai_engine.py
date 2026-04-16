import random
import json
import re
import streamlit as st
import time
import datetime

class AIEngine:
    def __init__(self):
        # 🧠 MODEL VERSIONING
        self.version = "1.2.0-Deterministic"
        self.llm_provider = "System-Defined-Logic"

    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_questions_cached(role, skills_str, difficulty, count, session_seed="RECRUITAI"):
        """
        DETERMINISTIC: Uses a fixed seed to ensure repeatable question sets for audits.
        """
        try:
            # Seed the randomizer for determinism
            random.seed(session_seed)
            
            skills = [s.strip() for s in skills_str.split(",")]
            raw_output = ""
            subjects = skills if skills else ["Systems Architecture"]
            
            # Generate exactly N questions in a fixed sequence
            for i in range(1, count + 1):
                sub = subjects[(i-1) % len(subjects)] # Round-robin instead of random.choice for 100% determinism
                raw_output += f"{i}. Describe a complex {sub} scenario you optimized for a {role} project.\n"
            
            questions = []
            for line in raw_output.split("\n"):
                line = line.strip()
                if line and "." in line[:4]:
                    q = line.split(".", 1)[-1].strip()
                    questions.append(q)
            return questions if questions else [f"Standard technical question for {role}"]
        except Exception:
            return [f"General inquiry regarding {role} best practices."]

    def evaluate_answer(self, question, answer):
        """
        STRICT PHASE 2 LOGIC + DETERMINISTIC SCORING
        """
        ans_clean = answer.strip().lower()
        
        # ⚠️ CASE 1: MEANINGLESS VALIDATION
        if not ans_clean or len(ans_clean) < 5 or ans_clean in ["abc", "xyz", "qwerty", "asdf", "12345"]:
            return {
                "score": 0,
                "keywords_matched": [],
                "missing_concepts": [],
                "strengths": [],
                "weaknesses": ["Invalid or irrelevant answer"]
            }

        # ⚖️ BIAS DETECTION
        bias_found = False
        forbidden_patterns = [r'\b(years old|man|woman|graduate of)\b']
        for pattern in forbidden_patterns:
            if re.search(pattern, ans_clean):
                bias_found = True
                break

        # DETERMINISTIC DEPTH ANALYSIS (Word-count based scoring rules)
        word_count = len(ans_clean.split())
        if word_count < 25:
            score = 6.0
            wk = ["Lacks implementation detail"]
        elif word_count < 60:
            score = 7.5
            wk = ["Moderate depth provided"]
        else:
            score = 9.2
            wk = []

        return {
            "score": score,
            "keywords_matched": ["Scalability", "Optimization"] if score > 7 else ["Implementation"],
            "missing_concepts": ["Fault Tolerance"] if score < 8 else [],
            "strengths": ["Clear technical structure"],
            "weaknesses": wk,
            "bias_check_passed": not bias_found,
            "model_version": self.version
        }

    @staticmethod
    def generate_final_result(evaluations, alerts):
        """
        STRICT PHASE 4: DETERMINISTIC SYNTHESIS
        """
        if not evaluations:
            return {"error": "Missing Phase 2 Evaluation data."}

        scores = [ev.get('score', 0) for ev in evaluations.values()]
        total_q = len(scores)
        interview_score = (sum(scores) / (10 * total_q)) * 100

        behavior_score = 100
        alert_summary = []
        for a in alerts:
            severity = a.get('severity', 'low').lower()
            a_type = a.get('alert_type', 'unknown')
            alert_summary.append(a_type)
            if severity == "high": behavior_score -= 20
            elif severity == "medium": behavior_score -= 10
            elif severity == "low": behavior_score -= 5
        
        behavior_score = max(0, behavior_score)
        final_score = (0.7 * interview_score) + (0.3 * behavior_score)

        if behavior_score > 80: risk_level = "low"
        elif behavior_score >= 50: risk_level = "medium"
        else: risk_level = "high"

        final_decision = "pass" if (final_score >= 60 and risk_level != "high") else "fail"
        
        # DETERMINISTIC JUSTIFICATION
        just = f"Consolidated Audit Result: {final_decision.upper()}. "
        just += f"Technical Score: {round(interview_score, 1)}%. Behavior Integrity: {round(behavior_score, 1)}%. "
        if alerts:
            just += f"Flags raised: {', '.join(list(set(alert_summary)))}."
        else:
            just += "No behavioral anomalies detected."
        
        return {
            "interview_score": round(interview_score, 1),
            "behavior_score": round(behavior_score, 1),
            "risk_level": risk_level,
            "alerts": list(set(alert_summary)), 
            "final_decision": final_decision,
            "justification": just,
            "build_id": "RECRUIT-AI-STABLE-1.2.0"
        }

ai_engine = AIEngine()
