from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routers import interview, auth

load_dotenv() # Load variables from .env
from services.surveillance import surveillance
from database import get_db, engine
import models
from sqlalchemy.orm import Session
from services.reporting import reporting_service
from fastapi import UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Autonomous Interview System")
print("DEBUG: MAIN.PY LOADED - AUTH ROUTER INCLUDED")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
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

@app.post("/proctoring/process_frame")
async def process_frame(interview_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    frame_bytes = await file.read()
    result = surveillance.process_frame(frame_bytes, interview_id, db)
    
    # Broadcast alerts to admin dashboard
    if result["alerts"]:
        await manager.broadcast({"interview_id": interview_id, "alerts": result["alerts"]})
        
    return result

@app.get("/interview/{interview_id}/report")
async def get_report(interview_id: int, db: Session = Depends(get_db)):
    from services.scoring import scoring_service
    results = scoring_service.calculate_unified_score(interview_id, db)
    # Fetch candidate name
    candidate = db.query(models.Candidate).join(models.Interview).filter(models.Interview.id == interview_id).first()
    name = candidate.name if candidate else "Candidate"
    
    report_path = reporting_service.generate_report(name, results)
    return FileResponse(report_path, filename=f"RecruitAI_Report_{interview_id}.pdf")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Autonomous Interview System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
