from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services.ai_engine import ai_engine
from services.scoring import scoring_service
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
        target_role=data.role,
        target_skills=", ".join(data.skills) if isinstance(data.skills, list) else data.skills
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # Pre-generate questions for this session using real AI
    questions_list = ai_engine.generate_questions(
        role=data.role, 
        skills=data.skills, 
        difficulty=data.difficulty,
        count=data.num_questions,
        experience=data.experience,
        interview_type=data.interview_type,
        style=data.style
    )
    
    for q_text in questions_list:
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
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    
    if not question or not interview:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    evaluation = ai_engine.evaluate_answer(
        question.text, 
        answer_text, 
        role=interview.target_role or "Expert",
        skills=[s.strip() for s in (interview.target_skills or "").split(",")]
    )
    
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
    # Read audio bytes
    audio_bytes = await file.read()
    
    # Use real AI for transcription
    transcription = ai_engine.transcribe_bytes(audio_bytes)
    
    # Evaluate the transcribed answer
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    
    evaluation = ai_engine.evaluate_answer(
        question.text if question else "", 
        transcription,
        role=interview.target_role if interview else "Expert",
        skills=[s.strip() for s in (interview.target_skills or "").split(",")] if interview else []
    )
    score = evaluation.get("score", 0)
    
    response = models.Response(
        interview_id=interview_id, 
        question_id=question_id, 
        answer_text=transcription,
        relevance_score=score
    )
    db.add(response)
    db.commit()
    
    return {"transcription": transcription, "score": score}

@router.get("/{interview_id}/results")
def get_interview_results(interview_id: int, db: Session = Depends(get_db)):
    results = scoring_service.calculate_unified_score(interview_id, db)
    return results
