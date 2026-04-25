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

import requests

# 🛡️ ARCHITECT FIX: UI → API Gateway Bridge
API_BASE_URL = "http://localhost:8000/interview"

def call_api(endpoint, data=None, method="POST"):
    """
    Production-grade REST bridge to FastAPI backend.
    """
    try:
        url = f"{API_BASE_URL.replace('/interview', '')}/{endpoint}" if "/" not in endpoint else f"http://localhost:8000{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"📡 API Connection Error: {str(e)}")
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
    if "question_ids" not in st.session_state:
        st.session_state.question_ids = []
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
                skills_list = [s.strip() for s in skills.split(",")]

                api_res = call_api("/interview/start", {
                    "candidate_name": name,
                    "candidate_email": email,
                    "role": role,
                    "skills": skills_list,
                    "difficulty": diff,
                    "num_questions": count,
                    "experience": exp,
                    "interview_type": i_type,
                    "style": style
                })

                interview_id = api_res.get("interview_id") if api_res else None
                if interview_id:
                    st.session_state.active_interview_id = interview_id

                # Fetch questions from DB (the API stored them there)
                fetched_questions = []
                if interview_id:
                    for i in range(count):
                        q_res = call_api(f"/interview/{interview_id}/question/{i}", method="GET")
                        if q_res and not q_res.get("finished"):
                            fetched_questions.append({
                                "text": q_res["text"],
                                "db_id": q_res["question_id"]
                            })

                if fetched_questions:
                    st.session_state.questions     = [q["text"] for q in fetched_questions]
                    st.session_state.question_ids  = [q["db_id"] for q in fetched_questions]
                    log_event("session_start", f"Loaded {len(fetched_questions)} questions from DB for {name}")
                else:
                    # Fallback: generate locally if API unreachable
                    if ai_engine:
                        local_qs = ai_engine.generate_questions(
                            role=role, skills=skills, difficulty=diff,
                            count=count, experience=exp,
                            interview_type=i_type, style=style
                        )
                        st.session_state.questions = local_qs or [
                            f"Explain a key concept in {role} related to {skills} (Part {i+1})" for i in range(count)
                        ]
                    else:
                        st.session_state.questions = [
                            f"Explain a key concept in {role} related to {skills} (Part {i+1})" for i in range(count)
                        ]
                    st.session_state.question_ids = list(range(len(st.session_state.questions)))
                    log_event("session_start", f"API offline — questions generated locally for {name}")

                st.session_state.app_state = "INTERVIEW"
                st.rerun()
            except Exception as e:
                st.error(f"System Failure: {str(e)}")

    @staticmethod
    def commit_answer(idx, q_text, ans):
        if not ans or len(ans.strip()) < 10:
            st.warning("Response is too brief (minimum 10 characters).")
            return False

        # Submit to API with the real DB question_id if available
        interview_id  = st.session_state.get("active_interview_id")
        question_ids  = st.session_state.get("question_ids", [])
        db_question_id = question_ids[idx] if idx < len(question_ids) else idx + 1

        if interview_id:
            call_api(
                f"/interview/{interview_id}/submit-response",
                {"question_id": db_question_id, "answer_text": ans}
            )

        st.session_state.answers[idx] = {
            "question": q_text,
            "answer": ans,
            "timestamp": time.time()
        }
        log_event("answer_commit", f"Response committed for Q{idx+1}")
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
        interview_id = st.session_state.get("active_interview_id")

        info = st.session_state.candidate_info

        for q_id in range(total):
            phase_idx = min(q_id, len(phases) - 1)
            status_placeholder.markdown(f"#### {phases[phase_idx]} (Q{q_id+1}/{total})")

            data = st.session_state.answers.get(q_id)
            if data and data.get("answer") and ai_engine:
                # REAL per-question evaluation
                eval_res = ai_engine.evaluate_answer(
                    question=data["question"],
                    answer=data["answer"],
                    role=info.get("role", "Expert"),
                    skills=info.get("skills", [])
                )
                st.session_state.evaluations[q_id] = eval_res
            elif data and data.get("answer"):
                # Local heuristic fallback
                words = len(data["answer"].split())
                st.session_state.evaluations[q_id] = {
                    "score": min(10, max(2, words // 15)),
                    "strengths": ["Response provided"],
                    "weaknesses": ["AI evaluation unavailable — local scoring applied"],
                    "sentiment": {"confidence": min(100, words * 4), "clarity": 70}
                }

            progress_bar.progress((q_id + 1) / total)
            time.sleep(0.4)

        # Generate final summary report
        try:
            report_data = ai_engine.generate_final_result(
                st.session_state.evaluations, st.session_state.alerts
            )
            st.session_state.final_report = report_data
        except Exception as e:
            st.session_state.final_report = {
                "interview_score": 0, "behavior_score": 0, "final_aggregate_score": 0,
                "final_decision": "AUDIT ERROR", "justification": f"Synthesis failed: {str(e)}"
            }
        
        st.session_state.app_state = "REPORT"
        log_event("audit_finalize", "High-fidelity report generated.")
        st.rerun()

# --------------------------------------------------
# 2. 🎨 PRODUCTION-READY UI DESIGN
# --------------------------------------------------

init_state()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── ANIMATIONS ── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 5px rgba(79,70,229,0.2); }
        50% { box-shadow: 0 0 20px rgba(79,70,229,0.5); }
        100% { box-shadow: 0 0 5px rgba(79,70,229,0.2); }
    }
    .fade-in { animation: fadeIn 0.6s ease-out forwards; }

    /* ── GLASSMORPHISM CARD ── */
    .prof-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .prof-card:hover { 
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
    }

    /* ── QUESTION CARD ── */
    .question-card {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        color: white;
        position: relative;
        overflow: hidden;
        animation: pulseGlow 4s infinite ease-in-out;
    }
    .question-card::before {
        content: '';
        position: absolute; top: -50px; right: -50px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }

    /* ── PULSE INDICATOR ── */
    .pulse-dot {
        height: 8px; width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
        animation: pulseDot 2s infinite;
    }
    @keyframes pulseDot {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* ── SIDEBAR BRANDING ── */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, rgba(79,70,229,0.05) 0%, rgba(255,255,255,0) 100%);
    }

    /* ── BUTTONS ── */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: white !important; border-radius: 12px !important;
        padding: 0.8rem 2.2rem !important; border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        letter-spacing: 0.5px !important;
        filter: brightness(1.1);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. 🚀 WORKFLOW ROUTING
