import streamlit as st
import datetime
import os
import sys
import uuid
import pandas as pd

# --- SYSTEM SETUP ---
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from services.ai_engine import ai_engine
    from services.surveillance import surveillance
    from services.stt import stt_service
except ImportError:
    st.error("Engine failure. Please ensure backend services are functional.")
    st.stop()

# --------------------------------------------------
# 1. 🏗️ CLEAN ARCHITECTURE: DATA LAYER
# --------------------------------------------------
def init_session():
    defaults = {
        "session_id": f"RECRUIT-{str(uuid.uuid4())[:6].upper()}",
        "app_state": "LANDING",
        "questions": [],
        "answers": {},
        "evaluations": {},
        "alerts": [],
        "logs": [],
        "q_idx": 0,
        "candidate_info": {},
        "final_result": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

def log_event(event_type, details=""):
    st.session_state.logs.append({
        "event": event_type,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "details": details
    })

# --------------------------------------------------
# 2. 🎨 UI DESIGN
# --------------------------------------------------
st.set_page_config(page_title="RecruitAI - Stable v1.2.0", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stButton>button { background-color: #4A90E2; color: white; border-radius: 10px; font-weight: 600; }
    .card { background-color: white; padding: 2rem; border-radius: 15px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. UI PANELS: LEFT PANEL
# --------------------------------------------------
with st.sidebar:
    st.markdown(f"### 🎖️ Session ID: `{st.session_state.session_id}`")
    st.divider()
    
    if st.session_state.app_state == "LANDING":
        st.subheader("📋 Profile Setup")
        c_name = st.text_input("Candidate Name", placeholder="e.g. Marie Curie")
        c_role = st.text_input("Target Position", value="Lead Auditor")
        c_skills = st.multiselect("Core Skills", ["Python", "SQL", "ML", "Audit", "Governance"], default=["Python"])
        c_diff = st.select_slider("Difficulty", ["Basic", "Medium", "Advanced"], value="Medium")
        c_count = st.slider("Questions", 1, 10, 3)
        
        if st.button("Initialize Stable Session →", use_container_width=True):
            if c_name and c_skills:
                st.session_state.candidate_info = {"name": c_name, "role": c_role}
                # 🎯 DETERMINISTIC GEN: Passing session_id as seed
                st.session_state.questions = ai_engine.generate_questions_cached(
                    c_role, ",".join(c_skills), c_diff, c_count, st.session_state.session_id
                )
                st.session_state.app_state = "INTERVIEW"
                log_event("session_initialized", f"Seed: {st.session_state.session_id}")
                st.rerun()
    else:
        st.success(f"Ongoing: {st.session_state.candidate_info.get('role')}")
        if st.button("Reset / Restart"):
            st.session_state.clear()
            st.rerun()
            
    st.divider()
    st.subheader("📑 System Log")
    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs).tail(5), use_container_width=True)

# --------------------------------------------------
# 4. MAIN PANEL
# --------------------------------------------------
if st.session_state.app_state == "LANDING":
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>RecruitAI Stable</h1>", unsafe_allow_html=True)
    st.container().image("https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    st.info("👈 System deterministic and audit-compliant. Please initiate the session.")

elif st.session_state.app_state == "INTERVIEW":
    idx = st.session_state.q_idx
    total = len(st.session_state.questions)
    
    if idx < total:
        st.progress((idx + 1) / total, text=f"Question {idx+1}/{total}")
        col_q, col_p = st.columns([2, 1], gap="large")
        
        with col_p:
            st.markdown("#### 📹 Safety Feed")
            cam = st.camera_input("Safety Scan", key=f"p5_cam_{idx}")
            if cam:
                alerts, emotion, gaze = surveillance.process_frame_signals(cam)
                for a in alerts:
                    if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != a["alert_type"]:
                        st.session_state.alerts.append(a)
                        log_event("proctoring_alert", a['alert_type'])
                st.write(f"**Gaze:** {gaze} | **Emotion:** {emotion}")

        with col_q:
            q_text = st.session_state.questions[idx]
            st.markdown(f"<div class='card'><h3>{q_text}</h3></div>", unsafe_allow_html=True)
            
            mode = st.radio("Input Mode", ["Manual", "Voice"], horizontal=True)
            if mode == "Voice":
                audio = st.audio_input("Record Answer")
                ans_text = stt_service.transcribe(audio) if audio else ""
                ans_text = st.text_area("Review Transcript", value=ans_text, height=150)
            else:
                ans_text = st.text_area("Type Answer", height=250)

            if st.button("Save & Next →", use_container_width=True):
                if ans_text.strip():
                    st.session_state.answers[idx] = {"question": q_text, "answer": ans_text}
                    log_event("question_answered", f"QID: {idx}")
                    st.session_state.q_idx += 1
                    st.rerun()
    else:
        st.success("✔ INTERVIEW DATA CAPTURED")
        if st.button("🚀 Analyze Final Audit", use_container_width=True):
            for q_id, data in st.session_state.answers.items():
                st.session_state.evaluations[q_id] = ai_engine.evaluate_answer(data["question"], data["answer"])
            st.session_state.final_result = ai_engine.generate_final_result(st.session_state.evaluations, st.session_state.alerts)
            st.session_state.app_state = "REPORT"
            st.rerun()

elif st.session_state.app_state == "REPORT":
    res = st.session_state.final_result
    st.header("🏢 Executive Audit Summary")
    st.markdown("---")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Tech Score", f"{res['interview_score']}%")
    m2.metric("Integrity", f"{res['behavior_score']}%")
    m3.metric("Status", res['final_decision'].upper())

    st.subheader("Deterministic Justification")
    st.write(res['justification'])
    
    with st.expander("Structured JSON Payload"):
        st.json(res)
    
    if st.button("New Audit Cycle"):
        st.session_state.clear()
        st.rerun()
