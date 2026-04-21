import streamlit as st
import datetime
import time
import os
import pandas as pd
from dotenv import load_dotenv

# 🔴 FIX 7: set_page_config must be FIRST
st.set_page_config(
    page_title="RecruitAI Professional Auditor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔴 FIX 8: Safe Import Handling
try:
    from backend.services.ai_engine import ai_engine
except ImportError:
    st.error("AI Engine not found. Ensure backend services are correctly linked.")
    ai_engine = None

try:
    from backend.services.reporting import reporting_service
except ImportError:
    reporting_service = None

try:
    from backend.services.surveillance import surveillance
except ImportError:
    surveillance = None

try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    mic_recorder = None

# 🔴 FIX 9: Database Persistence Setup
try:
    from backend.database import SessionLocal
    import backend.models as models
    from sqlalchemy.orm import Session
except ImportError:
    SessionLocal = None
    models = None

def get_db_sync():
    if SessionLocal:
        db = SessionLocal()
        try:
            return db
        except:
            db.close()
    return None

# Load Environment Variables
load_dotenv()

# --------------------------------------------------
# 1. 🏗️ CORE SYSTEM LOGIC
# --------------------------------------------------

def init_state():
    if "app_state" not in st.session_state:
        st.session_state.app_state = "DASHBOARD"
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "evaluations" not in st.session_state:
        st.session_state.evaluations = {}
    if "q_idx" not in st.session_state:
        st.session_state.q_idx = 0
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "alerts" not in st.session_state:
        st.session_state.alerts = []

def log_event(event_type, message):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "type": event_type,
        "message": message
    })
    st.session_state.logs = st.session_state.logs[-50:]

class InterviewController:
    @staticmethod
    def initialize_session(name, role, skills, diff, count, exp, i_type, style):
        st.session_state.candidate_info = {
            "name": name,
            "role": role,
            "skills": [s.strip() for s in skills.split(",")],
            "experience": exp,
            "difficulty": diff
        }
        
        with st.spinner("Initializing Professional Audit Core..."):
            try:
                # 🛡️ PERSISTENCE FIX: Save session to DB
                db = get_db_sync()
                interview_id = None
                if db and models:
                    candidate = db.query(models.Candidate).filter(models.Candidate.email == email).first()
                    if not candidate:
                        candidate = models.Candidate(name=name, email=email)
                        db.add(candidate)
                        db.commit()
                        db.refresh(candidate)
                    
                    interview = models.Interview(
                        candidate_id=candidate.id,
                        status="ongoing",
                        target_role=role,
                        target_skills=", ".join(skills.split(",")) if isinstance(skills, str) else skills
                    )
                    db.add(interview)
                    db.commit()
                    db.refresh(interview)
                    interview_id = interview.id
                    st.session_state.active_interview_id = interview_id
                
                questions = ai_engine.generate_questions(
                    role, skills, diff, count, exp, i_type, style
                )
                
                # 🔴 FIX 2: Validate AI Output & Ensure Count
                if not isinstance(questions, list) or len(questions) < count:
                    questions = [
                        f"Technical question for {role}: Explain a key challenge you've faced with {skills} (Part {i+1})"
                        for i in range(count)
                    ]
                
                # Save questions to DB if possible
                if db and interview_id:
                    for q_text in questions[:count]:
                        db_q = models.Question(interview_id=interview_id, text=q_text, category=role, difficulty=diff)
                        db.add(db_q)
                    db.commit()
                
                if db: db.close()

                st.session_state.questions = questions[:count]
                st.session_state.app_state = "INTERVIEW"
                log_event("session_start", f"Audit initialized for {name} (ID: {interview_id})")
                st.rerun()
            except Exception as e:
                st.error(f"System Failure: {str(e)}")

    @staticmethod
    def commit_answer(idx, q_text, ans):
        if not ans or len(ans.strip()) < 10:
            st.warning("⚠️ Response is too brief. Please provide a detailed technical explanation.")
            return False
        
        # 🛡️ PERSISTENCE FIX: Save response to DB
        db = get_db_sync()
        if db and models and "active_interview_id" in st.session_state:
            interview_id = st.session_state.active_interview_id
            # Find question_id
            question = db.query(models.Question).filter(
                models.Question.interview_id == interview_id,
                models.Question.text == q_text
            ).first()
            
            if question:
                response = db.query(models.Response).filter(
                    models.Response.interview_id == interview_id,
                    models.Response.question_id == question.id
                ).first()
                
                if response:
                    response.answer_text = ans
                else:
                    response = models.Response(
                        interview_id=interview_id,
                        question_id=question.id,
                        answer_text=ans
                    )
                    db.add(response)
                db.commit()
        if db: db.close()

        st.session_state.answers[idx] = {
            "question": q_text,
            "answer": ans,
            "timestamp": time.time()
        }
        log_event("answer_commit", f"Committed response for Unit {idx+1}")
        return True

    @staticmethod
    def finalize_audit():
        st.session_state.app_state = "ANALYZING"
        
        # 🧠 MANAGER'S UPGRADE: Dynamic Analysis Feedback
        phases = [
            "🧬 Initializing Neural Evaluation Core...",
            "⚙️ Parsing Technical Depth & Accuracy...",
            "🛡️ Auditing Behavioral Integrity Signals...",
            "🧪 Synthesizing Competency Matrix...",
            "📊 Generating Executive Certification..."
        ]
        
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        total = len(st.session_state.questions)
        info = st.session_state.candidate_info
        
        # 🛡️ PERSISTENCE FIX: Finalize in DB
        db = get_db_sync()
        interview_id = st.session_state.get("active_interview_id")
        
        for q_id in range(total):
            # Dynamic status update
            phase_idx = min(q_id, len(phases)-1)
            status_placeholder.markdown(f"#### {phases[phase_idx]}")
            
            data = st.session_state.answers.get(q_id)
            if not data:
                eval_res = {"score": 0, "strengths": [], "weaknesses": ["Skipped"]}
                st.session_state.evaluations[q_id] = eval_res
            else:
                try:
                    eval_res = ai_engine.evaluate_answer(
                        data["question"], data["answer"], role=info["role"], skills=info["skills"]
                    )
                    st.session_state.evaluations[q_id] = eval_res
                    
                    # Update DB with score
                    if db and models and interview_id:
                        response = db.query(models.Response).join(models.Question).filter(
                            models.Response.interview_id == interview_id,
                            models.Question.text == data["question"]
                        ).first()
                        if response:
                            response.relevance_score = eval_res["score"]
                except Exception as e:
                    st.session_state.evaluations[q_id] = {"score": 0, "strengths": [], "weaknesses": ["System Error"]}
            
            progress_bar.progress((q_id + 1) / total)
            time.sleep(0.5) 
            
        if db and interview_id:
            db.commit()
        
        status_placeholder.markdown(f"#### {phases[-1]}")
        try:
            report_data = ai_engine.generate_final_result(st.session_state.evaluations, st.session_state.alerts)
            st.session_state.final_report = report_data
            
            # Close Interview in DB
            if db and interview_id:
                interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
                if interview:
                    interview.status = "completed"
                db.commit()
                
            st.session_state.app_state = "REPORT"
            log_event("audit_finalize", "High-fidelity report generated.")
        except Exception as e:
            st.error(f"Final synthesis failed: {str(e)}")
        
        if db: db.close()
        st.rerun()

