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
    from services.auth import auth_service
    from services.surveillance import surveillance
    from services.scoring import scoring_service
    from services.llm import llm_service
    from services.reporting import reporting_service
except Exception as e:
    st.error(f"🚨 CRITICAL IMPORT ERROR: {e}")
    st.info("Check if your backend files are correctly structured or if there's a circular import.")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# --- RESOURCE CACHING ---
@st.cache_resource
def init_db():
    try:
        models.Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        return e

db_status = init_db()
if db_status is not True:
    st.error(f"Critical Database Error: {db_status}")
    st.stop()

# --- APP CONFIG ---
st.set_page_config(
    page_title="RecruitAI - Autonomous Interview System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
    }
    
    .stButton>button {
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 700;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1), 0 2px 4px -1px rgba(79, 70, 229, 0.06);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2), 0 4px 6px -2px rgba(79, 70, 229, 0.05);
        color: white;
    }
    
    .card {
        background: white;
        padding: 2rem;
        border-radius: 24px;
        border: 1px solid #eef2f8;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .sidebar-brand {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'Landing'
if 'interview_id' not in st.session_state:
    st.session_state.interview_id = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None

# --- DATABASE HELPERS ---
def get_db_session():
    return SessionLocal()

# --- PAGES ---

def landing_page():
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.write("")
        st.write("")
        st.markdown("<h1 style='font-size: 3.5rem; font-weight: 800; line-height: 1.1;'>Smarter Interviews with <span style='color: #4F46E5;'>RecruitAI</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.2rem; color: #64748b; margin: 1.5rem 0;'>Experience the future of talent acquisition. Our AI-driven platform monitors, evaluates, and reports on technical interviews in real-time.</p>", unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns([1, 2])
        with btn_col1:
            if st.button("Get Started", use_container_width=True):
                st.session_state.page = 'Login'
                st.rerun()
        
    with col2:
        st.image("https://img.freepik.com/free-vector/hiring-process-concept-illustration_114360-592.jpg", use_container_width=True)

def login_register_page():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Welcome Back")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            db = get_db_session()
            user = db.query(models.Candidate).filter(models.Candidate.email == email).first()
            if user and auth_service.verify_password(password, user.hashed_password):
                st.session_state.user = {"id": user.id, "name": user.name, "email": user.email}
                st.session_state.page = 'Dashboard'
                db.close()
                st.rerun()
            else:
                st.error("Invalid credentials")
            db.close()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Join RecruitAI")
        new_name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        if st.button("Register", use_container_width=True):
            db = get_db_session()
            existing = db.query(models.Candidate).filter(models.Candidate.email == new_email).first()
            if existing:
                st.error("Email already registered")
            else:
                hashed = auth_service.get_password_hash(new_password)
                user = models.Candidate(name=new_name, email=new_email, hashed_password=hashed)
                db.add(user)
                db.commit()
                st.success("Registration successful! Please login.")
            db.close()
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard_page():
    st.markdown(f"### Hello, {st.session_state.user['name']} 👋")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Your Interview Sessions")
    with col2:
        if st.button("Start New Interview ✨", use_container_width=True):
            db = get_db_session()
            new_interview = models.Interview(candidate_id=st.session_state.user['id'])
            db.add(new_interview)
            db.commit()
            db.refresh(new_interview)
            st.session_state.interview_id = new_interview.id
            st.session_state.page = 'Interview'
            db.close()
            st.rerun()
    
    db = get_db_session()
    interviews = db.query(models.Interview).filter(models.Interview.candidate_id == st.session_state.user['id']).all()
    
    if not interviews:
        st.info("No interviews yet. Click the button above to start your first session!")
    else:
        for itv in interviews:
            with st.expander(f"Session ID: {itv.id}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"Status: **{itv.status}**")
                if itv.status == 'Finished':
                    results = scoring_service.calculate_unified_score(itv.id, db)
                    c2.write(f"Score: **{results['total_score']}%**")
                    if c3.button("View Report 📄", key=f"view_{itv.id}"):
                        st.session_state.interview_id = itv.id
                        st.session_state.page = 'Report'
                        st.rerun()
                elif c2.button("Resume Interview ⏯️", key=f"resume_{itv.id}"):
                    st.session_state.interview_id = itv.id
                    st.session_state.page = 'Interview'
                    st.rerun()
    db.close()
    st.markdown('</div>', unsafe_allow_html=True)

def interview_page():
    db = get_db_session()
    
    # Progress check
    responses_count = db.query(models.Response).filter(models.Response.interview_id == st.session_state.interview_id).count()
    total_questions = 5 # Configuration
    
    if responses_count >= total_questions:
        itv = db.query(models.Interview).filter(models.Interview.id == st.session_state.interview_id).first()
        itv.status = 'Finished'
        db.commit()
        st.session_state.page = 'Report'
        db.close()
        st.rerun()

    st.markdown(f"#### Interview In Progress - ID: {st.session_state.interview_id}")
    st.progress(responses_count / total_questions)
    
    # Question Logic
    if st.session_state.current_question is None:
        with st.spinner("Generating next question..."):
            text = llm_service.generate_question()
            new_q = models.Question(interview_id=st.session_state.interview_id, text=text)
            db.add(new_q)
            db.commit()
            db.refresh(new_q)
            st.session_state.current_question = {"id": new_q.id, "text": new_q.text}

    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
        st.info("📷 AI Proctoring Feed (Active)")
        camera_photo = st.camera_input("Look at the camera while answering", key="cam_input")
        
        if camera_photo:
            with st.spinner("Analyzing feed..."):
                img_bytes = camera_photo.getvalue()
                surveillance.process_frame(img_bytes, st.session_state.interview_id, db)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
        st.write("---")
        st.markdown(f"### Q{responses_count + 1}: {st.session_state.current_question['text']}")
        st.write("---")
        
        user_answer = st.text_area("Your Response", height=250, placeholder="Type your answer here...")
        
        if st.button("Submit Response →", use_container_width=True):
            if not user_answer.strip():
                st.warning("Please provide an answer.")
            else:
                score, sentiment = scoring_service.evaluate_response(user_answer, st.session_state.current_question['text'])
                resp = models.Response(
                    interview_id=st.session_state.interview_id,
                    question_id=st.session_state.current_question['id'],
                    answer_text=user_answer,
                    relevance_score=score,
                    sentiment_score=sentiment
                )
                db.add(resp)
                db.commit()
                st.session_state.current_question = None
                db.close()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    db.close()

def report_page():
    db = get_db_session()
    itv_id = st.session_state.interview_id
    
    st.markdown("# 📊 Performance Report")
    results = scoring_service.calculate_unified_score(itv_id, db)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Overall Score", f"{results['total_score']}%")
    c2.metric("Risk Level", results['risk_level'], delta_color="inverse")
    c3.metric("Alerts Logged", results['alert_count'], delta="-1" if results['alert_count'] > 0 else "0", delta_color="inverse")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Score Breakdown")
        st.write(f"**Interview Performance:** {results['interview_score']}%")
        st.write(f"**Behavioral Integrity:** {results['behavior_score']}%")
        st.progress(results['total_score'] / 100)
        
        st.subheader("Integrity Alerts")
        alerts = db.query(models.Alert).filter(models.Alert.interview_id == itv_id).all()
        if not alerts:
            st.success("No proctoring violations detected. Exceptional integrity!")
        else:
            for a in alerts:
                st.error(f"🚨 {a.alert_type.replace('_', ' ').capitalize()} (Severity: {a.severity})")

    with col_right:
        st.subheader("Executive PDF Generation")
        if st.button("Generate & Download PDF Report", use_container_width=True):
            name = st.session_state.user['name']
            report_path = reporting_service.generate_report(name, results)
            with open(report_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="Download Report Now",
                data=pdf_bytes,
                file_name=f"RecruitAI_Report_{itv_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'Dashboard'
        st.session_state.interview_id = None
        st.rerun()
    db.close()

# --- MAIN NAVIGATION ---

st.sidebar.markdown('<p class="sidebar-brand">🤖 RecruitAI</p>', unsafe_allow_html=True)

if st.session_state.user:
    st.sidebar.write(f"Logged in as: **{st.session_state.user['name']}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.page = 'Landing'
        st.rerun()
else:
    if st.sidebar.button("Home", use_container_width=True):
        st.session_state.page = 'Landing'
        st.rerun()

# Router
if st.session_state.page == 'Landing':
    landing_page()
elif st.session_state.page == 'Login':
    login_register_page()
elif st.session_state.page == 'Dashboard':
    dashboard_page()
elif st.session_state.page == 'Interview':
    interview_page()
elif st.session_state.page == 'Report':
    report_page()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("System Status: Online 🟢")
st.sidebar.caption("Engine: V2.5.0-Release")
st.sidebar.caption("© 2026 Developed by Kodati Ramya Sree")
