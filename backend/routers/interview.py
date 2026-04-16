from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services.stt import stt_service
from services.scoring import scoring_service
from services.llm import llm_service
import os
import datetime
from typing import List

router = APIRouter(prefix="/interview", tags=["interview"])

@router.post("/start")
def start_interview(data: schemas.InterviewStart, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.email == data.candidate_email).first()
    if not candidate:
        candidate = models.Candidate(name=data.candidate_name, email=data.candidate_email)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    
    interview = models.Interview(
        candidate_id=candidate.id, 
        status="ongoing",
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # Pre-generate questions for this session to ensure "Navigation Logic" works smoothly
    for i in range(data.num_questions):
        q_text = llm_service.generate_question(role=data.role, skills=data.skills, difficulty=data.difficulty)
        question = models.Question(interview_id=interview.id, text=q_text, category=data.role, difficulty=data.difficulty)
        db.add(question)
    
    db.commit()
    
    return {"interview_id": interview.id, "message": "Interview started", "total_questions": data.num_questions}

@router.get("/{interview_id}/question/{question_index}")
def get_question_by_index(interview_id: int, question_index: int, db: Session = Depends(get_db)):
    # Phase 1: Navigation Logic - Retrieve question by index
    questions = db.query(models.Question).filter(models.Question.interview_id == interview_id).all()
    if question_index < 0 or question_index >= len(questions):
        return {"finished": True}
    
    question = questions[question_index]
    
    # Check if there's already a response for this question in this session
    existing_response = db.query(models.Response).filter(
        models.Response.interview_id == interview_id,
        models.Response.question_id == question.id
    ).first()
    
    return {
        "question_id": question.id,
        "text": question.text,
        "previous_answer": existing_response.answer_text if existing_response else "",
        "finished": False,
        "total": len(questions)
    }

@router.post("/{interview_id}/submit-response")
def submit_response(interview_id: int, question_id: int, answer_text: str, db: Session = Depends(get_db)):
    # Phase 1: Validation
    if not answer_text or len(answer_text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Answer is empty or too short.")
    
    # Phase 2: Evaluation Engine (Strictly based on input)
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    evaluation = scoring_service.evaluate_response(answer_text, question.text)
    
    # Phase 1: Unique Answer Storage (update if exists)
    response = db.query(models.Response).filter(
        models.Response.interview_id == interview_id,
        models.Response.question_id == question_id
    ).first()
    
    if response:
        response.answer_text = answer_text
        response.timestamp = datetime.datetime.utcnow()
        response.relevance_score = evaluation["score"]
    else:
        response = models.Response(
            interview_id=interview_id, 
            question_id=question_id, 
            answer_text=answer_text,
            relevance_score=evaluation["score"]
        )
        db.add(response)
    
    db.commit()
    
    # Phase 2 REQUIREMENT: RETURN ONLY JSON
    return evaluation

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