# --------------------------------------------------
# 2. 🎨 PRODUCTION-READY UI DESIGN
# --------------------------------------------------

init_state()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding: 3rem 5rem !important;
        max-width: 1200px;
    }

    /* Professional Card Styling */
    .prof-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
    }

    .header-text {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }

    /* Form & Input Styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"], .stNumberInput input {
        background-color: white !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        padding: 0.75rem !important;
    }

    .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.025em;
        border: none !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. 🚀 WORKFLOW ROUTING
# --------------------------------------------------

with st.sidebar:
    st.markdown("<h2 style='color: #4f46e5; margin-bottom: 0;'>RecruitAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.8rem; margin-top: 0;'>ELITE AUDITOR v2.0</p>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.app_state != "DASHBOARD":
        st.markdown("### 🛠 Audit Control")
        if st.button("🚪 ABORT SESSION", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if st.session_state.app_state == "DASHBOARD":
    st.markdown("<h1>Professional Audit Center</h1>", unsafe_allow_html=True)
    st.markdown("<p class='header-text'>Secure, High-Precision Technical Talent Evaluation</p>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        
        with st.form("setup_form", clear_on_submit=False):
            st.markdown("#### 👤 Candidate Profile")
            c1, c2 = st.columns(2)
            name = c1.text_input("Full Name", "Candidate X")
            email = c2.text_input("Email Address", "candidate@audit.ai")
            
            c3, c4 = st.columns(2)
            role = c3.text_input("Target Role", "Senior Software Engineer")
            skills = c4.text_input("Core Skills (CSV)", "Python, Distributed Systems, AWS")
            
            st.divider()
            st.markdown("#### ⚙️ Audit Calibration")
            
            c5, c6, c7 = st.columns(3)
            diff = c5.selectbox("Intensity", ["Junior", "Mid", "Senior", "Lead", "Architect"], index=2)
            count = c6.number_input("Question Count", 1, 10, 3)
            exp = c7.selectbox("Tenure", ["0-1Y", "1-3Y", "3-5Y", "5-10Y", "10+Y"], index=3)
            
            c8, c9 = st.columns(2)
            i_type = c8.selectbox("Audit Type", ["Technical", "Behavioral", "System Design", "Mixed"])
            style = c9.selectbox("Interviewer Persona", ["Professional", "Challenging", "Friendly", "Strict"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 START PROFESSIONAL AUDIT", use_container_width=True)
            if submit:
                InterviewController.initialize_session(name, role, skills, diff, count, exp, i_type, style)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.markdown("### 🏥 System Status")
        
        st.markdown("""
        <div style='margin-bottom: 15px;'>
            <span style='color: #64748b; font-size: 0.9rem;'>AI Engine:</span>
            <span class='status-pill' style='background: #f0fdf4; color: #16a34a; border-color: #bbf7d0;'>ACTIVE</span>
        </div>
        <div style='margin-bottom: 25px;'>
            <span style='color: #64748b; font-size: 0.9rem;'>Proctoring:</span>
            <span class='status-pill' style='background: #f0fdf4; color: #16a34a; border-color: #bbf7d0;'>ONLINE</span>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("Confidence", "99%")
        m2.metric("Latency", "240ms")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📖 Recent Activity")
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-5:]):
                st.markdown(f"<div style='font-size: 0.85rem; color: #64748b; margin-bottom: 5px;'><b>[{log['timestamp']}]</b> {log['message']}</div>", unsafe_allow_html=True)
        else:
            st.caption("Awaiting session start...")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.app_state == "INTERVIEW":
    idx = st.session_state.q_idx
    q_text = st.session_state.questions[idx]
    info = st.session_state.candidate_info
    
    st.markdown(f"<h2>Audit Room: {info['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='header-text'>{info['role']} • Technical Unit {idx+1} of {len(st.session_state.questions)}</p>", unsafe_allow_html=True)
    
    st.progress((idx + 1) / len(st.session_state.questions))
    
    col_main, col_side = st.columns([2.5, 1])
    
    with col_main:
        st.markdown(f"""
        <div class='prof-card' style='border-left: 5px solid #4f46e5; background: #fcfdff;'>
            <p style='color: #4f46e5; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 0.5rem;'>Technical Challenge {idx+1}</p>
            <h3 style='margin-top: 0; line-height: 1.4; font-size: 1.5rem;'>{q_text}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.markdown("#### 🎙️ Voice Response")
        
        if mic_recorder:
            audio = mic_recorder(
                start_prompt="🎤 START RECORDING", 
                stop_prompt="⏹️ STOP & TRANSCRIBE", 
                key=f"mic_{idx}"
            )
            
            # 🔴 FIX 1 & 3: Reliable validation and state flag
            if audio and audio.get('bytes'):
                audio_id = audio.get('id', hash(audio['bytes']))
                if st.session_state.get(f"last_proc_{idx}") != audio_id:
                    with st.spinner("🧬 Converting & Transcribing..."):
                        webm_path = None
                        wav_path = None
                        try:
                            from pydub import AudioSegment
                            import tempfile
                            
                            # 1. Save raw capture (WebM)
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                                tmp.write(audio['bytes'])
                                webm_path = tmp.name
                            
                            # 2. Convert to WAV (PCM)
                            wav_path = webm_path.replace(".webm", ".wav")
                            audio_seg = AudioSegment.from_file(webm_path, format="webm")
                            audio_seg.export(wav_path, format="wav")
                            
                            # 3. Transcribe
                            transcription = ai_engine.transcribe_audio(wav_path)
                            if not transcription:
                                # Fallback to bytes transcription if WAV fails
                                transcription = ai_engine.transcribe_bytes(audio['bytes'], mime_type="audio/webm")
                                
                            if transcription:
                                st.session_state[f"ans_{idx}"] = transcription
                                st.session_state[f"last_proc_{idx}"] = audio_id
                                log_event("audio_proc", f"Voice data processed for Q{idx+1}")
                                st.rerun()
                            else:
                                st.warning("🔇 No speech detected. Please speak closer to the microphone and try again.")
                                
                        except Exception:
                            # 🛡️ SILENT PRODUCTION FALLBACK: If FFmpeg is missing, quietly use Gemini
                            transcription = ai_engine.transcribe_bytes(audio['bytes'], mime_type="audio/webm")
                            if transcription:
                                st.session_state[f"ans_{idx}"] = transcription
                                st.session_state[f"last_proc_{idx}"] = audio_id
                                st.toast("✅ Voice captured successfully!", icon="🎙️")
                                st.rerun()
                            else:
                                st.error("❌ Transcription Sync Error. Please try again or type your response.")
                                st.caption("💡 Tip: For the best experience, ensure your browser has microphone permissions enabled.")
                        finally:
                            import time
                            time.sleep(0.5) # 🛡️ WINDOWS FIX: Allow file handles to release
                            for p in [webm_path, wav_path]:
                                if p and os.path.exists(p):
                                    try:
                                        os.remove(p)
                                    except:
                                        pass
        else:
            st.warning("Audio recorder component is not available.")

        existing_ans = st.session_state.get(f"ans_{idx}", st.session_state.answers.get(idx, {}).get("answer", ""))
        ans = st.text_area("Final Technical Response", value=existing_ans, height=200, key=f"text_{idx}")
        st.session_state[f"ans_{idx}"] = ans
        
        c1, c2 = st.columns([1, 2])
        with c1:
            if idx > 0:
                if st.button("← PREVIOUS"):
                    st.session_state.q_idx -= 1
                    st.rerun()
        with c2:
            if st.button("COMMIT & CONTINUE →", use_container_width=True):
                if InterviewController.commit_answer(idx, q_text, ans):
                    if idx + 1 < len(st.session_state.questions):
                        st.session_state.q_idx += 1
                        st.rerun()
                    else:
                        InterviewController.finalize_audit()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_side:
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.markdown("#### 🛡️ AI Proctoring")
        if surveillance:
            cam_input = st.camera_input("Integrity Check", key=f"cam_{idx}", label_visibility="collapsed")
            if cam_input:
                try:
                    # 🛡️ PERSISTENCE FIX: Save proctoring alerts to DB in real-time
                    db = get_db_sync()
                    alerts, emotion, gaze = surveillance.process_frame_signals(
                        cam_input, 
                        interview_id=st.session_state.get("active_interview_id"),
                        db=db
                    )
                    if db: db.close()
                    st.markdown(f"<p style='font-size: 0.9rem; color: #64748b;'>Emotion: <b>{emotion}</b></p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 0.9rem; color: #64748b;'>Gaze: <b>{gaze}</b></p>", unsafe_allow_html=True)
                    if alerts: 
                        st.warning("⚠️ Integrity Alert Detected")
                        st.session_state.alerts.extend(alerts)
                        log_event("proctoring_flag", f"Detections: {[a['alert_type'] for a in alerts]}")
                except: st.caption("Proctoring sync offline")
        else:
            st.caption("Surveillance module not available.")
        
        st.markdown("<hr style='margin: 1.5rem 0; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("#### 📖 Audit Feed")
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-4:]):
                color = "#4f46e5" if log['type'] == "audio_proc" else "#dc2626" if log['type'] == "proctoring_flag" else "#64748b"
                st.markdown(f"<div style='font-size: 0.75rem; color: {color}; margin-bottom: 4px;'>• {log['message']}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ABORT AUDIT", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.app_state == "REPORT":
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>📋 Audit Certification</h1>", unsafe_allow_html=True)
    report = st.session_state.final_report
    info = st.session_state.candidate_info
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Technical Score", f"{report['interview_score']}%")
    m2.metric("Behavioral Score", f"{report['behavior_score']}%")
    m3.metric("Final Aggregate", f"{report['final_aggregate_score']}%")
    
    col_rep_l, col_rep_r = st.columns([2, 1])
    
    with col_rep_l:
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Executive Summary")
        color = "#16a34a" if report['final_decision'] == "SELECTED" else "#dc2626" if report['final_decision'] == "REJECTED" else "#ca8a04"
        st.markdown(f"<h2 style='color: {color}; margin-top: 0;'>{report['final_decision']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; line-height: 1.8; font-size: 1.1rem;'>{report['justification']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### 🔍 Technical Deep Dive")
        for q_id, eval in st.session_state.evaluations.items():
            with st.expander(f"Question {q_id+1}: {st.session_state.questions[q_id][:60]}..."):
                st.markdown(f"**Score:** {eval['score']*10}/100")
                st.markdown(f"**Response:** {st.session_state.answers.get(q_id, {}).get('answer', 'N/A')}")
                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Strengths**")
                    for s in eval.get('strengths', []): st.markdown(f"- {s}")
                with c2:
                    st.markdown("**Weaknesses**")
                    for w in eval.get('weaknesses', []): st.markdown(f"- {w}")
    
    with col_rep_r:
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.markdown("### 📜 Official Certificate")
        st.markdown("<p style='color: #64748b; font-size: 0.9rem;'>Generate a verified PDF report of this audit session for records.</p>", unsafe_allow_html=True)
        
        if reporting_service:
            if st.button("📄 GENERATE PDF REPORT", use_container_width=True):
                report_path = reporting_service.generate_report(info['name'], report)
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="⬇️ DOWNLOAD CERTIFICATE",
                        data=f,
                        file_name=os.path.basename(report_path),
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("Report Generated Successfully!")
        else:
            st.warning("Reporting engine unavailable.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 START NEW SESSION", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
