import streamlit as st

st.set_page_config(
    page_title="AI Autonomous Interview System",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Autonomous Interview System")
st.markdown("""
### Welcome to the AI Autonomous Interview System Dashboard
This project is a comprehensive technical interview platform featuring:
- **AI Proctoring**: Real-time surveillance using computer vision.
- **Dynamic Questioning**: NLP-driven interview flows.
- **Automated Scoring**: Unified performance metrics.
- **Executive Reporting**: PDF report generation.

---

#### 🛠 Project Architecture
The system is built with:
1. **Backend**: FastAPI (Python)
2. **Frontend**: React (Vite/Tailwind)
3. **AI Models**: Transformers, OpenCV, Dlib

#### 🚀 Deployment Info
- **GitHub Repository**: [AI-Autonomous-Interview-System](https://github.com/Ramyasreekodati/AI-Autonomous-Interview-System)
- **Frontend**: To deploy the React app, we recommend **Vercel** or **Netlify**.
- **Backend**: To deploy the FastAPI app, we recommend **Render**, **Railway**, or **AWS/GCP**.

*Note: This Streamlit page serves as a project showcase and documentation hub.*
""")

st.sidebar.info("Developed by Kodati Ramya Sree")
st.sidebar.markdown("[GitHub Profile](https://github.com/Ramyasreekodati)")
