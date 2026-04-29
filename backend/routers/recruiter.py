from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from typing import List

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])

@router.get("/candidates")
def get_all_candidates(db: Session = Depends(get_db)):
    """Fetch all registered candidates."""
    return db.query(models.Candidate).all()

@router.get("/interviews")
def get_all_interviews(db: Session = Depends(get_db)):
    """Fetch all interview sessions with scores."""
    return db.query(models.Interview).order_by(models.Interview.start_time.desc()).all()

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """Global system metrics for recruiter."""
    total_interviews = db.query(models.Interview).count()
    avg_score = db.query(models.Interview).filter(models.Interview.status == "completed").all()
    # Simple calculation for demo
    scores = [i.total_score for i in avg_score if i.total_score > 0]
    mean_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "total_sessions": total_interviews,
        "average_score": round(mean_score, 1),
        "total_candidates": db.query(models.Candidate).count()
    }
