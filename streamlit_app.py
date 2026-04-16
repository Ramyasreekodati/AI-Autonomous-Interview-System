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
st.set_page_config(page_title="RecruitAI - Phase-Based Core", page_icon="🤖", layout="wide")

# --------------------------------------------------
# SYSTEM STATE CONTROL (STRICT PHASE EXECUTION)
# --------------------------------------------------
if "app_state" not in st.session_state:
    st.session_state.app_state = "HOME"

# Phase 1 Data (Generation + Storage)
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# Phase 2 & 4 Data (Evaluation + Results)
if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}
if "final_results" not in st.session_state:
    st.session_state.final_results = None

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
                # Phase 1: Question Generation
                with st.spinner("Ph1: Generating questions..."):
                    skill_list = [s.strip() for s in skills.split(",")]
                    questions = ai_engine.generate_questions(role, skill_list, diff, count)
                    if not questions:
                        st.error("Engine failed.")
                        st.stop()
                    st.session_state.questions = questions
                    st.session_state.current_q = 0
                    st.session_state.answers = {}
                    st.session_state.app_state = "PHASE1_INTERVIEW"
                    st.rerun()
    else:
        st.success(f"Execution: {st.session_state.app_state}")
        st.write(f"Candidate: {st.session_state.candidate_info['name']}")
        if st.button("Reset Entire System"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# --- PHASE CONTROLLERS ---

def show_homepage():
    st.markdown("# RecruitAI: Autonomous Interview System")
    st.info("Configure the sidebar to trigger Phase 1 (Data Collection).")

def run_phase1_interview():
    # PHASE 1: Data Collection & Answer Storage
    curr_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    if curr_idx >= total:
        # Move to PHASE 2
        st.session_state.app_state = "PHASE2_EVALUATION"
        st.rerun()
        return

    st.progress((curr_idx + 1) / total)
    st.subheader(f"Phase 1: Interview Context ({curr_idx + 1}/{total})")
    
    q_text = st.session_state.questions[curr_idx]
    st.markdown(f"### {q_text}")
    
    ans_key = f"ans_{curr_idx}"
    default_ans = st.session_state.answers.get(curr_idx, "")
    answer = st.text_area("Your Response", height=200, key=ans_key, value=default_ans)
    
    # Store Answer (Phase 1 Isolation)
    if answer:
        st.session_state.answers[curr_idx] = answer
    
    col_nav1, col_nav2 = st.columns([1,1])
    with col_nav1:
        if curr_idx > 0 and st.button("← Back"):
            st.session_state.current_q -= 1
            st.rerun()
    with col_nav2:
        if st.button("Store & Next →"):
            if not answer.strip():
                st.warning("No data provided for storage.")
            else:
                st.session_state.current_q += 1
                st.rerun()

    # PHASE 3: (Future/Active) Proctoring
    with st.expander("🎥 Surveillance Hub", expanded=False):
        st.camera_input("Active Session Monitoring")

def run_phase2_evaluation():
    # PHASE 2: Evaluate Answers
    # PHASE 4: Combine Results
    st.header("Phase 2 & 4: Deep Analysis & Synthesis")
    st.write("The system is now processing stored data. No user input required.")
    
    progress_bar = st.progress(0)
    total = len(st.session_state.questions)
    
    evals = {}
    for i in range(total):
        q = st.session_state.questions[i]
        a = st.session_state.answers.get(i, "No response.")
        
        st.write(f"Analyzing Q{i+1}...")
        evals[i] = ai_engine.evaluate_answer(a, q)
        progress_bar.progress((i + 1) / total)
    
    st.session_state.evaluations = evals
    
    # PHASE 4: Combine Results (Synthetic Logic)
    avg_score = sum([e['score'] for e in evals.values()]) / total
    st.session_state.final_results = {
        "interview_score": round(avg_score, 1),
        "behavior_score": 100, # Mock
        "risk_level": "low" if avg_score > 6 else "medium",
        "justification": f"Candidate averaged {round(avg_score, 1)}/10 across technical assessment."
    }
    
    st.success("Analysis Complete.")
    if st.button("Generate Final Report"):
        st.session_state.app_state = "PHASE5_REPORT"
        st.rerun()

def run_phase5_report():
    # PHASE 5: UI + Reports
    st.header("Phase 5: Executive Assessment Report")
    
    results = st.session_state.final_results
    if not results:
        st.error("No data found to report.")
        st.stop()
        
    c1, c2, c3 = st.columns(3)
    c1.metric("Tech Quality", f"{results['interview_score']}/10")
    c2.metric("Behavior Integrity", f"{results['behavior_score']}%")
    c3.metric("Risk Status", results['risk_level'].upper())
    
    st.markdown("---")
    st.subheader("Automated Synthesis")
    st.write(results['justification'])
    
    # Report Generation (Independent of active UI logic, dependent ONLY on session_state data)
    if st.button("Export Standard PDF"):
        path = reporting_service.generate_report(st.session_state.candidate_info['name'], results)
        with open(path, "rb") as f:
            st.download_button("Download Now", f, file_name=os.path.basename(path))

# --- MAIN ROUTER ---
if st.session_state.app_state == "HOME":
    show_homepage()
elif st.session_state.app_state == "PHASE1_INTERVIEW":
    run_phase1_interview()
elif st.session_state.app_state == "PHASE2_EVALUATION":
    run_phase2_evaluation()
elif st.session_state.app_state == "PHASE5_REPORT":
    run_phase5_report()
