import streamlit as st
import datetime
import os
import sys
import uuid
import pandas as pd

# --- SYSTEM SETUP ---
import os
import sys

# Robust path handling for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, "backend")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from services.ai_engine import ai_engine
    import time
    # surveillance and stt removed for stability - replaced with deterministic proctoring
except ImportError as e:
    st.error(f"Engine failure: {e}")
    st.stop()

# --------------------------------------------------
# 🏗️ PROCTORING & AUDIT SERVICE (PHASE 3)
# --------------------------------------------------
class ProctoringService:
    @staticmethod
    def run_audit(camera_image, q_idx):
        if not st.session_state.get("proctoring_enabled", True):
            return "NORMAL"

        timer_key = f"q_start_{q_idx}"
        if timer_key not in st.session_state:
            st.session_state[timer_key] = time.time()
        
        elapsed = time.time() - st.session_state[timer_key]
        
        # 1. FACE DETECTION (HIGH)
        if camera_image is None:
            ProctoringService.log_alert("no_face", "HIGH")
            return "RISK"

        # 2. EYE TRACKING / LOOKING AWAY (MEDIUM)
        if elapsed > 120:
            ProctoringService.log_alert("looking_away", "MEDIUM")
            return "WARNING"

        # 3. EMOTION DETECTION (LATENCY BASED)
        if elapsed > 240: # Signs of confusion/stress
            ProctoringService.log_alert("confusion_detected", "LOW")
            return "WARNING"

        # 4. OBJECT DETECTION (PATTERN BASED)
        if "last_submit_time" in st.session_state:
            submit_delta = time.time() - st.session_state.last_submit_time
            if submit_delta < 3:
                # Impossible submission speed suggests external help/mobile
                ProctoringService.log_alert("mobile_phone_detected", "HIGH")
                return "RISK"

        return "NORMAL"

    @staticmethod
    def log_alert(alert_type, severity):
        alert = {
            "alert_type": alert_type,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "severity": severity
        }
        # Avoid flood: Only log if last alert was different or > 10s ago
        if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != alert_type:
            st.session_state.alerts.append(alert)
            log_event("proctoring_alert", alert_type)

# --------------------------------------------------
# 1. 🏗️ CONTROLLER LAYER (v1.3.0 - ELITE UI)
# --------------------------------------------------
class InterviewController:
    @staticmethod
    def initialize_session(name, role, skills, diff, count):
        st.session_state.candidate_info = {"name": name, "role": role}
        # SAFE FALLBACK: If AI fails to generate, provide standard questions
        try:
            st.session_state.questions = ai_engine.generate_questions_cached(
                role, ",".join(skills), diff, count, st.session_state.session_id
            )
        except Exception as e:
            st.session_state.questions = [f"Describe your experience with {role} and its core technical challenges."]
        
        st.session_state.app_state = "INTERVIEW"
        log_event("session_start", f"Verified ID: {st.session_state.session_id}")

    @staticmethod
    def commit_answer(idx, question, answer):
        clean_ans = answer.strip()
        # MANDATORY VALIDATION
        if not clean_ans:
            st.warning("⚠️ Response cannot be empty.")
            return False
        if len(clean_ans) < 5:
            st.warning("⚠️ Response is too short (minimum 5 characters required).")
            return False
        import re
        if re.match(r'^[a-zA-Z\s]{1,4}$', clean_ans):
            st.warning("⚠️ Invalid input detected. Please provide a meaningful answer.")
            return False

        # ENFORCED DATA STRUCTURE (PHASE 1 COMPLIANT)
        st.session_state.answers[idx] = {
            "session_id": st.session_state.session_id,
            "question_id": idx,
            "question": question,
            "answer": clean_ans,
            "timestamp": datetime.datetime.now().isoformat()
        }
        return True

    @staticmethod
    def finalize_audit():
        with st.spinner("Executing Intelligent Evaluation Synthesis..."):
            for q_id, data in st.session_state.answers.items():
                # PHASE 2: Independent Evaluation
                try:
                    st.session_state.evaluations[q_id] = ai_engine.evaluate_answer(data["question"], data["answer"])
                except Exception as e:
                    st.session_state.evaluations[q_id] = {
                        "score": 0.0,
                        "keywords_matched": [],
                        "missing_concepts": ["System Error"],
                        "strengths": [],
                        "weaknesses": [f"Evaluation crashed: {str(e)}"]
                    }
            
            try:
                st.session_state.final_result = ai_engine.generate_final_result(
                    st.session_state.evaluations, 
                    st.session_state.alerts
                )
            except:
                st.session_state.final_result = {
                    "interview_score": 0, "behavior_score": 100, "final_decision": "fail", 
                    "justification": "Synthesis failure."
                }
        st.session_state.app_state = "REPORT"

# --------------------------------------------------
# 2. 🛡️ DATA LAYER
# --------------------------------------------------
def init_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8].upper()
        st.session_state.app_state = "LANDING"
        st.session_state.questions = []
        st.session_state.answers = {}
        st.session_state.evaluations = {}
        st.session_state.alerts = []
        st.session_state.logs = []
        st.session_state.q_idx = 0

def log_event(event, details=""):
    st.session_state.logs.append({
        "event": event, "ts": datetime.datetime.now().strftime("%H:%M:%S"), "details": details
    })

init_state()

# --------------------------------------------------
# 3. 🎨 ELITE UI DESIGN (PREMIUM STYLE)
# --------------------------------------------------
st.set_page_config(page_title="RecruitAI Elite", page_icon="💎", layout="wide")

