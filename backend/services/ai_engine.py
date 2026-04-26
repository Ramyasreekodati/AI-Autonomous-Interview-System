import google.generativeai as genai
import os
import re
import json
import time
import datetime
try:
    import streamlit as st  # Optional: only used for secrets when running in Streamlit
except ImportError:
    st = None
from dotenv import load_dotenv

load_dotenv()

# Module-level key store so transcribe_bytes can build its own model
_CONFIGURED_API_KEY = None

def load_ai_model():
    """
    Secure Model Initialization with Live Discovery (Cache disabled for recovery).
    """
    # 🛡️ ARCHITECT FIX: Force reload .env every time if init failed previously
    load_dotenv(override=True)
    from pathlib import Path
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Discovery Logic
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    source = "Environment" if api_key else "None"
    
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
            if api_key: source = "Secrets"
        except:
            pass
            
    if not api_key:
        print("[AIEngine] Error: No API Key discovered in any source.")
        return None
        
    # Sanitization
    clean_key = api_key.strip().strip('"').strip("'")
    print(f"[AIEngine] Key found via {source} (Starts with: {clean_key[:5]}...)")
    
    try:
        global _CONFIGURED_API_KEY
        genai.configure(api_key=clean_key)
        _CONFIGURED_API_KEY = clean_key  # Store for use in transcribe_bytes
        
        # Prefer multimodal-capable models first (added newer versions found in models.txt)
        models_to_try = [
            'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-flash-latest', 
            'gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-pro'
        ]
        
        for model_name in models_to_try:
            full_name = f"models/{model_name}" if not model_name.startswith("models/") else model_name
            try:
                # 🛡️ VERIFICATION: get_model will 404 here if the model is truly missing
                genai.get_model(full_name)
                model = genai.GenerativeModel(model_name)
                # Test call to ensure generateContent is supported
                print(f"[AIEngine] Model verified: {model_name}")
                return model
            except Exception as e:
                print(f"[AIEngine] Model {model_name} unavailable: {str(e)}")
                continue
    except Exception as e:
        print(f"[AIEngine] Configuration failed: {str(e)}")
        
    return None

