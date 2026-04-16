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

st.set_page_config(page_title="RecruitAI - Phase 3 Proctoring", page_icon="🤖", layout="wide")

# --------------------------------------------------
# 1. 💾 SESSION INITIALIZATION
# --------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = f"SES_{str(uuid.uuid4())[:8].upper()}"

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
    if clean_text.lower() in ["abc", "xyz", "qwerty", "asdf", "12345"]:
        return False
    return True

# --------------------------------------------------
# 3. UI: PHASE 0 (SETUP)
# --------------------------------------------------
if st.session_state.current_phase == "SETUP":
    st.title("🚀 AI Interview Room Setup")
    with st.sidebar:
        st.subheader("Candidate Info")
        name = st.text_input("Name")
        role = st.text_input("Role", "Software Engineer")
        skills = st.text_input("Skills", "Python, SQL")
        diff = st.selectbox("Difficulty", ["Basic", "Medium", "Advanced"], index=1)
        count = st.number_input("Question Count", 1, 10, value=3)

    if st.button("Launch Phase 1 & 3 Session →", use_container_width=True):
        if name and skills:
            st.session_state.questions = ai_engine.generate_questions_cached(role, skills, diff, count)
            st.session_state.current_phase = "INTERVIEW"
            st.rerun()
        else:
            st.error("Configuration incomplete.")

# --------------------------------------------------
# 4. UI: PHASE 1 & 3 (INTERVIEW + PROCTORING)
# --------------------------------------------------
elif st.session_state.current_phase == "INTERVIEW":
    idx = st.session_state.q_idx
    total = len(st.session_state.questions)
    
    if idx < total:
        st.progress((idx + 1) / total, text=f"Question {idx + 1} of {total}")
        
        # UI SPLIT: 2 Columns for Question vs Proctoring Feed
        col_q, col_proctor = st.columns([2, 1], gap="medium")
        
        with col_proctor:
            st.markdown("#### 📹 Surveillance Hub")
            # 📷 PHASE 3: WEBCAM INTEGRATION
            cam_data = st.camera_input("Proctoring Active", key=f"cam_{idx}")
            
            if cam_data:
                # 👤 PHASE 3: FACE DETECTION (REAL OPENCV)
                alert, face_count = surveillance.detect_face_violation(cam_data)
                
                # 🚨 PHASE 3: ALERT SYSTEM
                if alert:
                    if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != alert["alert_type"]:
                        st.session_state.alerts.append(alert)
                    st.toast(f"PROCTORING FLAG: {alert['alert_type']}", icon="🚨")
                else:
                    st.caption(f"Status: Secure (Faces: {face_count})")

        with col_q:
            q_text = st.session_state.questions[idx]
            st.markdown(f"### {q_text}")
            
            default_val = st.session_state.answers.get(idx, {}).get("answer", "")
            ans_input = st.text_area("Your Response", height=300, key=f"ans_{idx}", value=default_val)
            
            c1, c2 = st.columns(2)
            with c1:
                if idx > 0 and st.button("← Previous"):
                    st.session_state.q_idx -= 1
                    st.rerun()
            with c2:
                if st.button("Confirm & Next →", use_container_width=True):
                    if validate_answer(ans_input):
                        st.session_state.answers[idx] = {
                            "session_id": st.session_state.session_id,
                            "question_id": idx,
                            "question": q_text,
                            "answer": ans_input,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        st.session_state.q_idx += 1
                        st.rerun()
                    else:
                        st.error("Invalid response detected.")
    else:
        st.success("✔ PHASE 1 & 3 COMPLETE")
        if st.button("🚀 Execute Phase 2: Evaluation Engine", use_container_width=True):
            with st.spinner("Analyzing performance signals..."):
                for q_id, data in st.session_state.answers.items():
                    res = ai_engine.evaluate_answer(data["question"], data["answer"])
                    st.session_state.evaluations[q_id] = res
            st.session_state.current_phase = "EVALUATION"
            st.rerun()

# --------------------------------------------------
# 5. UI: PHASE 2 (EVALUATION STREAM)
# --------------------------------------------------
elif st.session_state.current_phase == "EVALUATION":
    st.header("🎯 Evaluation & Proctoring Logs")
    
    tab1, tab2 = st.tabs(["Technical Assessment", "Integrity Logs"])
    
    with tab1:
        for q_id, res in st.session_state.evaluations.items():
            st.json(res)
            
    with tab2:
        if st.session_state.alerts:
            st.error("⚠️ Behavioral Violations Detected")
            st.table(st.session_state.alerts)
        else:
            st.success("No proctoring alerts recorded.")
    
    if st.button("Reset All"):
        st.session_state.clear()
        st.rerun()
