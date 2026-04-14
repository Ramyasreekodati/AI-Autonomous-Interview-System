from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services.stt import stt_service
from services.scoring import scoring_service
from services.llm import llm_service
import os
from fastapi import UploadFile, File

router = APIRouter(prefix="/interview", tags=["interview"])

@router.post("/start")
def start_interview(candidate_email: str, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.email == candidate_email).first()
    if not candidate:
        candidate = models.Candidate(name="Guest", email=candidate_email)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    
    interview = models.Interview(candidate_id=candidate.id, status="ongoing")
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return {"interview_id": interview.id, "message": "Interview started"}

@router.get("/{interview_id}/next-question")
def get_next_question(interview_id: int, db: Session = Depends(get_db)):
    # Simple logic: get a random question not yet answered
    answered_q_ids = db.query(models.Response.question_id).filter(models.Response.interview_id == interview_id).all()
    answered_q_ids = [q[0] for q in answered_q_ids]
    
    # End interview after 5 questions for this demo
    if len(answered_q_ids) >= 5:
        # Update interview status to completed
        interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
        if interview:
            interview.status = "completed"
            db.commit()
        return {"finished": True}
    
    question = db.query(models.Question).filter(~models.Question.id.in_(answered_q_ids)).first()
    if not question:
        # Generate a new question on the fly
        text = llm_service.generate_question()
        new_q = models.Question(text=text, category="AI-Generated")
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        question = new_q
    
    return {"question_id": question.id, "text": question.text, "finished": False}

@router.post("/{interview_id}/submit-response")
def submit_response(interview_id: int, question_id: int, answer_text: str, db: Session = Depends(get_db)):
    response = models.Response(interview_id=interview_id, question_id=question_id, answer_text=answer_text)
    db.add(response)
    db.commit()
    return {"message": "Response submitted"}

@router.post("/{interview_id}/submit-audio")
async def submit_audio_response(interview_id: int, question_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_path = f"temp_{interview_id}_{question_id}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    transcription = stt_service.transcribe(temp_path)
    # os.remove(temp_path) # Optionally keep for debugging
    
    score, sentiment = scoring_service.evaluate_response(transcription, "")
    
    response = models.Response(
        interview_id=interview_id, 
        question_id=question_id, 
        answer_text=transcription,
        sentiment_score=sentiment,
        relevance_score=score
    )
    db.add(response)
    db.commit()
    
    return {"transcription": transcription, "score": score}

@router.get("/{interview_id}/results")
def get_interview_results(interview_id: int, db: Session = Depends(get_db)):
    results = scoring_service.calculate_unified_score(interview_id, db)
    return results
