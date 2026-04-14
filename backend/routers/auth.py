from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = db.query(models.Candidate).filter(models.Candidate.email == candidate.email).first()
    if db_candidate:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth_service.get_password_hash(candidate.password)
    new_candidate = models.Candidate(
        name=candidate.name,
        email=candidate.email,
        hashed_password=hashed_password
    )
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return {"message": "Candidate registered successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.email == form_data.username).first()
    if not candidate or not auth_service.verify_password(form_data.password, candidate.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": candidate.email})
    return {"access_token": access_token, "token_type": "bearer"}
