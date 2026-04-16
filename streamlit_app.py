import streamlit as st
import sys
import os
import datetime
import time

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
    st.error(f"🚨 CRITICAL SYSTEM ERROR: {e}")
    st.stop()

# --- DATABASE INITIALIZATION ---
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

# Custom CSS for Phase 1-5 Final Production
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #fcfdfe;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f5f9;
        padding: 2rem 1rem;
    }
    
    .main-card {
        background: white;
        padding: 3rem;
        border-radius: 32px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #4A90E2, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .stButton>button {
        border-radius: 16px;
        padding: 0.8rem 2.5rem;
        background: #4A90E2;
        color: white;
        border: none;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 700;
        width: 100%;
    }
    
    .stButton>button:hover {
        background: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION INITIALIZATION
# --------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {"name": "", "email": ""}
if "interview_id" not in st.session_state:
    st.session_state.interview_id = None
if "status" not in st.session_state:
    st.session_state.status = "Setup"

# --- SIDEBAR (LEFT PANEL) ---
with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 2rem;">RecruitAI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state.started:
        st.subheader("👤 Candidate Info")
        cl_name = st.text_input("Full Name", placeholder="e.g. John Doe")
        cl_email = st.text_input("Work Email", placeholder="e.g. john@company.com")
        
        st.markdown("---")
        st.subheader("⚙️ Interview Config")
        role = st.text_input("Target Role", placeholder="e.g. Frontend Engineer")
        skills = st.text_input("Core Skills", placeholder="React, CSS, TypeScript")
        diff = st.selectbox("Difficulty Level", ["Basic", "Medium", "Advanced"], index=1)
        num_q = st.number_input("Number of Questions", 1, 20, 5)

        if st.button("Launch Session"):
            if not cl_name or not cl_email or not role or not skills:
                st.error("Missing mandatory configuration.")
            else:
                with st.spinner("Synthesizing Interview Environment..."):
                    st.session_state.candidate_info = {"name": cl_name, "email": cl_email}
                    db = get_db_session()
                    
                    # 1. Register Candidate
                    cand = db.query(models.Candidate).filter(models.Candidate.email == cl_email).first()
                    if not cand:
                        cand = models.Candidate(name=cl_name, email=cl_email)
                        db.add(cand)
                        db.commit()
                        db.refresh(cand)
                    
                    # 2. Start Interview Session
                    itv = models.Interview(candidate_id=cand.id, status="ongoing")
                    db.add(itv)
                    db.commit()
                    db.refresh(itv)
                    st.session_state.interview_id = itv.id
                    
                    # 3. Phase 1: Question Generation
                    q_list = llm_service.generate_question_set(role, [s.strip() for s in skills.split(",")], diff, num_q)
                    
                    # Persist questions to DB for Phase 4 summary
                    for q_text in q_list:
                        new_q = models.Question(interview_id=itv.id, text=q_text)
                        db.add(new_q)
                    db.commit()
                    db.close()
                    
                    st.session_state.questions = q_list
                    st.session_state.started = True
                    st.session_state.current_q = 0
                    st.session_state.answers = {}
                    st.session_state.scores = {}
                    st.session_state.status = "Interview"
                    st.rerun()
    else:
        st.success("Session Active")
        st.write(f"**Candidate:** {st.session_state.candidate_info['name']}")
        st.write(f"**Session ID:** `{st.session_state.interview_id}`")
        if st.button("Terminate Session"):
            st.session_state.started = False
            st.session_state.status = "Setup"
            st.rerun()

# --- PAGES ---

def show_homepage():
    st.markdown("<h1 style='font-size: 5rem; font-weight: 800; line-height: 1; letter-spacing: -3px;'>Autonomous <span class='gradient-text'>Hiring.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.5rem; color: #64748b; margin: 2rem 0; max-width: 700px;'>RecruitAI is a localized, non-hallucinating interview system. Use the sidebar to configure the candidate's technical profile.</p>", unsafe_allow_html=True)
    st.info("👈 Complete the configuration in the left panel to trigger the AI question generator.")

def show_interview():
    db = get_db_session()
    # Map questions to their DB IDs for storage
    db_questions = db.query(models.Question).filter(models.Question.interview_id == st.session_state.interview_id).all()
    
    if st.session_state.current_q >= len(st.session_state.questions):
        st.session_state.status = "Result"
        db.close()
        st.rerun()
        return

    q_text = st.session_state.questions[st.session_state.current_q]
    curr_q_db = db_questions[st.session_state.current_q]
    
    st.progress((st.session_state.current_q + 1) / len(st.session_state.questions))
    st.markdown(f"**Question {st.session_state.current_q + 1} of {len(st.session_state.questions)}**")

    st.markdown(f"""
    <div class="main-card">
        <h2 style="margin-top: 0; font-size: 2rem; color: #1e293b;">{q_text}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    
    col_input, col_proctor = st.columns([2, 1], gap="large")
    
    with col_input:
        ans_key = f"answer_{st.session_state.current_q}"
        ans_text = st.text_area("Your Response", height=300, key=ans_key)
        
        # Phase 2: Show instant score if navigating back
        if st.session_state.current_q in st.session_state.scores:
            st.info(f"Previous AI Score: {st.session_state.scores[st.session_state.current_q]}/10")

        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.session_state.current_q > 0:
                if st.button("← Previous"):
                    st.session_state.current_q -= 1
                    st.rerun()
                    
        with col_nav2:
            if st.button("Submit & Next →"):
                if not ans_text.strip():
                    st.warning("Please provide a technical explanation.")
                else:
                    with st.spinner("AI evaluating response..."):
                        # Phase 2: Evaluation Engine
                        eval_res = scoring_service.evaluate_response(ans_text, q_text)
                        
                        # Store in session
                        st.session_state.answers[st.session_state.current_q] = ans_text
                        st.session_state.scores[st.session_state.current_q] = eval_res['score']
                        
                        # Phase 1: Unique Answer Storage (Sync to DB)
                        existing_res = db.query(models.Response).filter(
                            models.Response.interview_id == st.session_state.interview_id,
                            models.Response.question_id == curr_q_db.id
                        ).first()
                        
                        if existing_res:
                            existing_res.answer_text = ans_text
                            existing_res.relevance_score = eval_res['score']
                        else:
                            db_res = models.Response(
                                interview_id=st.session_state.interview_id,
                                question_id=curr_q_db.id,
                                answer_text=ans_text,
                                relevance_score=eval_res['score']
                            )
                            db.add(db_res)
                        db.commit()
                        
                        st.success(f"Analysed. Score: {eval_res['score']}/10")
                        if eval_res['missing_concepts']:
                            st.caption(f"Tip: Focus more on {', '.join(eval_res['missing_concepts'])}")
                        
                        time.sleep(1)
                        st.session_state.current_q += 1
                        st.rerun()

    with col_proctor:
        st.markdown("<div style='background: #0f172a; padding: 1.5rem; border-radius: 24px; color: white;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 10px; font-weight: 800; color: #94a3b8;'>LIVE SURVEILLANCE</p>", unsafe_allow_html=True)
        cam = st.camera_input("Monitoring feed active")
        if cam:
            # Phase 3: AI Proctoring
            res = surveillance.process_frame(cam.getvalue(), st.session_state.interview_id, db)
            st.markdown(f"**Gaze:** `{res.get('gaze', 'Center')}`")
            st.markdown(f"**Emotion:** `{res.get('emotion', 'Neutral')}`")
            if res.get('alerts'):
                st.toast(f"Alert: {res['alerts'][0]['alert_type']}", icon="⚠️")
        st.markdown("</div>", unsafe_allow_html=True)
    db.close()

def show_result():
    db = get_db_session()
    # Phase 4: System Integration (Unified Scoring)
    results = scoring_service.calculate_unified_score(st.session_state.interview_id, db)
    
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Session <span class='gradient-text'>Analysis</span></h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Tech Quality", f"{results['interview_score']}/10")
    c2.metric("Integrity", f"{results['behavior_score']}%")
    c3.metric("Risk Level", results['risk_level'].upper())
    
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Executive AI Justification")
    st.info(results['justification'])
    
    if results['alerts']:
        st.write("---")
        st.subheader("Logged Integrity Alerts")
        for alert in results['alerts']:
            st.error(f"🚩 {alert.replace('_', ' ').capitalize()}")
            
    # Phase 5: Production Reporting
    if st.button("Generate Executive PDF Report", use_container_width=True):
        path = reporting_service.generate_report(st.session_state.candidate_info['name'], results)
        with open(path, "rb") as f:
            st.download_button("Download Report Now", f, file_name=os.path.basename(path))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("New Audit Session"):
        st.session_state.started = False
        st.session_state.status = "Setup"
        st.rerun()
    db.close()

# --- MAIN ROUTER ---
if not st.session_state.started:
    show_homepage()
else:
    if st.session_state.status == "Result":
        show_result()
    else:
        show_interview()
