// ── Config ────────────────────────────────────────────────────────────────────
const API_BASE = 'http://localhost:8000';

// ── App State ─────────────────────────────────────────────────────────────────
const state = {
    candidateName: '',
    interviewId: null,
    accessToken: null,
    currentQuestionId: null,
    currentQuestionIndex: 0,
    totalQuestions: 5,
    isRecording: false,
    mediaRecorder: null,
    audioChunks: [],
    stream: null,
    proctoringInterval: null,
    wsAlerts: null,
};

// ── View Management ───────────────────────────────────────────────────────────
function showView(viewId) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(viewId)) {
            link.classList.add('active');
        }
    });
    document.querySelectorAll('main > section').forEach(s => s.style.display = 'none');
    const target = document.getElementById(`view-${viewId}`);
    if (target) target.style.display = 'block';
    if (viewId !== 'interview') stopCamera();
}

// ── Toast Notifications ───────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const colors = { info: 'var(--accent-blue)', success: 'var(--accent-teal)', warning: '#F59E0B', error: '#EF4444' };
    const toast = document.getElementById('toast');
    toast.style.borderColor = colors[type] || colors.info;
    document.getElementById('toast-message').innerHTML = message;
    toast.style.display = 'flex';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => { toast.style.display = 'none'; }, 4500);
}

// ── Setup Modal ───────────────────────────────────────────────────────────────
function openSetupModal() {
    document.getElementById('setup-modal').style.display = 'flex';
}
function closeSetupModal() {
    document.getElementById('setup-modal').style.display = 'none';
}

// ── Camera ────────────────────────────────────────────────────────────────────
async function initCamera() {
    const video = document.getElementById('webcam-preview');
    if (!video) return;
    try {
        state.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        video.srcObject = state.stream;
    } catch (err) {
        showToast('⚠️ Camera access denied. Enable camera for proctoring.', 'warning');
    }
}

function stopCamera() {
    if (state.stream) { state.stream.getTracks().forEach(t => t.stop()); state.stream = null; }
    if (state.proctoringInterval) { clearInterval(state.proctoringInterval); state.proctoringInterval = null; }
    if (state.wsAlerts) { state.wsAlerts.close(); state.wsAlerts = null; }
}

// ── WebSocket: Proctoring Alerts ──────────────────────────────────────────────
function connectAlertWebSocket() {
    try {
        state.wsAlerts = new WebSocket(`ws://localhost:8000/ws/alerts`);
        state.wsAlerts.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.alerts?.length) showToast(`🚨 Alert: ${data.alerts[0]}`, 'warning');
        };
        state.wsAlerts.onerror = () => console.warn('[WS] Proctoring alerts offline.');
    } catch (e) { console.warn('[WS] Could not connect.'); }
}

// ── Proctoring: Send Frames Every 3s ─────────────────────────────────────────
function startProctoring() {
    if (!state.interviewId) return;
    const video = document.getElementById('webcam-preview');
    state.proctoringInterval = setInterval(async () => {
        if (!state.stream || !state.interviewId || !video.videoWidth) return;
        try {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth; canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            canvas.toBlob(async (blob) => {
                if (!blob) return;
                const form = new FormData();
                form.append('file', blob, 'frame.jpg');
                await fetch(`${API_BASE}/proctoring/process_frame?interview_id=${state.interviewId}`, { method: 'POST', body: form });
            }, 'image/jpeg', 0.7);
        } catch (e) { /* silent */ }
    }, 3000);
}

// ── Sanitize text before inserting into HTML (prevent XSS) ──────────────────
function safe(str) {
    const d = document.createElement('div');
    d.textContent = str ?? '';
    return d.innerHTML;
}

