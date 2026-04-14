# AI Autonomous Interview System

A state-of-the-art, end-to-end platform for automated technical interviews, featuring real-time AI surveillance, behavioral analysis, and automated scoring.

## 🚀 Overview

This system streamlines the recruitment process by leveraging AI to conduct, monitor, and evaluate interviews. It provides:
- **AI Proctoring**: Real-time eye tracking, head pose detection, and object detection to ensure interview integrity.
- **Dynamic Questioning**: Adaptive NLP-driven questions based on candidate responses.
- **Automated Scoring**: Intelligent grading using NLP and sentiment analysis.
- **Executive Reporting**: Comprehensive performance dashboards for recruiters.

## 🛠 Tech Stack

- **Backend**: FastAPI (Python), SQLite (SQLAlchemy), JWT Authentication.
- **Frontend**: React (Vite), Tailwind CSS, Lucide Icons.
- **AI/ML**: Computer Vision (Proctoring), NLP (Evaluation).

## 📁 Project Structure

```text
├── backend/            # FastAPI application logic and routers
├── frontend/           # React + Vite frontend application
├── .gitignore          # Root ignore file
└── README.md           # Project documentation
```

## 🚦 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. `uvicorn main:app --reload`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## 📊 Phase Implementation
The project was completed in a structured 5-phase approach:
1. **Core Architecture**: Backend & Frontend foundations.
2. **AI Integration**: Surveillance and proctoring layers.
3. **Data Fusion**: Authentication and database persistence.
4. **Analytics**: Scoring and interview logic.
5. **Polishing**: Deployment readiness and UX optimization.

---
Built with ❤️ by [Kodati Ramya Sree](https://github.com/Ramyasreekodati)