# --------------------------------------------------

with st.sidebar:
    st.markdown("<h2 style='color: #4f46e5; margin-bottom: 0;'>RecruitAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.8rem; margin-top: 0; font-weight: 600; letter-spacing: 1px;'>ELITE AUDITOR v3.0</p>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.app_state != "DASHBOARD":
        st.markdown("### 🛠 Audit Control")
        if st.button("🚪 ABORT SESSION", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if st.session_state.app_state == "DASHBOARD":
    engine_mode = "AI Core Active" if (ai_engine and ai_engine.model) else "Local Engine Active"
    st.markdown(
        f"<div class='fade-in'>"
        f"<h1 style='margin-bottom:0.3rem;'>Autonomous Interview System</h1>"
        f"<p class='header-text'><span class='pulse-dot'></span>{engine_mode} &nbsp;|&nbsp; Precision Audit v3.0</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
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
        st.markdown("### System Status")

        ai_ok  = ai_engine and ai_engine.model
        proc_ok = surveillance is not None
        stt_ok  = True  # Always available via browser

        def _pill(label, ok, local_label=None):
            if ok:
                return f"<span class='status-pill pill-online'>{label}: ONLINE</span>"
            elif local_label:
                return f"<span class='status-pill pill-local'>{label}: {local_label}</span>"
            else:
                return f"<span class='status-pill pill-offline'>{label}: OFFLINE</span>"

        st.markdown(
            f"<div style='display:flex;flex-direction:column;gap:10px;margin-bottom:1.5rem;'>"
            f"{_pill('AI Engine', ai_ok, 'LOCAL')}"
            f"{_pill('Proctoring', proc_ok, 'DISABLED')}"
            f"{_pill('Voice STT', stt_ok)}"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("#### Recent Activity")
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-5:]):
                st.markdown(
                    f"<div style='font-size:0.8rem;color:#64748b;margin-bottom:6px;'>"
                    f"<b>[{log['timestamp']}]</b> {log['message']}</div>",
                    unsafe_allow_html=True
                )
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
        <div class='question-card'>
            <div class='q-label'>Question {idx+1} of {len(st.session_state.questions)} &nbsp;&bull;&nbsp; {info['role']}</div>
            <h3>{q_text}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # ============================================================
        # 🎙️ BROWSER-NATIVE SPEECH-TO-TEXT (No API Key Required)
        # Uses Chrome's built-in SpeechRecognition engine — FREE & Fast
        # ============================================================
        
        # Bridge: a hidden text input that JavaScript will populate
        stt_bridge_key = f"stt_bridge_{idx}"
        if stt_bridge_key not in st.session_state:
            st.session_state[stt_bridge_key] = ""

        import streamlit.components.v1 as components

        stt_html = f"""
        <div style="font-family: 'Inter', sans-serif;">
            <button id="sttBtn_{idx}" onclick="toggleRecording_{idx}()" 
                style="
                    background: linear-gradient(135deg, #4f46e5, #7c3aed);
                    color: white;
                    border: none;
                    padding: 10px 24px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.2s;
                    box-shadow: 0 4px 12px rgba(79,70,229,0.3);
                ">
                🎤 START RECORDING
            </button>
            <div id="sttStatus_{idx}" style="margin-top:10px; font-size:13px; color:#64748b; min-height:20px;"></div>
            <div id="sttResult_{idx}" style="
                margin-top:10px; padding:12px; 
                background:#f8fafc; border:1px solid #e2e8f0; 
                border-radius:8px; font-size:14px; 
                color:#1e293b; min-height:40px; display:none;
            "></div>
            <button id="sttApply_{idx}" onclick="applyTranscript_{idx}()" style="
                display:none; margin-top:10px;
                background:#10b981; color:white; border:none;
                padding:8px 20px; border-radius:6px;
                font-size:13px; font-weight:600; cursor:pointer;
            ">✅ USE THIS TEXT</button>
        </div>

        <script>
        var recognition_{idx} = null;
        var isRecording_{idx} = false;
        var finalTranscript_{idx} = '';

        function toggleRecording_{idx}() {{
            if (isRecording_{idx}) {{
                stopRecording_{idx}();
            }} else {{
                startRecording_{idx}();
            }}
        }}

        function startRecording_{idx}() {{
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                document.getElementById('sttStatus_{idx}').innerHTML = 
                    '⚠️ Speech recognition not supported. Please use Chrome browser.';
                return;
            }}

            recognition_{idx} = new SpeechRecognition();
            recognition_{idx}.continuous = true;
            recognition_{idx}.interimResults = true;
            recognition_{idx}.lang = 'en-US';
            finalTranscript_{idx} = '';

            recognition_{idx}.onstart = function() {{
                isRecording_{idx} = true;
                var btn = document.getElementById('sttBtn_{idx}');
                btn.innerHTML = '⏹️ STOP RECORDING';
                btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                btn.style.boxShadow = '0 4px 12px rgba(239,68,68,0.4)';
                document.getElementById('sttStatus_{idx}').innerHTML = 
                    '<span style="color:#ef4444;">🔴 Recording... Speak now</span>';
                document.getElementById('sttResult_{idx}').style.display = 'none';
                document.getElementById('sttApply_{idx}').style.display = 'none';
            }};

            recognition_{idx}.onresult = function(event) {{
                var interimTranscript = '';
                for (var i = event.resultIndex; i < event.results.length; i++) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript_{idx} += event.results[i][0].transcript + ' ';
                    }} else {{
                        interimTranscript += event.results[i][0].transcript;
                    }}
                }}
                var display = finalTranscript_{idx} + 
                    '<span style="color:#94a3b8;">' + interimTranscript + '</span>';
                document.getElementById('sttResult_{idx}').innerHTML = display;
                document.getElementById('sttResult_{idx}').style.display = 'block';
            }};

            recognition_{idx}.onerror = function(event) {{
                document.getElementById('sttStatus_{idx}').innerHTML = 
                    '⚠️ Mic error: ' + event.error + '. Check browser mic permissions.';
                stopRecording_{idx}();
            }};

            recognition_{idx}.onend = function() {{
                if (isRecording_{idx}) {{
                    // Auto-restart for continuous recording
                    recognition_{idx}.start();
                }}
            }};

            recognition_{idx}.start();
        }}

        function stopRecording_{idx}() {{
            isRecording_{idx} = false;
            if (recognition_{idx}) recognition_{idx}.stop();
            var btn = document.getElementById('sttBtn_{idx}');
            btn.innerHTML = '🎤 START RECORDING';
            btn.style.background = 'linear-gradient(135deg, #4f46e5, #7c3aed)';
            btn.style.boxShadow = '0 4px 12px rgba(79,70,229,0.3)';
            
            if (finalTranscript_{idx}.trim()) {{
                document.getElementById('sttStatus_{idx}').innerHTML = 
                    '✅ Transcription complete! Click "USE THIS TEXT" to apply.';
                document.getElementById('sttApply_{idx}').style.display = 'inline-block';
            }} else {{
                document.getElementById('sttStatus_{idx}').innerHTML = 
                    '🔇 No speech detected. Try again.';
            }}
        }}

        function applyTranscript_{idx}() {{
            var text = finalTranscript_{idx}.trim();
            if (!text) return;
            
            // Write to the dedicated Python bridge input (identified by placeholder)
            var inputs = window.parent.document.querySelectorAll('input[type="text"]');
            var bridgeInput = null;
            for (var i = 0; i < inputs.length; i++) {{
                if (inputs[i].placeholder && inputs[i].placeholder.indexOf('transcript will appear') !== -1) {{
                    bridgeInput = inputs[i];
                    break;
                }}
            }}
            
            if (bridgeInput) {{
                var nativeSetter = Object.getOwnPropertyDescriptor(
                    window.parent.HTMLInputElement.prototype, 'value').set;
                nativeSetter.call(bridgeInput, text);
                bridgeInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                document.getElementById('sttStatus_{idx}').innerHTML = 
                    '🎯 Text ready! Click the "Apply Voice to Answer" button below.';
            }} else {{
                // Fallback: fill any visible textarea
                var textareas = window.parent.document.querySelectorAll('textarea');
                if (textareas.length > 0) {{
                    var nativeSetter2 = Object.getOwnPropertyDescriptor(
                        window.parent.HTMLTextAreaElement.prototype, 'value').set;
                    nativeSetter2.call(textareas[0], text);
                    textareas[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    document.getElementById('sttStatus_{idx}').innerHTML = 
                        '🎯 Text applied directly to answer box!';
                }}
            }}
        }}
        </script>
        """
        
        components.html(stt_html, height=200)

        # ============================================================
        # PYTHON BRIDGE: Read what JavaScript wrote into the bridge input
        # ============================================================
        bridge_val = st.text_input(
            "Voice transcript bridge (hidden)",
            key=stt_bridge_key,
            label_visibility="collapsed",
            placeholder="(transcript will appear here after recording)"
        )
        
        # If bridge has content, offer a clear 'Apply' action
        if bridge_val and bridge_val.strip():
            if st.button("🎯 Apply Voice to Answer", key=f"apply_stt_{idx}", use_container_width=False):
                st.session_state[f"ans_{idx}"] = bridge_val.strip()
                st.session_state[stt_bridge_key] = ""  # Clear bridge
                st.rerun()

        # 🛡️ UI SYNC FIX: Bind text_area directly to session state via key
        if f"ans_{idx}" not in st.session_state:
            st.session_state[f"ans_{idx}"] = st.session_state.answers.get(idx, {}).get("answer", "")
            
        ans = st.text_area("Final Technical Response", height=200, key=f"ans_{idx}")
        
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

if st.session_state.app_state == "REPORT":
    if "final_report" not in st.session_state:
        st.error("Report data missing. Please restart the audit.")
        if st.button("RESTART"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    report = st.session_state.final_report
    info   = st.session_state.candidate_info
    decision_color = {"SELECTED": "#16a34a", "REJECTED": "#dc2626"}.get(report.get('final_decision',''), "#ca8a04")

    # ── Header banner
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg,#4f46e5,#7c3aed);
        color:white; padding:2.5rem 3rem; border-radius:20px; margin-bottom:2rem;
        display:flex; align-items:center; justify-content:space-between;
    '>
        <div>
            <p style='margin:0;opacity:0.8;font-size:0.85rem;text-transform:uppercase;
                      letter-spacing:0.1em;'>Audit Certification</p>
            <h1 style='margin:0.3rem 0 0;color:white;font-size:2rem;'>{info.get('name','Candidate')}</h1>
            <p style='margin:0.3rem 0 0;opacity:0.75;font-size:0.95rem;'>{info.get('role','')} &bull; {info.get('experience','')}</p>
        </div>
        <div style='text-align:right;'>
            <div style='font-size:0.8rem;opacity:0.75;'>Final Decision</div>
            <div style='font-size:2.2rem;font-weight:800;'>{report.get('final_decision','N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Technical Score", f"{report.get('interview_score', 0)}%")
    m2.metric("Behavioral Score", f"{report.get('behavior_score', 0)}%")
    m3.metric("Final Aggregate", f"{report.get('final_aggregate_score', 0)}%")
    
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
