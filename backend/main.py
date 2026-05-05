from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routers import interview, auth

load_dotenv() # Load variables from .env
from services.surveillance import surveillance
import logging
from database import get_db, engine
import models
from sqlalchemy.orm import Session
from services.reporting import reporting_service

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainAPI")
from fastapi import UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import FileResponse
from typing import List
import json
import io
import datetime
import PyPDF2
from agents import interview_graph, InterviewState
from agents.resume_agent import analyze_resume

models.Base.metadata.create_all(bind=engine)

# 🛠️ INTERNAL CONNECTION FIX: Manual Migration
def run_migrations():
    from sqlalchemy import text
    with engine.connect() as conn:
        columns = [row[1] for row in conn.execute(text("PRAGMA table_info(interviews)")).fetchall()]
        if "experience_level" not in columns:
            conn.execute(text("ALTER TABLE interviews ADD COLUMN experience_level VARCHAR"))
        if "infinite_mode" not in columns:
            conn.execute(text("ALTER TABLE interviews ADD COLUMN infinite_mode BOOLEAN DEFAULT 0"))
        if "adaptive_mode" not in columns:
            conn.execute(text("ALTER TABLE interviews ADD COLUMN adaptive_mode BOOLEAN DEFAULT 1"))
        if "target_role" not in columns:
            conn.execute(text("ALTER TABLE interviews ADD COLUMN target_role VARCHAR"))
        if "target_skills" not in columns:
            conn.execute(text("ALTER TABLE interviews ADD COLUMN target_skills VARCHAR"))
        conn.commit()

try:
    run_migrations()
    logger.info("DATABASE SCHEMA SYNCED SUCCESSFULLY")
except Exception as e:
    logger.warning(f"MIGRATION WARNING: {str(e)}")

from routers import recruiter
app = FastAPI(title="AI Autonomous Interview System")
app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(recruiter.router)
logger.info("MAIN.PY LOADED - ALL ROUTERS INCLUDED")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "null",  # Allows requests from file:// (browser sends Origin: null)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview.router)
app.include_router(auth.router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    import logging
    logging.error(f"Global Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket): 
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket) # Using standard names
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/interview")
async def interview_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize the interview state
    current_state = {
        "candidate_id": "test_user",
        "candidate_name": "John Doe",
        "job_role": "Software Engineer",
        "difficulty": "Adaptive",
        "transcript": [],
        "current_question": "",
        "question_count": 0,
        "scores": {"technical": 0, "communication": 0, "overall_grade": 0},
        "proctoring_alerts": [],
        "status": "in_progress"
    }
    
    # Trigger the first question
    result_state = interview_graph.invoke(current_state)
    current_state.update(result_state)
    await websocket.send_json({"type": "state_update", "state": current_state})
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "human_answer":
                # Add human answer to state
                current_state["transcript"].append({"role": "human", "content": message["content"]})
                
                # Run the graph again (it goes to Evaluator, then Interviewer)
                new_state = interview_graph.invoke(current_state)
                current_state.update(new_state)
                
                # Award XP and check for badges (Live Data Connection)
                try:
                    db = next(get_db())
                    email = "candidate@audit.ai" # Fixed for MVP session
                    xp_reward = 50 if current_state["scores"].get("overall_grade", 0) > 60 else 10
                    
                    # Call the update logic
                    await update_user_stats({
                        "email": email, 
                        "xp_gain": xp_reward, 
                        "badge": current_state["scores"].get("badge")
                    }, db)
                except Exception as e:
                    print(f"Stats Update Error: {e}")

                # Send the updated state back to frontend
                await websocket.send_json({"type": "state_update", "state": current_state})
                
    except WebSocketDisconnect:
        logger.info("Interview WebSocket disconnected")

@app.post("/proctoring/process_frame")
async def process_frame(interview_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    frame_bytes = await file.read()
    result = surveillance.process_frame(frame_bytes, interview_id, db)
    
    # Broadcast alerts to admin dashboard
    if result["alerts"]:
        await manager.broadcast({"interview_id": interview_id, "alerts": result["alerts"]})
        
    return result

@app.get("/user/stats/{candidate_email}")
async def get_user_stats(candidate_email: str, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.email == candidate_email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.stats:
        # Initialize stats if they don't exist
        new_stats = models.UserStats(candidate_id=candidate.id, streak=0, xp=0, badges=[])
        db.add(new_stats)
        db.commit()
        db.refresh(candidate)
    
    return {
        "streak": candidate.stats.streak,
        "xp": candidate.stats.xp,
        "badges": candidate.stats.badges
    }

@app.post("/user/stats/update")
async def update_user_stats(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    xp_gain = data.get("xp_gain", 0)
    new_badge = data.get("badge")
    
    candidate = db.query(models.Candidate).filter(models.Candidate.email == email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.stats:
        candidate.stats = models.UserStats(candidate_id=candidate.id)
    
    candidate.stats.xp += xp_gain
    if new_badge and new_badge not in candidate.stats.badges:
        # We need to re-assign to trigger JSON change detection in SQLAlchemy
        badges = list(candidate.stats.badges)
        badges.append(new_badge)
        candidate.stats.badges = badges
    
    # Simple streak logic: if practiced today, check last practice date
    now = datetime.datetime.utcnow()
    if candidate.stats.last_practice_date.date() < now.date():
        if (now.date() - candidate.stats.last_practice_date.date()).days == 1:
            candidate.stats.streak += 1
        else:
            candidate.stats.streak = 1
        candidate.stats.last_practice_date = now
        
    db.commit()
    return {"status": "success", "new_stats": {"xp": candidate.stats.xp, "streak": candidate.stats.streak}}

@app.post("/resume/analyze")
async def process_resume(file: UploadFile = File(...), job_desc: str = Form(...)):
    try:
        pdf_bytes = await file.read()
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        resume_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        analysis = analyze_resume(resume_text, job_desc)
        return analysis
    except Exception as e:
        return {"error": str(e)}

@app.delete("/user/data/{candidate_email}")
async def delete_user_data(candidate_email: str, db: Session = Depends(get_db)):
    """
    GDPR/DPDP Compliant endpoint to completely wipe a user's data.
    """
    try:
        candidate = db.query(models.Candidate).filter(models.Candidate.email == candidate_email).first()
        if not candidate:
            return {"status": "error", "message": "Candidate not found"}
            
        # Delete associated interviews
        db.query(models.Interview).filter(models.Interview.candidate_id == candidate.id).delete()
        # Delete candidate
        db.delete(candidate)
        db.commit()
        
        return {"status": "success", "message": "All user data securely wiped from system."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/interview/{interview_id}/report")
async def get_report(interview_id: int, db: Session = Depends(get_db)):
    from services.scoring import scoring_service
    results = scoring_service.calculate_unified_score(interview_id, db)
    # Fetch candidate name
    candidate = db.query(models.Candidate).join(models.Interview).filter(models.Interview.id == interview_id).first()
    name = candidate.name if candidate else "Candidate"
    
    report_path = reporting_service.generate_report(name, results)
    return FileResponse(report_path, filename=f"RecruitAI_Report_{interview_id}.pdf")

# @app.get("/")
# async def root():
#     return {"message": "Welcome to AI Autonomous Interview System API"}

from fastapi.staticfiles import StaticFiles

# --- API ROUTES END HERE ---

# Mount Frontend Build (Ensure this is AFTER all API routes)
# We check if the directory exists first to avoid crashes during development
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    async def root_fallback():
        return {"message": "Welcome to RecruitAI API. Frontend build not found. Run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
