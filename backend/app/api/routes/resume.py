from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.resume import ResumeRead
from app.services.resume_service import create_resume as create_resume_service


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
	return create_resume_service(file, db)


@router.post("/upload", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
	return create_resume_service(file, db)