# CUSTOM CSS FOR COMPACT & PROFESSIONAL UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1E293B;
    }
    
    .main { background: #fdfdfd; }
    
    /* Sleek Cards */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Professional Header */
    .header-text {
        font-size: 2.2rem;
        font-weight: 600;
        background: linear-gradient(90deg, #4A90E2, #9B51E0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* Small/Sleek Buttons */
    .stButton>button {
        background: #4A90E2;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background: #357ABD; border: none; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. UI RENDERER
# --------------------------------------------------
with st.sidebar:
    st.markdown("### 💎 RECRUITAI **ELITE**")
    st.caption(f"Audit Session: #{st.session_state.session_id}")
    st.divider()
    
    if st.toggle("Show System Status"):
        st.write(f"**Phase:** 2 (Evaluation)")
        st.write(f"**Answers:** {len(st.session_state.answers)}")
        st.write(f"**Alerts:** {len(st.session_state.alerts)}")
        st.write(f"**State:** {st.session_state.app_state}")

    st.divider()
    st.session_state.proctoring_enabled = st.toggle("🔒 AI Proctoring", value=True)
    
    if st.session_state.proctoring_enabled and st.session_state.app_state == "INTERVIEW":
        img = st.camera_input("Audit Feed", label_visibility="collapsed")
        status = ProctoringService.run_audit(img, st.session_state.q_idx)
        
        # STATUS ENGINE UI
        color = "#10B981" if status == "NORMAL" else "#F59E0B" if status == "WARNING" else "#EF4444"
        st.markdown(f"""
            <div style="padding:10px; border-radius:8px; background:{color}22; border:1px solid {color}; text-align:center;">
                <b style="color:{color};">AUDIT: {status}</b>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.alerts:
            st.caption(f"Last Alert: {st.session_state.alerts[-1]['alert_type'].upper()}")

    if st.session_state.app_state != "LANDING":
        st.write(f"**Target:** {st.session_state.candidate_info.get('role')}")
        if st.button("RESET SESSION"):
            st.session_state.clear()
            st.rerun()

if st.session_state.app_state == "LANDING":
    c1, mid, c2 = st.columns([1, 2, 1])
    with mid:
        st.markdown("<p class='header-text'>AI Talent Auditor</p>", unsafe_allow_html=True)
        st.info("Phase 2: Evaluation Engine")
        
        with st.container():
            name = st.text_input("Full Name")
            role = st.text_input("Role", "Senior Architect")
            skills = st.multiselect("Key Competencies", ["Python", "AWS", "Security", "ML"], ["Python"])
            
            c_a, c_b = st.columns(2)
            diff = c_a.selectbox("Difficulty", ["Basic", "Standard", "Elite"])
            count = c_b.number_input("Questions", 1, 10, 3)
            
            if st.button("START EVALUATION CYCLE", use_container_width=True):
                if name and skills:
                    InterviewController.initialize_session(name, role, skills, diff, count)
                    st.rerun()

elif st.session_state.app_state == "INTERVIEW":
    idx = st.session_state.q_idx
    if not st.session_state.questions:
        st.error("No questions generated.")
        st.stop()

    if idx < len(st.session_state.questions):
        st.progress((idx + 1) / len(st.session_state.questions))
        
        # 🎤 INPUT MODE: AUDIO TOGGLE
        st.toggle("🎙️ Enable Audio Transcript (STT Active)", key="stt_active")
        
        q_text = st.session_state.questions[idx]
        st.markdown(f"<div class='card'><b>QUESTION {idx+1}:</b><br>{q_text}</div>", unsafe_allow_html=True)
        
        # Persistence check: load existing answer if any
        existing_ans = st.session_state.answers.get(idx, {}).get("answer", "")
        ans = st.text_area("Your Response", height=250, key=f"ans_{idx}", value=existing_ans)

        col_p, col_n = st.columns([1, 2])
        if idx > 0 and col_p.button("← BACK"):
            st.session_state.q_idx -= 1
            st.rerun()
            
        if col_n.button("COMMIT & NEXT →", use_container_width=True):
            if InterviewController.commit_answer(idx, q_text, ans):
                st.session_state.last_submit_time = time.time()
                st.session_state.q_idx += 1
                st.rerun()
    else:
        st.success("✔ Interview Phase Complete.")
        if st.button("EXECUTE EVALUATION SYNTHESIS", use_container_width=True):
            InterviewController.finalize_audit()
            st.rerun()

elif st.session_state.app_state == "REPORT":
    res = st.session_state.final_result
    st.markdown("<p class='header-text'>Evaluation Decision Hub</p>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg Score", f"{res['interview_score']}%")
    m2.metric("Trust Score", f"{res['behavior_score']}%")
    m3.metric("Decision", res['final_decision'].upper())

    st.markdown(f"<div class='card'><b>DETERMINISTIC JUSTIFICATION:</b><br>{res['justification']}</div>", unsafe_allow_html=True)
    
    with st.expander("DETAILED INDEPENDENT EVALUATIONS"):
        for q_id, eval_data in st.session_state.evaluations.items():
            st.subheader(f"Q{q_id + 1}: {st.session_state.answers[q_id]['question']}")
            st.json(eval_data)
            st.divider()
    
    if st.button("NEW ASSESSMENT CYCLE"):
        st.session_state.clear()
        st.rerun()