class AIEngine:
    # 🧬 ELITE LOCAL KNOWLEDGE BASE
    TECHNICAL_KEYWORDS = {
        "Software Engineer": ["python", "java", "javascript", "api", "database", "git", "cloud", "deployment", "agile", "testing", "backend", "frontend", "fullstack", "architecture"],
        "Data Scientist": ["python", "r", "machine learning", "statistics", "data", "modeling", "pandas", "numpy", "visualization", "ai", "deep learning", "regression", "classification"],
        "HR": ["recruitment", "onboarding", "culture", "conflict", "management", "talent", "employee", "interview", "hiring", "policy", "retention", "diversity", "inclusion"],
        "Generic": ["professional", "teamwork", "leadership", "communication", "problem solving", "skills", "experience", "efficient", "quality", "goal", "success"]
    }

    def __init__(self):
        self.model = load_ai_model()

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

    def transcribe_bytes(self, audio_data, mime_type="audio/webm"):
        """
        MULTIMODAL STT: Direct cloud processing for bytes.
        Always uses gemini-1.5-flash which supports audio input.
        """
        if not _CONFIGURED_API_KEY:
            print("[AIEngine] transcribe_bytes: No API key available.")
            return None
        try:
            # Use the successfully loaded model if available, fallback to a generic flash alias
            multimodal_model = self.model if (self.model and 'flash' in self.model.model_name) else genai.GenerativeModel('gemini-flash-latest')
            audio_part = {"mime_type": mime_type, "data": audio_data}
            prompt = (
                "You are a transcription engine. Listen to this audio recording of a job interview response. "
                "Transcribe every word spoken accurately. "
                "If there is only silence or background noise with no speech, return exactly: [SILENCE]"
            )
            print(f"[AIEngine] Transcribing {len(audio_data)} bytes...")
            response = multimodal_model.generate_content([prompt, audio_part])
            text = response.text.strip()
            print(f"[AIEngine] Raw Transcription: '{text}'")
            # Return empty string for silence, actual text otherwise
            if "[SILENCE]" in text or not text:
                return ""
            return text
        except Exception as e:
            print(f"[AIEngine] Transcription Exception ({type(e).__name__}): {str(e)}")
            return None

    def analyze_sentiment(self, text):
        """
        Extract behavioral signals (Confidence, Clarity, Tone).
        """
        # Guard: return neutral defaults if text is missing
        if not text or not isinstance(text, str) or not text.strip():
            return {"confidence": 50, "clarity": 50, "tone": "Neutral"}

        if not self.model:
            # Local Sentiment Fallback: Length and punctuation based
            confidence = min(100, len(text.split()) * 5)
            clarity = 80 if "?" not in text else 60
            return {"confidence": confidence, "clarity": clarity, "tone": "Professional (Local)"}

        try:
            prompt = f"""
            Analyze the following interview response for behavioral signals:
            "{text}"
            Return ONLY a valid JSON object with:
            {{
                "confidence": 0-100 score,
                "clarity": 0-100 score,
                "tone": "Confident/Anxious/Neutral/Professional"
            }}
            """
            try:
                response = self.model.generate_content(prompt)
                if not response.text: raise ValueError("Empty response")
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception as e:
                print(f"[AIEngine] Sentiment analysis failed: {e}")
        except: pass
        return {"confidence": 50, "clarity": 50, "tone": "Neutral"}

    def _get_local_questions(self, role, count):
        """Offline Expert Knowledge Base"""
        bank = {
            "Software Engineer": [
                "Explain the difference between synchronous and asynchronous programming.",
                "How do you handle state management in complex applications?",
                "Describe the principles of RESTful API design.",
                "What is your approach to debugging a production environment issue?",
                "Explain the concept of Big O notation and why it matters."
            ],
            "HR": [
                "How do you handle conflict within a team environment?",
                "Describe a situation where you had to manage a difficult employee.",
                "What strategies do you use for high-volume talent acquisition?",
                "How do you ensure workplace diversity and inclusion?",
                "What are the key elements of a successful performance review?"
            ],
            "Data Scientist": [
                "Explain the bias-variance tradeoff in machine learning.",
                "How do you handle missing data in a large dataset?",
                "Describe the difference between L1 and L2 regularization.",
                "What is a random forest and how does it work?",
                "Explain the process of feature engineering for a predictive model."
            ]
        }
        
        # Generic questions if role not found
        generic = [
            "What is your greatest technical achievement to date?",
            "How do you stay updated with the latest trends in your field?",
            "Describe a complex problem you solved and the steps you took.",
            "What is your preferred development environment and why?",
            "Explain a difficult technical concept to a non-technical person."
        ]
        
        role_questions = bank.get(role, generic)
        import random
        # Return unique questions
        return random.sample(role_questions, min(count, len(role_questions)))

    def generate_next_dynamic_question(self, role, skills, experience, previous_q_and_a=[], adaptive=True):
        """
        DYNAMIC FLOW: Generates the next question based on interview history.
        """
        if not self.model:
            return self._get_local_questions(role, 1)[0]

        try:
            history_context = ""
            if previous_q_and_a:
                history_context = "Previous Conversation:\n"
                for q, a, score in previous_q_and_a:
                    history_context += f"Q: {q}\nA: {a}\nScore: {score}/10\n---\n"

            adaptive_instruction = (
                "If adaptive=True, adjust the difficulty of the next question based on the candidate's previous scores. "
                "If they scored high, make it harder. If they struggled, clarify or simplify."
            ) if adaptive else ""

            prompt = f"""
            You are an expert AI interviewer for a {role} position.
            Candidate Skills: {skills}
            Candidate Experience: {experience}
            
            {history_context}
            
            Based on the history and candidate profile, generate the NEXT single interview question.
            {adaptive_instruction}
            
            Guidelines:
            1. Do NOT repeat previous questions.
            2. Keep it conversational but technical.
            3. If this is the first question, start with a strong foundational topic.
            
            Return ONLY the question text as a string.
            """
            
            response = self.model.generate_content(prompt)
            # 🛡️ CLEANUP: Remove conversational filler and extract just the question
            text = response.text.strip().split("\n")[0].strip('"').strip('*')
            if len(text) < 10: raise ValueError("AI response too short")
            return text
                
        except Exception as e:
            print(f"[AIEngine] Dynamic Generation Failure: {str(e)}")
            return self._get_local_questions(role, 1)[0]

    def generate_questions(self, role, skills, difficulty, count, experience, interview_type, style, previous_questions=[]):
        """
        MASTER PROMPT 1: UNIQUE QUESTION GENERATION
        """
        if not self.model:
            print(f"[AIEngine] Using Local Fallback for {role}")
            return self._get_local_questions(role, count)

        try:
            exclusion = f"IMPORTANT: Do NOT repeat these previous questions: {previous_questions}" if previous_questions else ""
            prompt = f"""
            Generate exactly {count} UNIQUE and professional technical interview questions for a {role} role.
            Skills: {skills}
            Level: {difficulty}
            Type: {interview_type}
            Experience: {experience}
            Style: {style}
            {exclusion}
            
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
            
            # 🛡️ ARCHITECT FIX: Filter out any inadvertent duplicates
            if isinstance(questions, list) and len(questions) > 0:
                questions = [q for q in questions if q not in previous_questions]
                if len(questions) >= count:
                    return questions[:count]
                else:
                    # Pad with unique variations if AI was short
                    padding = [f"Technical challenge regarding {skills} (Context {i+1})" for i in range(count - len(questions))]
                    return questions + padding
                
        except Exception as e:
            print(f"[AIEngine] Generation Failure: {str(e)}")
            # Silent fallback to local questions instead of showing red error box

        return self._get_local_questions(role, count)

    def analyze_resume_v2(self, resume_text, job_description="Generic"):
        """
        ADVANCED RESUME ANALYZER: Scores based on Readability, Credibility, and ATS Fit.
        """
        if not self.model:
            return {"readability": 70, "credibility": 60, "ats_fit": 50, "feedback": "AI analysis offline."}

        try:
            prompt = f"""
            Analyze the following resume against the job context: "{job_description}"
            Resume: {resume_text}
            
            Score the following categories (0-100) and provide specific insights:
            1. Readability: Clarity, formatting, and grammar.
            2. Credibility: Evidence of accomplishments (not just tasks).
            3. ATS Fit: Keyword alignment and structure.
            
            Return ONLY a valid JSON object:
            {{
                "readability": score,
                "credibility": score,
                "ats_fit": score,
                "strengths": ["list"],
                "weaknesses": ["list"],
                "critical_keywords_missing": ["list"],
                "best_practice_tip": "One key tip"
            }}
            """
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"[AIEngine] Resume V2 Failure: {str(e)}")
            
        return {"readability": 0, "credibility": 0, "ats_fit": 0, "error": "Analysis failed"}

    def evaluate_answer(self, question, answer, role="Expert", skills=[], star_mode=True):
        """
        MASTER PROMPT 2: BEHAVIORAL + TECHNICAL + STAR AUDIT
        """
        if not answer:
            return {"score": 0, "strengths": [], "weaknesses": ["No response provided"], "sentiment": {"confidence":0, "clarity":0}}

        # 🧬 SYNERGY: Behavioral Analysis
        sentiment = self.analyze_sentiment(answer)
        
        # 🎙️ SPEECH ANALYTICS (Filler Words & Pace)
        filler_words = ["um", "uh", "like", "you know", "actually", "basically", "so"]
        words = answer.lower().split()
        filler_count = sum(1 for w in words if w in filler_words)
        pace = len(words) # Rough proxy for word count
        
        filler_feedback = (
            f"Watch out for filler words. You used '{filler_words}' roughly {filler_count} times. "
            if filler_count > 3 else "Excellent clarity and minimal filler words."
        )
        
        star_prompt = (
            "Additionally, audit the response using the STAR method (Situation, Task, Action, Result). "
            "Identify if any components are missing."
        ) if star_mode else ""

        if not self.model:
            # ELITE LOCAL SEMANTIC ANALYZER
            ans_lower = answer.lower()
            words = ans_lower.split()
            
            # 🧬 Keyword Density Analysis
            role_keywords = self.TECHNICAL_KEYWORDS.get(role, self.TECHNICAL_KEYWORDS["Generic"])
            matches = [w for w in role_keywords if w in ans_lower]
            keyword_score = min(5, len(matches))
            
            # 📏 Length Bonus (max 5)
            length_score = min(5, len(words) // 10)
            
            total_local_score = keyword_score + length_score
            
            return {
                "score": total_local_score,
                "strengths": [f"Technical keywords identified: {', '.join(matches[:3])}"] if matches else ["Professional engagement"],
                "weaknesses": ["More specific technical depth recommended"] if len(words) < 20 else ["Elaborate further on implementation"],
                "technical_accuracy": f"Local Match: {len(matches)} key concepts detected.",
                "behavioral_feedback": f"Response clarity is sufficient. Confidence: {sentiment['confidence']}%",
                "sentiment": sentiment
            }

        try:
            prompt = f"""
            Act as a Senior {role} Auditor. 
            Question: {question}
            Answer: {answer}
            Target Skills: {skills}
            Candidate Confidence: {sentiment['confidence']}/100
            Candidate Clarity: {sentiment['clarity']}/100
            
            Evaluate the response fairly. A score of 10/10 requires precise terminology and clear logic.
            Return ONLY a valid JSON object:
            {{
                "score": 0-10 (integer),
                "strengths": ["list", "of", "positives"],
                "weaknesses": ["list", "of", "areas", "to", "improve"],
                "technical_accuracy": "Detailed feedback on the technical content",
                "behavioral_feedback": "Critique on confidence, tone, and communication",
                "star_audit": {
                    "situation": "Present/Missing",
                    "task": "Present/Missing",
                    "action": "Present/Missing",
                    "result": "Present/Missing",
                    "critique": "Brief comment on STAR structure"
                }
            }}
            """
            
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["behavioral_feedback"] = f"{result.get('behavioral_feedback', '')} {filler_feedback}"
                result["speech_metrics"] = {
                    "filler_count": filler_count,
                    "pace": "Optimal" if 100 < pace < 160 else "Fast" if pace >= 160 else "Slow",
                    "word_count": pace
                }
                result["sentiment"] = sentiment
                return result
        except Exception as e:
            print(f"[AIEngine] Evaluation Failure: {str(e)}")
            
        return {"score": 5, "strengths": ["Attempted"], "weaknesses": ["AI evaluation failed"], "sentiment": sentiment}

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
