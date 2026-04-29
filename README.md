# 🚀 RecruitAI: Elite Professional Auditor
### Autonomous AI Technical Interview & Proctoring System

**RecruitAI** is a state-of-the-art, end-to-end platform for automated technical interviews. It leverages the latest multimodal AI (Google Gemini 1.5) to conduct, monitor, and evaluate candidates with human-level precision and enterprise-grade reliability.

---

## ✨ Key Features

- **🧠 Multi-Agent Interview Flow**: Powered by LangGraph, featuring Evaluator, Interviewer, and Orchestrator agents.
- **🎙️ Real-time Analysis**: Live speech-to-text with behavioral metrics (pace, confidence, tone).
- **🛡️ AI Proctoring**: Real-time surveillance tracking gaze, emotion, and suspicious objects.
- **📄 Resume AI Scanner**: ATS optimization and job match analysis.
- **📊 Admin Dashboard**: Recruiter portal for viewing interview recordings and detailed PDF reports.
- **💎 Glassmorphism UI**: High-end, modern React frontend with smooth animations.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS 4 + Framer Motion
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **AI Core**: Google Gemini 1.5 (via LangChain & LangGraph)
- **Database**: SQLite with SQLAlchemy
- **Surveillance**: MediaPipe + OpenCV

---

## 🚦 Quick Start

### 1. Prerequisites
- Python 3.9+
- Node.js & npm
- A Google Gemini API Key

### 2. Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Installation & Run

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Admin Dashboard (Optional)
```bash
streamlit run streamlit_app.py
```

## 📂 Project Structure
```text
├── backend/            # FastAPI Server
│   ├── agents/         # LangGraph Multi-Agent logic
│   ├── services/       # Core services (AI, STT, Proctoring)
│   ├── routers/        # API Endpoints
│   └── database.py     # SQLAlchemy Configuration
├── frontend/           # React Application
│   ├── src/components/ # Reusable UI components
│   └── src/pages/      # Main application views
├── admin/              # (Planned) Admin tools
├── streamlit_app.py    # Admin & Recruiter Dashboard
├── docs/               # Project documentation & reports
└── .env                # Environment Configuration
```

---
Built with ❤️ by **[Kodati Ramya Sree](https://github.com/Ramyasreekodati)**
*Final Project Submission - Career Success Risk Modeling*