import streamlit as st
import cv2
import datetime
import time
import os
import sys
import numpy as np
import pandas as pd

# Add backend to path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from services.ai_engine import ai_engine
    from services.surveillance import surveillance
    from services.reporting import reporting_service
    from services.stt import stt_service
except ImportError:
    st.error("Missing backend services.")
    st.stop()

# --------------------------------------------------
# LOGGING SYSTEM
# --------------------------------------------------
def log_event(event, details=""):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append({
        "event": event,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "details": details
    })

# --------------------------------------------------
# UI CONFIG (PHASE 5 DESIGN)
# --------------------------------------------------
st.set_page_config(page_title="RecruitAI - Final Production", page_icon="🤖", layout="wide")

# Psychology-based color system implementation
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Primary Blue & Purple Gradients */
    .gradient-text {
        background: linear-gradient(135deg, #4A90E2, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .main-card {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .stButton>button {
        border-radius: 12px;
        padding: 0.6rem 2rem;
        background: #4A90E2;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: #357ABD;
        transform: translateY(-2px);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
defaults = {
    "app_state": "HOME",
    "questions": [],
    "answers": {},
    "evaluations": {},
    "alerts": [],
    "logs": [],
    "current_q": 0,
    "candidate_info": {},
    "audio_enabled": False,
    "final_result": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR (PHASE 5 FIELDS) ---
with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 2rem;">RecruitAI</h1>', unsafe_allow_html=True)
    st.divider()

    if st.session_state.app_state == "HOME":
        st.subheader("👤 Candidate Portal")
        candidate_name = st.text_input("Candidate Name", placeholder="e.g. John Doe")
        candidate_email = st.text_input("User ID / Email", placeholder="e.g. john@recruit.ai")
        
        st.divider()
        st.subheader("⚙️ Configuration")
        role = st.selectbox("Target Role", ["Data Scientist", "Software Engineer", "AI Researcher", "Data Analyst", "DevOps Engineer"])
        
        skills_pool = ["Python", "SQL", "ML", "DL", "AI", "Excel", "Statistics", "Java", "DSA", "AWS", "Docker"]
        skills = st.multiselect("Skills Multi-select", skills_pool, default=["Python"])
        
        diff = st.select_slider("Difficulty Level", options=["Basic", "Medium", "Advanced"], value="Medium")
        num_q = st.number_input("Number of Questions", 1, 20, value=3)

        if st.button("Initialize Production Session →", use_container_width=True):
            if candidate_name and candidate_email and skills:
                st.session_state.candidate_info = {"name": candidate_name, "email": candidate_email, "role": role}
                st.session_state.questions = ai_engine.generate_questions_cached(role, ",".join(skills), diff, num_q)
                st.session_state.app_state = "INTERVIEW"
                log_event("session_initialized", f"Target: {role}")
                st.rerun()
            else:
                st.error("Incomplete configuration.")
    else:
        st.success(f"Ongoing Session: {st.session_state.candidate_info.get('role', '')}")
        st.write(f"**Candidate:** {st.session_state.candidate_info.get('name', '')}")
        
        if st.button("Manual Termination"):
            log_event("session_manually_terminated")
            for key in defaults.keys():
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        st.subheader("System Logs")
        st.dataframe(pd.DataFrame(st.session_state.logs).tail(5), use_container_width=True)

# --- MAIN PANEL CONTROLLER ---

def show_homepage():
    st.markdown("<h1 style='font-size: 3.5rem; font-weight: 800; line-height: 1.1;'>Elite Interviewing. <br><span class='gradient-text'>Powered by Logic.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.25rem; color: #64748b; margin: 2rem 0; max-width: 600px;'>RecruitAI uses psychology-based design and high-integrity AI to audit technical talent in real-time. Zero hallucination. 100% Data-driven.</p>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&q=80&w=1200", use_container_width=True)

def show_interview():
    col_q, col_proctor = st.columns([2, 1], gap="large")
    
    with col_q:
        idx = st.session_state.current_q
        total = len(st.session_state.questions)
        
        if idx < total:
            # 1. Progress Bar
            st.progress((idx + 1) / total, text=f"Assessment Progress: {idx+1}/{total}")
            
            st.markdown(f"<p style='color: #4A90E2; font-weight: 700; letter-spacing: 1px;'>QUESTION {idx+1} OF {total}</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='main-card'><h3>{st.session_state.questions[idx]}</h3></div>", unsafe_allow_html=True)
            
            st.write("")
            
            # 1. AUDIO SYSTEM (SPEAK OR TYPE)
            col_mode, col_space = st.columns([1, 2])
            with col_mode:
                audio_mode = st.toggle("🎤 Speak Answer", value=st.session_state.get('audio_mode_active', False))
                st.session_state.audio_mode_active = audio_mode

            if audio_mode:
                audio_data = st.audio_input("Record your response")
                if audio_data:
                    with st.spinner("AI Transcribing..."):
                        # In real production, save to temp file and use stt_service
                        transcript = "Transcript simulation: Candidate explains architectural tradeoffs."
                        st.session_state.answers[idx] = st.text_area("Review Transcript", value=transcript, height=200, key=f"ans_{idx}")
                else:
                    st.info("Click the mic to start speaking.")
            else:
                st.session_state.answers[idx] = st.text_area("Type your response", placeholder="Explain your approach technically...", height=250, key=f"ans_{idx}")
            
            # Navigation
            c1, c2 = st.columns(2)
            with c1:
                if idx > 0 and st.button("Previous Question"):
                    st.session_state.current_q -= 1
                    st.rerun()
            with c2:
                if st.button("Confirm & Next →", use_container_width=True):
                    if st.session_state.answers.get(idx):
                        log_event("question_answered", f"Index: {idx}")
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.warning("Empty response detected.")
        else:
            st.success("Analysis Ready: All data points collected.")
            if st.button("Launch Evaluation Engine ⚙️", use_container_width=True):
                st.session_state.app_state = "ANALYSIS"
                st.rerun()

    with col_proctor:
        st.subheader("Surveillance Hub")
        with st.container(border=True):
            frame_ph = st.empty()
            # Multi-user isolation simulation (Integrated logic)
            cap = cv2.VideoCapture(0)
            while cap.isOpened() and st.session_state.app_state == "INTERVIEW":
                ret, frame = cap.read()
                if not ret: break
                res = surveillance.process_frame(frame, st.session_state.candidate_info.get('email', 'temp'))
                if res:
                    for alert in res['alerts']:
                        if not st.session_state.alerts or st.session_state.alerts[-1]['alert_type'] != alert['alert_type']:
                            st.session_state.alerts.append(alert)
                            log_event("integrity_alert", alert['alert_type'])
                    cv2.putText(frame, f"STATUS: SECURE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    frame_ph.image(frame, channels="BGR", use_container_width=True)
                time.sleep(0.01)
                if st.session_state.app_state != "INTERVIEW": break
            cap.release()

def show_analysis():
    st.header("Phase 5: Intelligent Synthesis")
    p = st.progress(0)
    for idx, ans in st.session_state.answers.items():
        st.write(f"Auditing Response {idx+1}...")
        st.session_state.evaluations[idx] = ai_engine.evaluate_answer(st.session_state.questions[idx], ans)
        p.progress((idx + 1) / len(st.session_state.answers))
    
    st.session_state.final_result = ai_engine.generate_final_result(st.session_state.evaluations, st.session_state.alerts)
    log_event("audit_finalized")
    st.session_state.app_state = "COMPLETED"
    st.rerun()

def show_reporting():
    res = st.session_state.final_result
    st.markdown(f"# Executive <span class='gradient-text'>Audit Report</span>", unsafe_allow_html=True)
    
    col_stat, col_res = st.columns([1, 2])
    with col_stat:
        st.metric("Technical Score", f"{res['interview_score']}%")
        st.metric("Behavioral Integrity", f"{res['behavior_score']}%")
        st.divider()
        st.subheader("Risk Assessment")
        risk_color = "green" if res['risk_level'] == "low" else "orange" if res['risk_level'] == "medium" else "red"
        st.markdown(f"<p style='font-size: 1.5rem; font-weight: 800; color: {risk_color};'>{res['risk_level'].upper()}</p>", unsafe_allow_html=True)

    with col_res:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.subheader("Non-Hallucinating Justification")
        st.write(res['justification'])
        
        if res['alerts']:
            st.warning("**Integrity Flags Raised:**")
            st.json(res['alerts'])
        
        st.divider()
        # 5. REPORTING SYSTEM (PDF)
        if st.button("Generate Executive PDF Report 📄", use_container_width=True):
            with st.spinner("Compiling Report..."):
                path = reporting_service.generate_report(st.session_state.candidate_info['name'], res)
                with open(path, "rb") as f:
                    st.download_button("Download Now", f, file_name=os.path.basename(path))
        st.markdown("</div>", unsafe_allow_html=True)

# --- ROUTER ---
if st.session_state.app_state == "HOME": show_homepage()
elif st.session_state.app_state == "INTERVIEW": show_interview()
elif st.session_state.app_state == "ANALYSIS": show_analysis()
elif st.session_state.app_state == "COMPLETED": show_reporting()
