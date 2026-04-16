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
    import models
    from database import SessionLocal
    from services.surveillance import surveillance
    from services.scoring import scoring_service
    from services.llm import llm_service
    from services.reporting import reporting_service
except Exception as e:
    st.error(f"🚨 CRITICAL SYSTEM ERROR: {e}")
    st.stop()

# --- APP CONFIG ---
st.set_page_config(
    page_title="AI Autonomous Interview System",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for Premium Audit Compliance
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #fcfdfe; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #f1f5f9; padding: 2rem 1rem; }
    .main-card { background: white; padding: 3rem; border-radius: 32px; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01); }
    .gradient-text { background: linear-gradient(135deg, #4A90E2, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    .stButton>button { border-radius: 16px; padding: 0.8rem 2.5rem; background: #4A90E2; color: white; border: none; transition: all 0.2s; font-weight: 700; width: 100%; }
    .stButton>button:hover { background: #2563eb; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 1. SESSION INITIALIZATION
# --------------------------------------------------
if "app_state" not in st.session_state:
    st.session_state.app_state = "HOME"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {"name": "", "email": ""}

if "interview_id" not in st.session_state:
    st.session_state.interview_id = None

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 2rem;">RecruitAI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.app_state == "HOME":
        st.subheader("👤 Candidate Info")
        c_name = st.text_input("Name", placeholder="John Doe")
        c_email = st.text_input("Email", placeholder="john@example.com")
        
        st.subheader("⚙️ Configuration")
        role = st.text_input("Target Role", placeholder="Backend Engineer")
        skills = st.text_input("Skills", placeholder="Python, AWS, SQL")
        diff = st.selectbox("Difficulty", ["Basic", "Medium", "Advanced"], index=1)
        num_q = st.number_input("Questions", 1, 20, 5)

        # 2. LAUNCH SESSION & 4. STORE QUESTIONS CORRECTLY
        if st.button("Launch Session"):
            if not c_name or not c_email or not role or not skills:
                st.error("Please fill all configuration details.")
            else:
                with st.spinner("Generating AI Questions..."):
                    # Phase 1 Logic
                    st.session_state.candidate_info = {"name": c_name, "email": c_email}
                    db = SessionLocal()
                    from models import Candidate, Interview, Question as DBQuestion
                    cand = db.query(Candidate).filter(Candidate.email == c_email).first()
                    if not cand:
                        cand = Candidate(name=c_name, email=c_email)
                        db.add(cand); db.commit(); db.refresh(cand)
                    itv = Interview(candidate_id=cand.id, status="ongoing")
                    db.add(itv); db.commit(); db.refresh(itv)
                    st.session_state.interview_id = itv.id
                    
                    # 1. FIX generate_questions and 2. FIX PARSING
                    questions = llm_service.generate_question_set(role, [s.strip() for s in skills.split(",")], diff, num_q)
                    
                    # 3. ADD SAFETY VALIDATION (MANDATORY)
                    if not questions or questions is None:
                        st.error("Question generation failed")
                        st.stop()
                    
                    # 4. STORE QUESTIONS CORRECTLY
                    st.session_state.questions = questions
                    st.session_state.current_q = 0
                    st.session_state.answers = {}
                    st.session_state.app_state = "INTERVIEW"
                    
                    for qt in questions:
                        db.add(DBQuestion(interview_id=itv.id, text=qt))
                    db.commit(); db.close()
                    st.rerun()
    else:
        st.success(f"Session: {st.session_state.app_state}")
        # 6. DEBUG OUTPUT (IMPORTANT)
        st.write("DEBUG QUESTIONS:", st.session_state.questions)
        if st.button("Reset Session"):
            st.session_state.app_state = "HOME"
            st.rerun()

# --- CONDITIONAL UI ROUTING ---

def show_homepage():
    st.markdown("<h1 style='font-size: 5rem; font-weight: 800; line-height: 1; letter-spacing: -3px;'>Autonomous <span class='gradient-text'>Hiring.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.5rem; color: #64748b; margin: 2rem 0; max-width: 700px;'>Local, non-hallucinating AI assessments. Use the sidebar to configure.</p>", unsafe_allow_html=True)
    st.info("👈 Please start by entering candidate details in the left panel.")

def show_interview():
    if not st.session_state.questions:
        st.session_state.app_state = "HOME"
        st.rerun()
        return

    # 5. DISPLAY QUESTIONS SAFELY
    q = st.session_state.questions[st.session_state.current_q]
    if q is None:
        st.error("Invalid question detected")
        st.stop()

    st.progress((st.session_state.current_q + 1) / len(st.session_state.questions))
    st.write(f"{st.session_state.current_q + 1}. {q}")

    st.markdown(f"""
    <div class="main-card">
        <h2 style="margin-top: 0; font-size: 2rem; color: #1e293b;">{q}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    col_input, col_proctor = st.columns([2, 1], gap="large")
    
    with col_input:
        ans_key = f"answer_{st.session_state.current_q}"
        default_val = st.session_state.answers.get(st.session_state.current_q, "")
        ans_text = st.text_area("Your Response", height=300, key=ans_key, value=default_val)
        st.session_state.answers[st.session_state.current_q] = ans_text

        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.session_state.current_q > 0:
                if st.button("Previous"):
                    st.session_state.current_q -= 1
                    st.rerun()
        with col_nav2:
            if st.button("Next Question →"):
                if not ans_text.strip():
                    st.warning("Please provide a response.")
                else:
                    if st.session_state.current_q + 1 >= len(st.session_state.questions):
                        st.session_state.app_state = "COMPLETED"
                    else:
                        st.session_state.current_q += 1
                    st.rerun()

    with col_proctor:
        st.markdown("<div style='background: #0f172a; padding: 1.5rem; border-radius: 24px; color: white;'><p style='font-size: 10px; font-weight: 800; color: #94a3b8;'>LIVE SURVEILLANCE</p>", unsafe_allow_html=True)
        cam = st.camera_input("Feed active")
        if cam:
            db = SessionLocal()
            surveillance.process_frame(cam.getvalue(), st.session_state.interview_id, db)
            db.close()
        st.markdown("</div>", unsafe_allow_html=True)

def show_report():
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Audit <span class='gradient-text'>Analysis</span></h1>", unsafe_allow_html=True)
    db = SessionLocal()
    from models import Response as DBResponse, Question as DBQuestion
    db_questions = db.query(DBQuestion).filter(DBQuestion.interview_id == st.session_state.interview_id).all()
    for idx, ans in st.session_state.answers.items():
        q_db = db_questions[idx]
        eval_res = scoring_service.evaluate_response(ans, q_db.text)
        db.add(DBResponse(interview_id=st.session_state.interview_id, question_id=q_db.id, answer_text=ans, relevance_score=eval_res['score']))
    db.commit()
    results = scoring_service.calculate_unified_score(st.session_state.interview_id, db)
    db.close()
    c1, c2, c3 = st.columns(3)
    c1.metric("Tech Quality", f"{results['interview_score']}/10")
    c2.metric("Integrity", f"{results['behavior_score']}%")
    c3.metric("Risk Level", results['risk_level'].upper())
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Data-Driven Report")
    st.write(results['justification'])
    if st.button("Download PDF", use_container_width=True):
        path = reporting_service.generate_report(st.session_state.candidate_info['name'], results)
        with open(path, "rb") as f:
            st.download_button("Download Now", f, file_name=os.path.basename(path))
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Start New Evaluation"):
        st.session_state.app_state = "HOME"
        st.rerun()

# --- MAIN ROUTER ---
if st.session_state.app_state == "HOME":
    show_homepage()
elif st.session_state.app_state == "INTERVIEW":
    show_interview()
elif st.session_state.app_state == "COMPLETED":
    show_report()
