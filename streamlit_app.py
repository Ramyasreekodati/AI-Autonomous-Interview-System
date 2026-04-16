import streamlit as st
import sys
import os
import datetime
import time
import base64

# Add backend to path to import services
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

# --- SECURE IMPORT BLOCK ---
try:
    import models
    from database import SessionLocal, engine
    from services.surveillance import surveillance
    from services.scoring import scoring_service
    from services.llm import llm_service
    from services.reporting import reporting_service
except Exception as e:
    st.error(f"🚨 CRITICAL IMPORT ERROR: {e}")
    st.stop()

# --- DATABASE INITIALIZATION ---
import models
from database import engine, Base
Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

# --- APP CONFIG ---
st.set_page_config(
    page_title="AI Autonomous Interview System",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for Phase 5 Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    .main-card {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        color: #1e293b;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #4A90E2, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .stButton>button {
        border-radius: 12px;
        padding: 0.75rem 2rem;
        background: #4A90E2;
        color: white;
        border: none;
        transition: all 0.2s;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background: #357ABD;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'interview_id' not in st.session_state:
    st.session_state.interview_id = None
if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 0
if 'interview_data' not in st.session_state:
    st.session_state.interview_data = None
if 'page' not in st.session_state:
    st.session_state.page = 'Setup'

# --- MAIN NAV ---
with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 1.8rem;">RecruitAI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.page == 'Setup':
        st.subheader("📋 Campaign Config")
        cand_name = st.sidebar.text_input("Candidate Name", placeholder="John Doe")
        cand_email = st.sidebar.text_input("Work Email", placeholder="john@example.com")
        role = st.sidebar.selectbox("Target Role", ["Software Engineer", "Data Scientist", "Frontend Developer", "ML Engineer"])
        skills = st.sidebar.multiselect("Specializations", ["Python", "React", "SQL", "Java", "Deep Learning"], default=["Python"])
        difficulty = st.sidebar.select_slider("Difficulty", options=["Basic", "Medium", "Advanced"], value="Medium")
        num_q = st.sidebar.slider("Questions", 1, 20, 5)
        
        if st.sidebar.button("Launch Session 🚀", use_container_width=True):
            if not cand_name or not cand_email:
                st.sidebar.error("Fill basic details")
            else:
                db = get_db_session()
                # 1. Start Interview (Logic from interview.py)
                candidate = db.query(models.Candidate).filter(models.Candidate.email == cand_email).first()
                if not candidate:
                    candidate = models.Candidate(name=cand_name, email=cand_email)
                    db.add(candidate)
                    db.commit()
                    db.refresh(candidate)
                
                interview = models.Interview(candidate_id=candidate.id, status="ongoing")
                db.add(interview)
                db.commit()
                db.refresh(interview)
                
                # Pre-generate questions
                for i in range(num_q):
                    q_text = llm_service.generate_question(role=role, skills=skills, difficulty=difficulty)
                    question = models.Question(interview_id=interview.id, text=q_text, category=role, difficulty=difficulty)
                    db.add(question)
                db.commit()
                
                st.session_state.interview_id = interview.id
                st.session_state.page = 'Interview'
                db.close()
                st.rerun()

    else:
        st.info("Session in Progress")
        st.caption(f"ID: {st.session_state.interview_id}")
        if st.sidebar.button("End Session"):
            st.session_state.page = 'Setup'
            st.session_state.interview_id = None
            st.rerun()

# --- PAGES ---
if st.session_state.page == 'Setup':
    st.markdown("""
    <div style='text-align: center; padding-top: 5rem;'>
        <h1 style='font-size: 4rem; font-weight: 800; letter-spacing: -2px;'>AI Powered <span class='gradient-text'>Autonomous Interview</span></h1>
        <p style='color: #64748b; font-size: 1.2rem; max-width: 600px; margin: 0 auto 3rem;'>
            Experience industry-standard technical assessments with zero bias. 
            Configure your campaign in the sidebar to begin.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.image("https://img.icons8.com/clouds/200/000000/artificial-intelligence.png")
    with col2: st.image("https://img.icons8.com/clouds/200/000000/security-shield.png")
    with col3: st.image("https://img.icons8.com/clouds/200/000000/analytics.png")

elif st.session_state.page == 'Interview':
    db = get_db_session()
    questions = db.query(models.Question).filter(models.Question.interview_id == st.session_state.interview_id).all()
    
    if st.session_state.q_idx >= len(questions):
        st.session_state.page = 'Result'
        db.close()
        st.rerun()
        
    curr_q = questions[st.session_state.q_idx]
    
    # UI Layout
    col_main, col_side = st.columns([2.5, 1], gap="large")
    
    with col_main:
        st.markdown(f"<p style='color: #4A90E2; font-weight: 700; text-transform: uppercase; font-size: 0.8rem;'>Question {st.session_state.q_idx + 1} of {len(questions)}</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin-top: 0;'>{curr_q.text}</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Unique Answer Storage logic
        existing_res = db.query(models.Response).filter(
            models.Response.interview_id == st.session_state.interview_id,
            models.Response.question_id == curr_q.id
        ).first()
        
        ans = st.text_area("Your Response", key=f"ans_{curr_q.id}", height=300, value=existing_res.answer_text if existing_res else "")
        
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Previous") and st.session_state.q_idx > 0:
                st.session_state.q_idx -= 1
                st.rerun()
        with c2:
            if st.button("Submit & Next →"):
                if not ans.strip():
                    st.warning("Please provide an answer.")
                else:
                    # Phase 2 Evaluation
                    eval_data = scoring_service.evaluate_response(ans, curr_q.text)
                    if existing_res:
                        existing_res.answer_text = ans
                        existing_res.relevance_score = eval_data['score']
                    else:
                        resp = models.Response(
                            interview_id=st.session_state.interview_id,
                            question_id=curr_q.id,
                            answer_text=ans,
                            relevance_score=eval_data['score']
                        )
                        db.add(resp)
                    db.commit()
                    st.session_state.q_idx += 1
                    st.rerun()

    with col_side:
        st.markdown("<div class='main-card' style='padding: 1.5rem;'>", unsafe_allow_html=True)
        st.subheader("📷 AI Proctoring")
        cam = st.camera_input("Active monitoring", lab="Surveillance Feed")
        if cam:
            surveillance.process_frame(cam.getvalue(), st.session_state.interview_id, db)
        st.caption("Gaze and emotions tracked in real-time.")
        st.markdown("</div>", unsafe_allow_html=True)
    db.close()

elif st.session_state.page == 'Result':
    db = get_db_session()
    results = scoring_service.calculate_unified_score(st.session_state.interview_id, db)
    
    st.markdown("<h1 style='text-align: center;'>Assessment <span class='gradient-text'>Concluded</span></h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Technical Score", f"{results['interview_score']}/10")
    c2.metric("Behavior Score", f"{results['behavior_score']}%")
    c3.metric("Risk Level", results['risk_level'].upper())
    
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("AI Justification")
    st.info(results['justification'])
    
    if results['alerts']:
        st.warning(f"Integrity Alerts: {', '.join(results['alerts'])}")
    
    if st.button("Generate & Download Executive PDF Report", use_container_width=True):
        candidate = db.query(models.Candidate).join(models.Interview).filter(models.Interview.id == st.session_state.interview_id).first()
        file_path = reporting_service.generate_report(candidate.name, results)
        with open(file_path, "rb") as f:
            st.download_button("Download Report Ahora", f, file_name=os.path.basename(file_path))
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Return to Setup"):
        st.session_state.page = 'Setup'
        st.session_state.interview_id = None
        st.session_state.q_idx = 0
        st.rerun()
    db.close()
