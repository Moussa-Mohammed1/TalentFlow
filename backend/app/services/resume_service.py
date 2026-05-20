from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate


def create_resume(payload: ResumeCreate, db: Session) -> Resume:
	resume = Resume(path=payload.path)
	db.add(resume)
	db.commit()
	db.refresh(resume)
	return resume
