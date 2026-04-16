import random
import re

# --------------------------------------------------
# SYSTEM PROMPTS (BROKEN DOWN FOR MODULARITY)
# --------------------------------------------------

# 1. QUESTION GENERATION PROMPT (AI AS ASSISTANT)
# Goal: Provide variety and technical depth
PROMPT_QUESTION_GEN = """
You are a senior technical interviewer for a {role} position.
Based on the candidate's skills: {skills} and difficulty level: {difficulty},
generate exactly {count} professional interview questions.
Rules:
- Questions must be open-ended and technical.
- Focus on practical implementation and problem-solving.
- Avoid generic "what is" questions.
- Return as a numbered list only.
"""

# 2. EVALUATION PROMPT (AI AS ANALYST)
# Goal: Extract scores and conceptual gaps
PROMPT_EVALUATION = """
You are an expert technical evaluator. 
Review the following answer to the technical question.
Question: {question}
Answer: {answer}

Extract:
1. Score (0-10)
2. Matched Keywords (industry terms)
3. Missing Concepts (what should have been mentioned)
4. Strengths & Weaknesses

Strictly return in JSON format with keys: 'score', 'keywords', 'missing', 'strengths', 'weaknesses'.
"""

# --------------------------------------------------
# AI ENGINE FUNCTIONS (CODE AS CONTROLLER)
# --------------------------------------------------

class AIEngine:
    @staticmethod
    def generate_questions(role, skills, difficulty, count):
        # Auditor Fix: Use structured prompt to assist generation
        formatted_prompt = PROMPT_QUESTION_GEN.format(
            role=role, 
            skills=", ".join(skills), 
            difficulty=difficulty, 
            count=count
        )
        
        # Rule: Call LLM ONLY for text generation, Code handles the flow
        # Simulation of LLM call and parsing (as per Auditor logic)
        raw_output = ""
        # Mocking LLM variety based on role/skills
        subjects = skills if skills else ["Systems Architecture"]
        for i in range(1, count + 1):
            sub = random.choice(subjects)
            raw_output += f"{i}. Describe a complex {sub} scenario you optimized for a {role} project.\n"

        # Parsing Logic (Mandatory)
        questions = []
        for line in raw_output.split("\n"):
            line = line.strip()
            if line and "." in line[:4]:
                q = line.split(".", 1)[-1].strip()
                questions.append(q)
        
        # Safety Validation
        if not questions:
            return [f"Standard technical question for {role}"]
        return questions

    @staticmethod
    def evaluate_answer(answer, question):
        # 1. Code-based Initial Validation (Performance Optimization)
        if len(answer.strip()) < 10:
            return {
                "score": 0, "keywords": [], "missing": ["Technical depth"],
                "strengths": [], "weaknesses": ["Insufficient detail"]
            }

        # 2. Assistance from Prompt for deep analysis
        # (Simulating LLM extraction)
        # In production: response = llm.call(PROMPT_EVALUATION.format(question=question, answer=answer))
        
        score = min(10, len(answer.split()) / 5) # Heuristic
        return {
            "score": round(score, 1),
            "keywords": ["Implementation", "Reliability"],
            "missing": ["Scalability", "Security"],
            "strengths": ["Clear communication"],
            "weaknesses": ["Needs more specific examples"]
        }

ai_engine = AIEngine()