// ── Begin Interview ───────────────────────────────────────────────────────────
async function beginInterview() {
    const name = document.getElementById('setup-name').value.trim();
    const email = document.getElementById('setup-email').value.trim();
    const role = document.getElementById('setup-role').value.trim() || 'Software Engineer';
    const skillsRaw = document.getElementById('setup-skills').value.trim();
    const difficulty = document.getElementById('setup-difficulty').value;

    if (!name || !email) { showToast('Please enter your name and email.', 'warning'); return; }

    const skills = skillsRaw ? skillsRaw.split(',').map(s => s.trim()).filter(Boolean) : ['General'];
    const btn = document.getElementById('btn-begin');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    btn.disabled = true;

    // Stop any existing session cleanly before starting a new one
    stopCamera();
    state.interviewId = null;

    try {
        const res = await fetch(`${API_BASE}/interview/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_name: name, candidate_email: email, role, skills, difficulty, num_questions: 5, adaptive_mode: true, infinite_mode: false })
        });
        if (!res.ok) throw new Error(`Server responded ${res.status}. Is the backend running?`);
        const data = await res.json();

        state.interviewId = data.interview_id;
        state.accessToken = data.access_token;
        
        showToast('🚀 Interview started!', 'success');
        state.currentQuestionIndex = 0;
        state.totalQuestions = data.total_questions > 0 ? data.total_questions : 5;

        closeSetupModal();
        showView('interview');
        await initCamera();
        connectAlertWebSocket();
        startProctoring();
        await loadQuestion(0);
        showToast(`✅ Interview started for ${name}! Good luck 🚀`, 'success');
    } catch (e) {
        showToast(`❌ ${e.message}`, 'error');
    } finally {
        btn.innerHTML = 'Start Interview <i class="fas fa-arrow-right"></i>';
        btn.disabled = false;
    }
}

// ── Load Question by Index ────────────────────────────────────────────────────
async function loadQuestion(index) {
    if (!state.interviewId) return;
    const questionEl = document.getElementById('current-question');
    const progressEl = document.getElementById('question-progress');
    questionEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating question...';

    try {
        const res = await fetch(`${API_BASE}/interview/${state.interviewId}/question/${index}`, {
            headers: { 'Authorization': `Bearer ${state.accessToken}` }
        });
        const data = await res.json();

        if (data.finished) {
            questionEl.innerText = '🎉 Interview complete! Great job.';
            document.getElementById('btn-next-question').style.display = 'none';
            document.getElementById('btn-submit-answer').style.display = 'none';
            await loadResults();
            return;
        }

        state.currentQuestionId = data.question_id;
        state.currentQuestionIndex = index;

        questionEl.classList.remove('animate-fade');
        void questionEl.offsetWidth;
        questionEl.innerText = data.text;
        questionEl.classList.add('animate-fade');

        if (progressEl) progressEl.innerText = `Question ${index + 1} of ${data.total || state.totalQuestions}`;
        document.getElementById('answer-input').value = data.previous_answer || '';
        document.getElementById('ai-feedback').style.display = 'none';
        document.getElementById('btn-submit-answer').style.display = '';
        document.getElementById('btn-next-question').style.display = '';
    } catch (e) {
        showToast('❌ Could not load question. Is the backend running on port 8000?', 'error');
        questionEl.innerText = 'Failed to load question.';
    }
}

// ── Next Question ─────────────────────────────────────────────────────────────
async function nextQuestion() {
    await loadQuestion(state.currentQuestionIndex + 1);
}

// ── Submit Text Answer ────────────────────────────────────────────────────────
async function submitAnswer() {
    if (!state.interviewId || !state.currentQuestionId) {
        showToast('⚠️ No active session. Please start an interview first.', 'warning');
        return;
    }
    const answer = document.getElementById('answer-input').value.trim();
    if (!answer || answer.length < 3) { showToast('Please type or record your answer.', 'warning'); return; }

    const btn = document.getElementById('btn-submit-answer');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/interview/${state.interviewId}/submit-response`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.accessToken}`
            },
            body: JSON.stringify({
                question_id: state.currentQuestionId,
                answer_text: answer
            })
        });
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        const result = await res.json();

        // Update live metrics with real data
        const sentiment = result.sentiment ?? {};
        const speech = result.speech_metrics ?? {};
        const el = (id) => document.getElementById(id);

        if (el('metric-conf')) el('metric-conf').innerText = `${sentiment.confidence ?? Math.round((result.score ?? 5) * 10)}%`;
        if (el('metric-pace')) el('metric-pace').innerText = speech.pace ? `${speech.pace}` : `${speech.word_count ?? '—'} wds`;
        if (el('metric-fillers')) el('metric-fillers').innerText = speech.filler_count ?? 0;

        renderFeedback(result);
        showToast(`✅ Score: ${result.score ?? '?'}/10 — Feedback ready!`, 'success');
    } catch (e) {
        showToast(`❌ Evaluation failed: ${e.message}`, 'error');
    } finally {
        btn.innerHTML = 'Submit <i class="fas fa-paper-plane"></i>';
        btn.disabled = false;
    }
}

// ── Render AI Feedback Panel ──────────────────────────────────────────────────
function renderFeedback(result) {
    const panel = document.getElementById('ai-feedback');
    const score = result.score ?? 0;
    const color = score >= 8 ? 'var(--accent-teal)' : score >= 5 ? 'var(--accent-blue)' : '#EF4444';
    const strengths = (result.strengths || []).map(s => `<li>✅ ${safe(s)}</li>`).join('');
    const weaknesses = (result.weaknesses || []).map(w => `<li style="color:#FCA5A5">⚠️ ${safe(w)}</li>`).join('');
    const bfText = safe(result.behavioral_feedback ?? '');
    const tone = safe(result.sentiment?.tone ?? '');
    const star = result.star_audit ? `<p style="font-size:0.78rem;color:var(--text-secondary);margin-top:0.5rem">
        STAR: S:${safe(result.star_audit.situation)} · T:${safe(result.star_audit.task)} · A:${safe(result.star_audit.action)} · R:${safe(result.star_audit.result)}</p>` : '';

    panel.innerHTML = `
        <div style="display:grid;grid-template-columns:80px 1fr;gap:1rem;align-items:start;padding:1rem;background:rgba(255,255,255,0.04);border-radius:12px;border:1px solid var(--glass-border);">
            <div style="text-align:center">
                <div style="font-size:2rem;font-weight:700;color:${color}">${score}<span style="font-size:0.9rem">/10</span></div>
                <div style="font-size:0.7rem;color:var(--text-secondary)">${result.sentiment?.tone ?? ''}</div>
            </div>
            <div>
                <ul style="list-style:none;padding:0;margin:0 0 0.4rem;font-size:0.85rem">${strengths}</ul>
                <ul style="list-style:none;padding:0;margin:0;font-size:0.85rem">${weaknesses}</ul>
                ${bfText ? `<p style="font-size:0.8rem;margin-top:0.4rem;color:var(--text-secondary)">${bfText}</p>` : ''}
                ${star}
            </div>
        </div>`;
    panel.style.display = 'block';
}

// ── Audio Recording ───────────────────────────────────────────────────────────
async function toggleRecording() {
    const btn = document.getElementById('btn-record');
    if (!state.isRecording) {
        try {
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            state.audioChunks = [];
            state.mediaRecorder = new MediaRecorder(audioStream);
            state.mediaRecorder.ondataavailable = (e) => state.audioChunks.push(e.data);
            state.mediaRecorder.onstop = async () => {
                const blob = new Blob(state.audioChunks, { type: 'audio/webm' });
                await submitAudioAnswer(blob);
                audioStream.getTracks().forEach(t => t.stop());
            };
            state.mediaRecorder.start();
            state.isRecording = true;
            btn.innerHTML = '<i class="fas fa-stop" style="color:#EF4444"></i> Stop';
            btn.style.borderColor = '#EF4444';
        } catch (e) { showToast('❌ Microphone access denied.', 'error'); }
    } else {
        state.mediaRecorder.stop();
        state.isRecording = false;
        btn.innerHTML = '<i class="fas fa-microphone"></i> Record';
        btn.style.borderColor = '';
    }
}

async function submitAudioAnswer(blob) {
    if (!state.interviewId || !state.currentQuestionId) return;
    showToast('🎙️ Transcribing your audio...', 'info');
    const form = new FormData();
    form.append('file', blob, 'answer.webm');
    try {
        const res = await fetch(`${API_BASE}/interview/${state.interviewId}/submit-audio?question_id=${state.currentQuestionId}`, { 
            method: 'POST', 
            headers: { 'Authorization': `Bearer ${state.accessToken}` },
            body: form 
        });
        const data = await res.json();
        if (data.transcription) {
            document.getElementById('answer-input').value = data.transcription;
            const confEl = document.getElementById('metric-conf');
            if (confEl && data.score != null) confEl.innerText = `${Math.round(data.score * 10)}%`;
            showToast(`✅ Transcribed! Score: ${data.score ?? '?'}/10`, 'success');
        }
    } catch (e) { showToast('❌ Audio transcription failed.', 'error'); }
}

// ── Resume Upload & Analysis ──────────────────────────────────────────────────
async function uploadResume(event) {
    const file = event.target.files[0];
    if (!file) return;

    const btn = document.getElementById('btn-select-resume');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    btn.disabled = true;
    document.getElementById('ats-keyword').innerText = '—';
    document.getElementById('ats-format').innerText = '—';
    document.getElementById('ats-insight').innerText = 'AI is analyzing your resume...';

    const form = new FormData();
    form.append('file', file);

    try {
        const res = await fetch(`${API_BASE}/interview/analyze-resume`, { method: 'POST', body: form });
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        const result = await res.json();

        const ats = result.ats_fit ?? 0;
        const fmt = result.readability ?? 0;
        document.getElementById('ats-keyword').innerText = `${ats}%`;
        document.getElementById('ats-keyword-bar').style.width = `${ats}%`;
        document.getElementById('ats-format').innerText = `${fmt}%`;
        document.getElementById('ats-format-bar').style.width = `${fmt}%`;
        document.getElementById('ats-insight').innerText = result.best_practice_tip ?? 'Analysis complete.';

        const missing = document.getElementById('ats-missing');
        if (result.critical_keywords_missing?.length) {
            missing.innerText = `Missing keywords: ${result.critical_keywords_missing.slice(0, 5).join(', ')}`;
            missing.style.display = 'block';
        } else { missing.style.display = 'none'; }

        showToast(`✅ Resume analyzed! ATS Fit: ${ats}%`, 'success');
    } catch (e) {
        showToast(`❌ Resume analysis failed: ${e.message}`, 'error');
        document.getElementById('ats-insight').innerText = 'Analysis failed. Is the backend running?';
    } finally {
        btn.innerHTML = 'Select File';
        btn.disabled = false;
    }
}

// ── Load Results into Dashboard ───────────────────────────────────────────────
async function loadResults() {
    if (!state.interviewId) return;
    try {
        const res = await fetch(`${API_BASE}/interview/${state.interviewId}/results`, {
            headers: { 'Authorization': `Bearer ${state.accessToken}` }
        });
        if (!res.ok) return;
        const data = await res.json();

        const el = (id) => document.getElementById(id);

        // interview_score is 0-100, behavior_score is 0-100
        const techScore  = data.interview_score  ?? 0;
        const behavScore = data.behavior_score   ?? 0;

        if (el('dash-sessions'))   el('dash-sessions').innerText   = state.currentQuestionIndex + 1;
        if (el('dash-confidence')) el('dash-confidence').innerText = `${Math.round(behavScore)}%`;
        if (el('dash-grade'))      el('dash-grade').innerText      = scoreToGrade(techScore);

        showToast(`📊 Results ready! Score: ${techScore}% — ${data.final_decision ?? ''}`, 'success');
        showView('dashboard');
    } catch (e) {
        console.warn('Could not load results:', e);
    }
}


function scoreToGrade(score) {
    if (score >= 90) return 'A+';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B+';
    if (score >= 60) return 'B';
    if (score >= 50) return 'C';
    return 'F';
}
