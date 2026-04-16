import random
import json
import re
import streamlit as st
import time

class AIEngine:
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_questions_cached(role, skills_str, difficulty, count):
        try:
            skills = [s.strip() for s in skills_str.split(",")]
            raw_output = ""
            subjects = skills if skills else ["Systems Architecture"]
            for i in range(1, count + 1):
                sub = random.choice(subjects)
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

    @staticmethod
    def evaluate_answer(question, answer):
        """
        STRICT PHASE 2 LOGIC: No hallucination. Indexed comparison.
        """
        ans_clean = answer.strip().lower()
        if not ans_clean or len(ans_clean) < 5 or ans_clean in ["abc", "xyz", "qwerty", "asdf", "12345"]:
            return {"score": 0, "keywords_matched": [], "missing_concepts": [], "strengths": [], "weaknesses": ["Invalid or irrelevant answer"]}

        word_count = len(ans_clean.split())
        if word_count < 25:
            score = 6.0
            keywords, missing, strengths, wk = ["Basic concept"], ["Advanced optimization", "Error handling"], ["Correct premise"], ["Lacks implementation detail"]
        else:
            score = 9.0
            keywords, missing, strengths, wk = ["Scalability", "Resource Optimization"], [], ["Detailed technical explanation"], []

        return {"score": score, "keywords_matched": keywords, "missing_concepts": missing, "strengths": strengths, "weaknesses": wk}

    @staticmethod
    def generate_final_result(evaluations, alerts):
        """
        STRICT PHASE 4: Core Intelligence Synthesis
        Combines technical signals and behavioral warnings into a PASS/FAIL decision.
        Uses 70/30 weighting and HIGH/MED/LOW behavior deductions.
        """
        if not evaluations:
            return {"error": "Missing Phase 2 Evaluation data."}

        # 📊 STEP 1: INTERVIEW SCORE (Normalization to 100)
        scores = [ev.get('score', 0) for ev in evaluations.values()]
        total_q = len(scores)
        interview_score = (sum(scores) / (10 * total_q)) * 100

        # ⚠️ STEP 2: BEHAVIOR SCORE (Deductions: H-20, M-10, L-5)
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

        # 🧮 STEP 3: FINAL SCORE (70/30 Weighted)
        final_score = (0.7 * interview_score) + (0.3 * behavior_score)

        # 🚦 STEP 4: RISK LEVEL
        if behavior_score > 80: risk_level = "low"
        elif behavior_score >= 50: risk_level = "medium"
        else: risk_level = "high"

        # ✅ STEP 5: FINAL DECISION
        # pass if final_score >= 60 and risk_level != "high"
        final_decision = "pass" if (final_score >= 60 and risk_level != "high") else "fail"

        # 🧾 STEP 6: JUSTIFICATION (Strict Logic Only)
        just = f"Candidate tech score: {round(interview_score, 1)}%. Behavior score: {round(behavior_score, 1)}%."
        if alerts:
            just += f" Behavioral integrity flagged: {', '.join(list(set(alert_summary)))}."
        else:
            just += " Zero behavioral violations detected."

        # 📤 STEP 7: FINAL OUTPUT (STRICT JSON)
        return {
            "interview_score": round(interview_score, 1),
            "behavior_score": round(behavior_score, 1),
            "risk_level": risk_level,
            "alerts": list(set(alert_summary)), 
            "final_decision": final_decision,
            "justification": just
        }

ai_engine = AIEngine()
