import streamlit as st
import datetime
import os
import sys
import uuid

# --- SYSTEM SETUP ---
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from services.ai_engine import ai_engine
    from services.surveillance import surveillance
except ImportError:
    st.error("Engine missing. Ensure backend/services/ scripts are present.")
    st.stop()

st.set_page_config(page_title="RecruitAI - Full Phase 3", page_icon="🤖", layout="wide")

# --------------------------------------------------
# 1. 💾 SESSION INITIALIZATION
# --------------------------------------------------
if "session_id" not in st.session_state:
    st.session_id = f"SES_{str(uuid.uuid4())[:8].upper()}"

if "current_phase" not in st.session_state:
    st.session_state.current_phase = "SETUP"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {} 

if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0

# --------------------------------------------------
# 2. 🔁 LOGIC LAYER
# --------------------------------------------------
def validate_answer(text):
    clean_text = text.strip()
    if not clean_text or len(clean_text) < 5:
        return False
    if clean_text.lower() in ["abc", "xyz"]:
        return False
    return True

# --------------------------------------------------
# 3. UI: PHASE 0 (SETUP)
# --------------------------------------------------
if st.session_state.current_phase == "SETUP":
    st.title("🚀 Full Phase 3 Prototyping")
    with st.sidebar:
        st.subheader("Config")
        name = st.text_input("Candidate Name")
        role = st.text_input("Role", "Software Engineer")
        skills = st.text_input("Skills", "Python")
        count = st.number_input("Count", 1, 10, value=3)

    if st.button("Launch Full Proctoring Session →", use_container_width=True):
        if name and skills:
            st.session_state.questions = ai_engine.generate_questions_cached(role, skills, "Medium", count)
            st.session_state.current_phase = "INTERVIEW"
            st.rerun()

# --------------------------------------------------
# 4. UI: PHASE 1 & 3 (CORE INTEGRATION)
# --------------------------------------------------
elif st.session_state.current_phase == "INTERVIEW":
    idx = st.session_state.q_idx
    total = len(st.session_state.questions)
    
    if idx < total:
        st.progress((idx + 1) / total, text=f"Progress: {idx + 1}/{total}")
        
        col_q, col_proctor = st.columns([2, 1], gap="medium")
        
        with col_proctor:
            st.markdown("#### 📹 AI Integrity Lab")
            cam_data = st.camera_input("Surveillance Active", key=f"cam_{idx}")
            
            if cam_data:
                # 🧠 PHASE 3: FULL SIGNAL PROCESSING (Gaze, Emotion, Face)
                alerts, emotion, gaze = surveillance.process_frame_signals(cam_data)
                
                # 🚨 ALERTS SYSTEM
                for a in alerts:
                    if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != a["alert_type"]:
                        st.session_state.alerts.append(a)
                
                # 👀 PHASE 3: LIVE DASHBOARD
                st.write(f"**Gaze Monitoring:** {gaze}")
                st.write(f"**Emotion Insight:** {emotion}")
                
                if gaze == "Looking Away":
                    st.warning("Violation Detection: Gaze deviated from screen.")
                if emotion == "Stress":
                    st.info("Signal: Elevated stress detected.")

        with col_q:
            q_text = st.session_state.questions[idx]
            st.markdown(f"### {q_text}")
            
            ans_input = st.text_area("Your Response", height=300, key=f"ans_{idx}")
            
            c1, c2 = st.columns(2)
            with c1:
                if idx > 0 and st.button("← Back"):
                    st.session_state.q_idx -= 1
                    st.rerun()
            with c2:
                if st.button("Save & Next →", use_container_width=True):
                    if validate_answer(ans_input):
                        st.session_state.answers[idx] = {"question": q_text, "answer": ans_input}
                        st.session_state.q_idx += 1
                        st.rerun()
    else:
        st.success("✔ PHASE 3 CAPTURE COMPLETE")
        if st.button("Analyze Data"):
            st.session_state.current_phase = "REPORT"
            st.rerun()

elif st.session_state.current_phase == "REPORT":
    st.header("Phase 3: Final Integrations Log")
    st.subheader("Behavioral Audit Alerts")
    if st.session_state.alerts:
        st.table(st.session_state.alerts)
    else:
        st.success("No behavioral violations found.")
    
    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()
