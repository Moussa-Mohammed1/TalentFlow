from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pathlib import Path
import shutil
import tempfile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.resume import ResumeRead, ResumeTextRead
from app.services.resume_service import create_resume as create_resume_service
from app.services.text_extractor_service import TextExtractionService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
	return create_resume_service(file, db)


@router.post("/upload", response_model=ResumeTextRead, status_code=status.HTTP_201_CREATED)
def upload_resume(file: UploadFile = File(...)):
	extractor = TextExtractionService()
	if not file.filename:
		raise HTTPException(status_code=400, detail="Resume file is required")

	file_suffix = Path(file.filename).suffix.lower()
	with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
		shutil.copyfileobj(file.file, temp_file)
		temp_path = temp_file.name

	try:
		raw_text = extractor.extract(temp_path)
	finally:
		Path(temp_path).unlink(missing_ok=True)

	return ResumeTextRead(raw_text=raw_text)