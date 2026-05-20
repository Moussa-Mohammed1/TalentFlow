from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.resume import ResumeCreate, ResumeRead
from app.services.resume_service import create_resume as create_resume_service


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume(payload: ResumeCreate, db: Session = Depends(get_db)):
	return create_resume_service(payload, db)


from app.core.database import engine
from sqlalchemy import text
@router.get("/test-db")
def test_db():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"message": "Database connected"}