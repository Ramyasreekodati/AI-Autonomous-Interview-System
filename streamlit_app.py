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
    st.error("Engine failure. Please ensure backend services are functional.")
    st.stop()

st.set_page_config(page_title="RecruitAI - Phase 4 Intelligence", page_icon="🛡️", layout="wide")

# --------------------------------------------------
# 1. 💾 SESSION INITIALIZATION
# --------------------------------------------------
defaults = {
    "session_id": f"SES_{str(uuid.uuid4())[:8].upper()}",
    "current_phase": "SETUP",
    "questions": [],
    "answers": {},
    "evaluations": {},
    "alerts": [],
    "final_result": None,
    "q_idx": 0
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --------------------------------------------------
# 2. UI: PHASE 0 (SETUP)
# --------------------------------------------------
if st.session_state.current_phase == "SETUP":
    st.title("🚀 RecruitAI System Integration")
    with st.sidebar:
        st.subheader("Config")
        name = st.text_input("Candidate Name")
        role = st.text_input("Role", "Software Engineer")
        skills = st.text_input("Skills", "Python")
        count = st.number_input("Count", 1, 10, value=3)

    if st.button("Launch System Session →", use_container_width=True):
        if name and skills:
            st.session_state.candidate_name = name
            st.session_state.questions = ai_engine.generate_questions_cached(role, skills, "Medium", count)
            st.session_state.current_phase = "INTERVIEW"
            st.rerun()

# --------------------------------------------------
# 3. UI: PHASE 1 & 3 (CORE INTEGRATION)
# --------------------------------------------------
elif st.session_state.current_phase == "INTERVIEW":
    idx = st.session_state.q_idx
    total = len(st.session_state.questions)
    
    if idx < total:
        st.progress((idx + 1) / total)
        col_q, col_p = st.columns([2, 1])
        
        with col_p:
            st.markdown("#### 📹 Proctoring HUD")
            cam = st.camera_input("Surveillance Active", key=f"cam_{idx}")
            if cam:
                al, emo, gaze = surveillance.process_frame_signals(cam)
                for a in al:
                    if not st.session_state.alerts or st.session_state.alerts[-1]["alert_type"] != a["alert_type"]:
                        st.session_state.alerts.append(a)
                st.write(f"**Gaze:** {gaze} | **Emotion:** {emo}")

        with col_q:
            q_text = st.session_state.questions[idx]
            st.markdown(f"### {q_text}")
            ans = st.text_area("Your Response", height=250, key=f"ans_{idx}")
            if st.button("Confirm Response"):
                if ans.strip():
                    st.session_state.answers[idx] = {"question": q_text, "answer": ans}
                    st.session_state.q_idx += 1
                    st.rerun()
    else:
        st.success("✔ INTERVIEW COMPLETE")
        if st.button("🚀 Execute Phase 4 Synthesis", use_container_width=True):
            with st.spinner("Analyzing Technical & AI Behavioral Signals..."):
                # Phase 2: Evaluation
                for q_id, data in st.session_state.answers.items():
                    st.session_state.evaluations[q_id] = ai_engine.evaluate_answer(data["question"], data["answer"])
                # Phase 4: Synthesis
                st.session_state.final_result = ai_engine.generate_final_result(st.session_state.evaluations, st.session_state.alerts)
            st.session_state.current_phase = "SYNTHESIS"
            st.rerun()

# --------------------------------------------------
# 4. UI: PHASE 4 (CORE INTELLIGENCE)
# --------------------------------------------------
elif st.session_state.current_phase == "SYNTHESIS":
    res = st.session_state.final_result
    st.header("🛡️ Phase 4: Comprehensive Audit Intelligence")
    st.info("The synthesis engine has combined technical assessments and proctoring logs into a weighted decision.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Weighted Score", f"{round(res['interview_score']*0.7 + res['behavior_score']*0.3, 1)}%")
    col2.metric("Risk Assessment", res['risk_level'].upper())
    col3.metric("Final Decision", res['final_decision'].upper())

    st.divider()
    st.subheader("📦 Final Audit Output (STRICT JSON)")
    st.json(res)
    
    if st.button("Reset System"):
        st.session_state.clear()
        st.rerun()
