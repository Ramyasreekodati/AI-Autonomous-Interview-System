import streamlit as st
import datetime
import os
import sys
import uuid
import pandas as pd

# --- SYSTEM SETUP & CORE SERVICE IMPORT ---
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
# 1. 🏗️ LOGIC LAYER: INTERVIEW CONTROLLER
# --------------------------------------------------
class InterviewController:
    """
    STRICT PRODUCTION CONTROLLER (v1.2.5)
    Separates System States from UI Rendering.
    """
    @staticmethod
    def initialize_session(name, role, skills, diff, count):
        # 📦 DATA ISOLATION
        st.session_state.candidate_info = {"name": name, "role": role, "start_time": datetime.datetime.now()}
        st.session_state.questions = ai_engine.generate_questions_cached(
            role, ",".join(skills), diff, count, st.session_state.session_id
        )
        st.session_state.app_state = "INTERVIEW"
        log_event("session_start", f"Role: {role} | Questions: {count}")

    @staticmethod
    def save_response(idx, question, answer):
        """Phase 1: Structured Answer Storage"""
        if not answer.strip() or len(answer.strip()) < 5:
            return False, "Response too short or empty."
        
        st.session_state.answers[idx] = {
            "session_id": st.session_state.session_id,
            "q": question,
            "a": answer,
            "ts": datetime.datetime.now().isoformat()
        }
        log_event("answer_saved", f"QID: {idx}")
        return True, ""

    @staticmethod
    def run_synthesis_engine():
        """Phase 2 & 4 Core Intelligence Flow"""
        log_event("synthesis_started")
        with st.spinner("Synthesizing multi-modal audit signals..."):
            # 1. Batch Evaluate (Phase 2)
            for q_id, data in st.session_state.answers.items():
                st.session_state.evaluations[q_id] = ai_engine.evaluate_answer(data["q"], data["a"])
            
            # 2. Score Synthesis (Phase 4)
            st.session_state.final_result = ai_engine.generate_final_result(
                st.session_state.evaluations, 
                st.session_state.alerts
            )
        st.session_state.app_state = "COMPLETED"
        log_event("synthesis_complete")

# --------------------------------------------------
# 2. 🛡️ DATA LAYER: STATE MANAGEMENT
# --------------------------------------------------
def init_stable_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"SES-{str(uuid.uuid4())[:8].upper()}"
        st.session_state.app_state = "LANDING"
        st.session_state.questions = []
        st.session_state.answers = {}
        st.session_state.evaluations = {}
        st.session_state.alerts = []
        st.session_state.logs = []
        st.session_state.q_idx = 0
        st.session_state.candidate_info = {}

def log_event(event, details=""):
    st.session_state.logs.append({
        "event": event,
        "ts": datetime.datetime.now().strftime("%H:%M:%S"),
        "details": details
    })

init_stable_state()

# --------------------------------------------------
# 3. 🎨 UI LAYER: PROFESSIONAL RENDERING
# --------------------------------------------------
st.set_page_config(page_title="RecruitAI - Final Production Build", layout="wide", page_icon="🛡️")

# Professional Styles
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { background-color: #4A90E2; color: white; border-radius: 8px; font-weight: 600; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #357ABD; border: none; }
    .card { background-color: white; padding: 2.5rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# SIDEBAR: SYSTEM AUDIT CONBOLE
with st.sidebar:
    st.title("🛡️ RecruitAI Pro v1.2.5")
    st.write(f"Session ID: `{st.session_state.session_id}`")
    st.divider()
    
    if st.session_state.app_state != "LANDING":
        st.success(f"Ongoing: {st.session_state.candidate_info.get('role', 'Candidate')}")
        if st.button("Manual Termination"):
            log_event("terminate_session")
            st.session_state.clear()
            st.rerun()
    st.divider()
    st.subheader("Event Tracker")
    if st.session_state.logs: st.dataframe(pd.DataFrame(st.session_state.logs).tail(10), use_container_width=True)

# MAIN ROUTER
if st.session_state.app_state == "LANDING":
    st.markdown("<h1 style='color: #4A90E2;'>Professional AI Talent Auditor</h1>", unsafe_allow_html=True)
    st.container().image("https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    
    with st.container(border=True):
        st.subheader("Audit Initialization")
        name = st.text_input("Candidate Name")
        c1, c2 = st.columns(2)
        role = c1.text_input("Target Role", "DevOps Engineer")
        diff = c2.selectbox("Complexity", ["Basic", "Medium", "Advanced"], index=1)
        skills = st.multiselect("Skill Focus", ["Python", "SQL", "ML", "AWS", "Java", "Docker"], ["Python"])
        count = st.slider("Question Count", 1, 15, 3)
        
        if st.button("Launch System →"):
            if name and skills:
                InterviewController.initialize_session(name, role, skills, diff, count)
                st.rerun()
            else: st.warning("Incomplete profile data.")

elif st.session_state.app_state == "INTERVIEW":
    # 🔁 NAVIGATION: Controlled via idx
    idx = st.session_state.q_idx
    if idx < len(st.session_state.questions):
        st.progress((idx + 1) / len(st.session_state.questions))
        
        col_q, col_p = st.columns([2, 1], gap="large")
        
        with col_p:
            st.markdown("#### 📹 Safety Feed")
            cam = st.camera_input("Safety Scanner", key=f"f5_cam_{idx}")
            if cam:
                al, emo, gaze = surveillance.process_frame_signals(cam)
                for a in al: 
                    if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != a["alert_type"]:
                        st.session_state.alerts.append(a)
                st.write(f"**Gaze:** {gaze} | **Emotion:** {emo}")

        with col_q:
            q_text = st.session_state.questions[idx]
            st.markdown(f"<div class='card'><h3>{q_text}</h3></div>", unsafe_allow_html=True)
            
            # STT / TEXT DUAL INPUT
            mode = st.radio("Input Selection", ["Keyboard", "Microphone"], horizontal=True)
            if mode == "Microphone":
                audio = st.audio_input("Record Response")
                ans_text = stt_service.transcribe(audio) if audio else ""
                ans_text = st.text_area("Edit / Verify Transcript", value=ans_text, key=f"ta_{idx}")
            else:
                ans_text = st.text_area("Enter Technical Response", height=300, key=f"ta_{idx}")

            if st.button("Submit & Progress →"):
                success, msg = InterviewController.save_response(idx, q_text, ans_text)
                if success:
                    st.session_state.q_idx += 1
                    st.rerun()
                else: st.error(msg)
    else:
        st.success("✔ PHASE 1 COMPLETE")
        if st.button("🚀 Execute Strategic Analysis"):
            InterviewController.run_synthesis_engine()
            st.rerun()

elif st.session_state.app_state == "COMPLETED":
    res = st.session_state.final_result
    st.header("📄 Consolidated Audit Report")
    
    # DASHBOARD
    m1, m2, m3 = st.columns(3)
    m1.metric("Tech Merit", f"{res['interview_score']}%")
    m2.metric("Integrity", f"{res['behavior_score']}%")
    m3.metric("Decision", res['final_decision'].upper())
    
    st.info(f"**Risk Profile:** {res['risk_level'].upper()} | **Justification:** {res['justification']}")
    st.divider()
    
    st.subheader("Final Forensic Payload (JSON)")
    st.json(res)
    
    if st.button("New Audit Cycle"):
        st.session_state.clear()
        st.rerun()
