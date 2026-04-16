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
except ImportError:
    st.error("Engine missing. Ensure ai_engine.py exists in backend/services/")
    st.stop()

st.set_page_config(page_title="RecruitAI - Phase 1 & 2 Core", page_icon="🤖", layout="wide")

# --------------------------------------------------
# 1. 💾 DATA STORAGE & SESSION ISOLATION
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

def save_phase1_data(idx, question, answer):
    st.session_state.answers[idx] = {
        "session_id": st.session_state.session_id,
        "question_id": idx,
        "question": question,
        "answer": answer,
        "timestamp": datetime.datetime.now().isoformat()
    }

# --------------------------------------------------
# 3. UI: PHASE 0 (SETUP)
# --------------------------------------------------
if st.session_state.current_phase == "SETUP":
    st.title("🚀 AI Interview System Setup")
    with st.sidebar:
        st.subheader("Candidate Info")
        name = st.text_input("Name")
        role = st.text_input("Role", "Software Engineer")
        skills = st.text_input("Skills", "Python, SQL")
        diff = st.selectbox("Difficulty", ["Basic", "Medium", "Advanced"], index=1)
        count = st.number_input("Question Count", 1, 10, value=3)

    if st.button("Launch Phase 1 Interview →", use_container_width=True):
        if name and skills:
            st.session_state.questions = ai_engine.generate_questions_cached(role, skills, diff, count)
            st.session_state.current_phase = "INTERVIEW"
            st.rerun()
        else:
            st.error("Please provide mandatory configuration.")

# --------------------------------------------------
# 4. UI: PHASE 1 (INTERVIEW ROOM)
# --------------------------------------------------
elif st.session_state.current_phase == "INTERVIEW":
    idx = st.session_state.q_idx
    total = len(st.session_state.questions)
    
    if idx < total:
        st.progress((idx + 1) / total, text=f"Question {idx + 1} of {total}")
        q_text = st.session_state.questions[idx]
        st.markdown(f"### {q_text}")
        
        default_val = st.session_state.answers.get(idx, {}).get("answer", "")
        ans_input = st.text_area("Your Response", height=250, key=f"ans_{idx}", value=default_val)
        
        c1, c2 = st.columns(2)
        with c1:
            if idx > 0 and st.button("← Previous"):
                st.session_state.q_idx -= 1
                st.rerun()
        with col2 := c2:
            if st.button("Confirm & Next →", use_container_width=True):
                if validate_answer(ans_input):
                    save_phase1_data(idx, q_text, ans_input)
                    st.session_state.q_idx += 1
                    st.rerun()
                else:
                    st.error("Invalid response detected.")
    else:
        st.success("✔ PHASE 1 COMPLETE")
        # 🔗 PHASE 2 TRANSITION
        if st.button("🚀 Execute Phase 2: Evaluation Engine", use_container_width=True):
            with st.spinner("Analyzing data signals..."):
                for q_id, data in st.session_state.answers.items():
                    res = ai_engine.evaluate_answer(data["question"], data["answer"])
                    st.session_state.evaluations[q_id] = res
            st.session_state.current_phase = "EVALUATION"
            st.rerun()

# --------------------------------------------------
# 5. UI: PHASE 2 (EVALUATION STREAM)
# --------------------------------------------------
elif st.session_state.current_phase == "EVALUATION":
    st.header("🎯 Phase 2: Intel Evaluation Summary")
    st.info("Technical assessments generated strictly from stored data signals.")
    
    # 📦 DISPLAY STRICT JSON (Audit verification)
    for q_id, res in st.session_state.evaluations.items():
        with st.expander(f"Question {q_id + 1} Assessment", expanded=True):
            st.json(res)
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
