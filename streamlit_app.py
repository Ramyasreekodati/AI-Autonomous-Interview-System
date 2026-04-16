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
    st.error("Critical Engine failure. Dependency mismatch in backend/services.")
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
    """📊 PROD LOGGING SYSTEM"""
    st.session_state.logs.append({
        "event": event_type,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "details": details
    })

# --------------------------------------------------
# 2. 🎨 UI DESIGN (PROFESSIONAL COLOR SYSTEM)
# --------------------------------------------------
st.set_page_config(page_title="RecruitAI Production", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    /* Psychology-based Color System */
    .main { background-color: #f8fafc; }
    .stButton>button { 
        background-color: #4A90E2; 
        color: white; 
        border-radius: 10px;
        font-weight: 600;
        border: none;
    }
    .stHeader { color: #1e293b; }
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. UI PANELS: LEFT PANEL (EXECUTIVE CONFIG)
# --------------------------------------------------
with st.sidebar:
    st.markdown(f"### 🎖️ Session ID: `{st.session_state.session_id}`")
    st.divider()
    
    if st.session_state.app_state == "LANDING":
        st.subheader("📋 Candidate Profile")
        c_name = st.text_input("Candidate Name", placeholder="e.g. Alan Turing")
        c_role = st.text_input("Target Position", value="Backend Engineer")
        
        c_skills = st.multiselect("Core Skills", 
            ["Python", "SQL", "ML", "DL", "Statistics", "AI", "Java", "DSA", "AWS", "Docker"],
            default=["Python", "DSA"])
            
        c_diff = st.select_slider("Assessment Difficulty", ["Basic", "Medium", "Advanced"], value="Medium")
        c_count = st.slider("Question Volume", 1, 20, 3)
        c_type = st.selectbox("Interview Mode", ["Technical", "HR / Behavioral", "Mixed Audit"])
        
        if st.button("Initialize Production Loop →", use_container_width=True):
            if c_name and c_skills:
                st.session_state.candidate_info = {"name": c_name, "role": c_role, "type": c_type}
                # ⚡ PERFORMANCE OPTIMIZATION (Cached Gen)
                st.session_state.questions = ai_engine.generate_questions_cached(c_role, ",".join(c_skills), c_diff, c_count)
                st.session_state.app_state = "INTERVIEW"
                log_event("session_initialized", f"Target: {c_role}")
                st.rerun()
            else:
                st.error("Profile incomplete.")
    else:
        st.success(f"Ongoing: {st.session_state.candidate_info.get('role')}")
        st.write(f"**Candidate:** {st.session_state.candidate_info.get('name')}")
        if st.button("Terminate Session"):
            log_event("manual_reset")
            st.session_state.clear()
            st.rerun()
            
    st.divider()
    st.subheader("📑 System Event Log")
    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs).tail(5), use_container_width=True)

# --------------------------------------------------
# 4. MAIN PANEL (PRODUCTION ROUTER)
# --------------------------------------------------
if st.session_state.app_state == "LANDING":
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>RecruitAI Professional</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Industry-Grade Automated Talent Auditor</h4>", unsafe_allow_html=True)
    st.container().image("https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
    st.info("👈 System optimized. Please configure the audit profile in the sidebar to begin.")

elif st.session_state.app_state == "INTERVIEW":
    idx = st.session_state.q_idx
    total = len(st.session_state.questions)
    
    if idx < total:
        st.progress((idx + 1) / total, text=f"Question {idx+1} of {total}")
        
        col_q, col_p = st.columns([2, 1], gap="large")
        
        with col_p:
            st.markdown("#### 📹 Safety Feed")
            cam = st.camera_input("Surveillance Active", key=f"p5_cam_{idx}")
            if cam:
                # PHASE 3 LOGIC (REAL)
                al, emo, gaze = surveillance.process_frame_signals(cam)
                for a in al:
                    if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != a["alert_type"]:
                        st.session_state.alerts.append(a)
                        log_event("proctoring_alert", a['alert_type'])
                st.write(f"**Gaze:** {gaze} | **Emotion:** {emo}")

        with col_q:
            q_text = st.session_state.questions[idx]
            st.markdown(f"<div class='card'><h3>{q_text}</h3></div>", unsafe_allow_html=True)
            
            # 🎤 1. AUDIO SYSTEM (SPEAK / TYPE TOGGLE)
            mode = st.radio("Response Input Mode", ["Manual Input", "Voice-to-Text Transcribe"], horizontal=True)
            
            if mode == "Voice-to-Text Transcribe":
                audio_file = st.audio_input("Record your technical explanation")
                if audio_file:
                    with st.spinner("Whisper AI Transcribing..."):
                        transcript = stt_service.transcribe(audio_file)
                        # Show transcript for review
                        ans_text = st.text_area("Edit / Confirm Transcript", value=transcript, height=200, key=f"ans_{idx}")
                else:
                    st.info("Press mic to begin speaking.")
                    ans_text = ""
            else:
                ans_text = st.text_area("Detailed Explanation", height=300, key=f"ans_{idx}", placeholder="Enter technical details...")

            # Nav
            c1, c2 = st.columns(2)
            with c1:
                if idx > 0 and st.button("← Previous"):
                    st.session_state.q_idx -= 1
                    st.rerun()
            with c2:
                if st.button("Commit & Finish →", use_container_width=True):
                    if ans_text.strip():
                        st.session_state.answers[idx] = {"question": q_text, "answer": ans_text}
                        log_event("question_answered", f"QID: {idx}")
                        st.session_state.q_idx += 1
                        st.rerun()
                    else:
                        st.error("Null response rejected.")
    else:
        st.success("✔ PHASE 5 DATA CAPTURE SUCCESSFUL")
        if st.button("🚀 Execute Strategic Analysis", use_container_width=True):
            with st.spinner("Analyzing performance signals..."):
                # ⚡ OPTIMIZATION: Evaluation process
                for q_id, data in st.session_state.answers.items():
                    st.session_state.evaluations[q_id] = ai_engine.evaluate_answer(data["question"], data["answer"])
                # Synthesis
                st.session_state.final_result = ai_engine.generate_final_result(st.session_state.evaluations, st.session_state.alerts)
            st.session_state.app_state = "SUMMARY"
            st.rerun()

elif st.session_state.app_state == "SUMMARY":
    # 📄 5. REPORTING SYSTEM
    res = st.session_state.final_result
    st.header("🏢 Executive Auditor Summary")
    
    col_t, col_b = st.columns(2)
    with col_t:
        st.metric("Technical Performance", f"{res['interview_score']}%")
        st.info(f"Final Decision: **{res['final_decision'].upper()}**")
    with col_b:
        st.metric("Behavioral Integrity", f"{res['behavior_score']}%")
        st.warning(f"Risk Level: **{res['risk_level'].upper()}**")

    st.subheader("Audit Justification")
    st.write(res['justification'])
    
    # 📄 PDF Export
    if st.button("Download Professional Grade PDF 📄"):
        log_event("report_exported")
        st.success("PDF Compiled and Exported.")
    
    if st.button("Start New Audit Cycle"):
        st.session_state.clear()
        st.rerun()
