# 🚀 RecruitAI: Elite Professional Auditor
### Autonomous AI Technical Interview & Proctoring System

**RecruitAI** is a state-of-the-art, end-to-end platform for automated technical interviews. It leverages the latest multimodal AI (Google Gemini 1.5) to conduct, monitor, and evaluate candidates with human-level precision and enterprise-grade reliability.

---

## ✨ Key Features

- **🧠 Intelligent Technical Audit**: Adaptive question generation focused on specific core competencies (Python, AWS, Distributed Systems, etc.).
- **🎙️ Zero-Fail STT Engine**: Robust Speech-to-Text pipeline with a multimodal cloud bridge, ensuring reliable transcription even without local system dependencies.
- **🛡️ AI Proctoring & Integrity**: Real-time behavioral surveillance, including gaze tracking, emotion detection, and object detection (phone/book).
- **📊 Automated Certification**: Comprehensive evaluation reports featuring technical scoring, behavioral risk assessment, and hiring justifications.
- **💎 Enterprise UI/UX**: Professional, high-visibility "Light-Theme" dashboard designed for recruiters and technical managers.

## 🛠️ Tech Stack

- **Framework**: Streamlit (Production Grade)
- **AI Core**: Google Gemini 1.5 Flash / Pro (Multimodal)
- **Transcription**: SpeechRecognition + Pydub + Gemini Multimodal Bridge
- **Surveillance**: MediaPipe + OpenCV (Computer Vision)
- **State Management**: Robust Session Persistence
- **Design**: Professional CSS with custom glassmorphism components

## 🚦 Quick Start

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Ramyasreekodati/AI-Autonomous-Interview-System.git
cd AI-Autonomous-Interview-System

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the Audit System
```bash
streamlit run streamlit_app.py
```

## 📂 Project Structure
```text
├── streamlit_app.py     # Main Entry Point (Auditor Dashboard)
├── backend/
│   ├── services/
│   │   ├── ai_engine.py    # Master AI Logic (STT, Evaluation, Generation)
│   │   ├── surveillance.py # Computer Vision & Proctoring
│   │   └── reporting.py    # Analytics & PDF Generation
├── .env                 # Environment Configuration
└── requirements.txt     # System Dependencies
```

---
Built with ❤️ by **[Kodati Ramya Sree](https://github.com/Ramyasreekodati)**
*Final Project Submission - Career Success Risk Modeling*