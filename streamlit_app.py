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

# Custom CSS for Phase 1-3 Fix & Premium Audit Compliance
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

    .status-badge {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        background: #f1f5f9;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'interview_id' not in st.session_state:
    st.session_state.interview_id = None
if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 0
if 'page' not in st.session_state:
    st.session_state.page = 'Setup'
if 'candidate_info' not in st.session_state:
    st.session_state.candidate_info = {"name": "", "email": ""}

# --- SIDEBAR (LEFT PANEL REDESIGN) ---
with st.sidebar:
    st.markdown('<h1 class="gradient-text" style="font-size: 2rem; margin-bottom: 2rem;">RecruitAI</h1>', unsafe_allow_html=True)
    
    if st.session_state.page == 'Setup':
        st.markdown("<p class='status-badge'>System Configuration</p>", unsafe_allow_html=True)
        st.subheader("👤 Candidate Info")
        c_name = st.text_input("Full Name", placeholder="e.g. John Doe", key="in_name")
        c_email = st.text_input("Work Email", placeholder="e.g. john@company.com", key="in_email")
        
        st.markdown("---")
        st.subheader("⚙️ Interview Config")
        role = st.text_input("Target Role", placeholder="e.g. Backend Engineer, UI Architect")
        preset_skills = ["Python", "React", "SQL", "ML", "FastAPI"]
        selected_presets = st.multiselect("Select Core Skills", preset_skills)
        custom_skills = st.text_input("Add Custom Skills (comma separated)", placeholder="e.g. GraphQL, AWS, Docker")
        all_skills = list(set(selected_presets + [s.strip() for s in custom_skills.split(",") if s.strip()]))
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            difficulty = st.selectbox("Difficulty", ["Basic", "Medium", "Advanced"], index=1)
        with col_c2:
            num_q = st.number_input("Questions", 1, 20, 5)
            
        itv_type = st.selectbox("Interview Type", ["Technical", "HR", "Mixed"])
        st.markdown("---")
        st.subheader("🛠️ Features")
        audio_toggle = st.toggle("Audio Input Mode", value=False)
        timer_toggle = st.toggle("Enable Session Timer", value=True)

        if st.button("Launch Session", use_container_width=True):
            if not c_name or not c_email or not role or not all_skills:
                st.error("Please provide name, email, role, and at least one skill.")
            else:
                with st.spinner("Initializing AI Session..."):
                    st.session_state.candidate_info = {"name": c_name, "email": c_email}
                    db = get_db_session()
                    candidate = db.query(models.Candidate).filter(models.Candidate.email == c_email).first()
                    if not candidate:
                        candidate = models.Candidate(name=c_name, email=c_email)
                        db.add(candidate)
                        db.commit()
                        db.refresh(candidate)
                    
                    interview = models.Interview(candidate_id=candidate.id, status="ongoing")
                    db.add(interview)
                    db.commit()
                    db.refresh(interview)
                    
                    for _ in range(num_q):
                        q_text = llm_service.generate_question(role=role, skills=all_skills, difficulty=difficulty, type=itv_type)
                        question = models.Question(interview_id=interview.id, text=q_text, category=role, difficulty=difficulty)
                        db.add(question)
                    db.commit()
                    
                    st.session_state.interview_id = interview.id
                    st.session_state.page = 'Interview'
                    st.session_state.q_idx = 0
                    db.close()
                    st.rerun()
    else:
        st.markdown("<p class='status-badge' style='background: #dcfce7; color: #166534;'>Active Evaluation</p>", unsafe_allow_html=True)
        st.markdown(f"**Candidate:** {st.session_state.candidate_info['name']}")
        st.markdown(f"**Session ID:** `{st.session_state.interview_id}`")
        if st.button("Terminate Session"):
            st.session_state.page = 'Setup'
            st.session_state.interview_id = None
            st.rerun()

# --- MAIN PANEL ---
if st.session_state.page == 'Setup':
    st.write("")
    st.write("")
    st.markdown("<h1 style='font-size: 5rem; font-weight: 800; line-height: 1; letter-spacing: -3px;'>Autonomous <span class='gradient-text'>Hiring.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.5rem; color: #64748b; margin: 2rem 0; max-width: 700px;'>RecruitAI is a localized, non-hallucinating interview system designed for high-integrity technical assessments.</p>", unsafe_allow_html=True)

elif st.session_state.page == 'Interview':
    db = get_db_session()
    questions = db.query(models.Question).filter(models.Question.interview_id == st.session_state.interview_id).all()
    
    if st.session_state.q_idx >= len(questions):
        st.session_state.page = 'Result'
        db.close()
        st.rerun()
        
    curr_q = questions[st.session_state.q_idx]
    st.progress((st.session_state.q_idx + 1) / len(questions))
    st.markdown(f"<p style='color: #64748b; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.1rem; text-transform: uppercase;'>Question {st.session_state.q_idx + 1} of {len(questions)}</p>", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="main-card"><h2 style="margin-top: 0; font-size: 2rem; color: #1e293b; line-height: 1.2;">{curr_q.text}</h2></div>""", unsafe_allow_html=True)
    st.write("")
    
    col_input, col_proctor = st.columns([2, 1], gap="large")
    with col_input:
        existing_res = db.query(models.Response).filter(models.Response.interview_id == st.session_state.interview_id, models.Response.question_id == curr_q.id).first()
        ans_text = st.text_area("Your Detailed Response", height=300, value=existing_res.answer_text if existing_res else "", placeholder="Explain your answer with technical examples...")
        
        if existing_res and existing_res.relevance_score > 0:
            with st.expander("📝 Previous AI Evaluation"):
                st.write(f"**Score:** {existing_res.relevance_score}/10")
                st.caption("Detailed feedback will be available in the final executive report.")

        c_nav1, c_nav2 = st.columns([1, 1])
        with c_nav1:
            if st.button("Previous Question") and st.session_state.q_idx > 0:
                st.session_state.q_idx -= 1
                st.rerun()
        with c_nav2:
            if st.button("Submit & Next →"):
                if not ans_text.strip():
                    st.warning("Assessment requires an answer to proceed.")
                else:
                    with st.spinner("AI evaluating response..."):
                        eval_res = scoring_service.evaluate_response(ans_text, curr_q.text)
                        if existing_res:
                            existing_res.answer_text = ans_text
                            existing_res.relevance_score = eval_res['score']
                        else:
                            db_res = models.Response(interview_id=st.session_state.interview_id, question_id=curr_q.id, answer_text=ans_text, relevance_score=eval_res['score'])
                            db.add(db_res)
                        db.commit()
                        st.success(f"Response analyzed. AI Score: {eval_res['score']}/10")
                        if eval_res['missing_concepts']:
                            st.info(f"Insight: Consider covering {', '.join(eval_res['missing_concepts'])} for a higher score.")
                        time.sleep(1.5)
                        st.session_state.q_idx += 1
                        st.rerun()

    with col_proctor:
        st.markdown("<div style='background: #0f172a; padding: 1.5rem; border-radius: 24px; color: white;'><p style='font-size: 10px; font-weight: 800; color: #94a3b8;'>LIVE SURVEILLANCE</p>", unsafe_allow_html=True)
        cam_feed = st.camera_input("Maintain focus on the screen")
        if cam_feed:
            with st.spinner("Analyzing Feed..."):
                proc_data = surveillance.process_frame(cam_feed.getvalue(), st.session_state.interview_id, db)
                st.markdown(f"**Gaze:** `{proc_data.get('gaze', 'N/A')}`")
                st.markdown(f"**Emotion:** `{proc_data.get('emotion', 'N/A')}`")
                if proc_data.get('alerts'):
                    for alert in proc_data['alerts']:
                        st.toast(f"🚨 {alert['alert_type'].replace('_', ' ').capitalize()}", icon="🚩")
                        st.error(f"Violation: {alert['alert_type'].replace('_', ' ')}")
                else:
                    st.success("Integrity Verified ✅")
        st.caption("Gaze and emotions tracked in real-time.")
        st.markdown("</div>", unsafe_allow_html=True)
    db.close()

elif st.session_state.page == 'Result':
    db = get_db_session()
    results = scoring_service.calculate_unified_score(st.session_state.interview_id, db)
    st.markdown("<h1 style='font-size: 4rem; text-align: center; margin-bottom: 2rem;'>Session <span class='gradient-text'>Audit</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Tech Accuracy", f"{results['interview_score']}/10")
    c2.metric("Behavior Score", f"{results['behavior_score']}%")
    c3.metric("Final Risk", results['risk_level'].upper())
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Data-Driven Justification")
    st.write(results['justification'])
    if results['alerts']:
        st.write("---")
        st.subheader("Integrity Alerts")
        for alert in results['alerts']:
            st.error(f"🚩 {alert.replace('_', ' ').capitalize()}")
    if st.button("Generate Executive Report (PDF)", use_container_width=True):
        candidate_name = st.session_state.candidate_info['name']
        pdf_path = reporting_service.generate_report(candidate_name, results)
        with open(pdf_path, "rb") as f:
            st.download_button("Download Report Ahora", f, file_name=os.path.basename(pdf_path))
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Start New Audit"):
        st.session_state.page = 'Setup'
        st.session_state.interview_id = None
        st.rerun()
    db.close()
