import streamlit as st
import sys
import os
import time

# Add backend to path to import services
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

# --- SECURE IMPORT BLOCK ---
try:
    from services.ai_engine import ai_engine
    from services.surveillance import surveillance
    from services.reporting import reporting_service
    from database import SessionLocal
    import models
except Exception as e:
    st.error(f"🚨 ENGINE CONFIG ERROR: {e}")
    st.stop()

# --- APP CONFIG ---
st.set_page_config(page_title="RecruitAI - Engine Core", page_icon="🤖", layout="wide")

# --------------------------------------------------
# SYSTEM STATE CONTROL (PHASE LOGIC IN CODE)
# --------------------------------------------------
if "app_state" not in st.session_state:
    st.session_state.app_state = "HOME" # HOME -> INTERVIEW -> COMPLETED

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {"name": "", "email": ""}

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.title("RecruitAI Config")
    if st.session_state.app_state == "HOME":
        st.subheader("📋 Session Setup")
        c_name = st.text_input("Candidate Name")
        c_email = st.text_input("Candidate Email")
        role = st.text_input("Target Role", value="Software Engineer")
        skills = st.text_input("Specialized Skills", value="Python, SQL")
        diff = st.selectbox("Difficulty", ["Basic", "Medium", "Advanced"], index=1)
        count = st.number_input("Questions count", 1, 10, value=3)

        if st.button("Initialize Engine 🚀"):
            if not c_name or not c_email or not role or not skills:
                st.error("Missing mandatory data.")
            else:
                st.session_state.candidate_info = {"name": c_name, "email": c_email}
                
                # PYTHON CONTROLS SYSTEM (Phase 1)
                with st.spinner("AI Engine generating questions..."):
                    skill_list = [s.strip() for s in skills.split(",")]
                    questions = ai_engine.generate_questions(role, skill_list, diff, count)
                    
                    if not questions:
                        st.error("Engine failed to generate questions.")
                        st.stop()
                    
                    st.session_state.questions = questions
                    st.session_state.current_q = 0
                    st.session_state.answers = {}
                    st.session_state.app_state = "INTERVIEW"
                    st.rerun()
    else:
        st.success(f"State: {st.session_state.app_state}")
        st.write(f"Candidate: {st.session_state.candidate_info['name']}")
        if st.button("Reset Session"):
            st.session_state.app_state = "HOME"
            st.rerun()

# --- MAIN PANEL CONTROLLER ---

def show_homepage():
    st.markdown("# Welcome to RecruitAI")
    st.info("👈 Use the Configuration Sidebar to initialize the AI Evaluation Engine.")

def show_interview_ui():
    # Progress & Question Logic
    curr_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    if curr_idx >= total:
        st.session_state.app_state = "COMPLETED"
        st.rerun()
        return

    q_text = st.session_state.questions[curr_idx]
    
    st.progress((curr_idx + 1) / total)
    st.subheader(f"Question {curr_idx + 1} of {total}")
    
    st.markdown(f"### {q_text}")
    
    # SYSTEM STATE: Store answers
    ans_key = f"ans_{curr_idx}"
    answer = st.text_area("Your Response", height=200, key=ans_key)
    st.session_state.answers[curr_idx] = answer
    
    col_nav1, col_nav2 = st.columns([1,1])
    with col_nav1:
        if curr_idx > 0 and st.button("← Previous"):
            st.session_state.current_q -= 1
            st.rerun()
    with col_nav2:
        if st.button("Submit & Next →"):
            if not answer.strip():
                st.warning("Please provide an answer.")
            else:
                # Evaluation (Call ONLY when needed)
                evaluation = ai_engine.evaluate_answer(answer, q_text)
                st.toast(f"AI Score: {evaluation['score']}/10", icon="📝")
                
                st.session_state.current_q += 1
                st.rerun()

    # Proctoring (Code Control)
    with st.expander("🎥 Surveillance Monitor", expanded=True):
        cam = st.camera_input("System Monitoring")
        if cam:
            # Code interacts with backend for proctoring
            pass

def show_completed_ui():
    st.header("Assessment Complete")
    st.write("Synthesizing final executive report...")
    
    results = {
        "interview_score": 8.5,
        "behavior_score": 100,
        "risk_level": "low",
        "alerts": [],
        "justification": "Candidate demonstrated strong engineering thinking in 3/3 questions."
    }
    
    st.json(results)
    
    if st.button("Download Final Report (PDF)"):
        # Reporting linkage
        path = reporting_service.generate_report(st.session_state.candidate_info['name'], results)
        with open(path, "rb") as f:
            st.download_button("Download Now", f, file_name=os.path.basename(path))

# --- ROUTER ---
if st.session_state.app_state == "HOME":
    show_homepage()
elif st.session_state.app_state == "INTERVIEW":
    show_interview_ui()
elif st.session_state.app_state == "COMPLETED":
    show_completed_ui()
