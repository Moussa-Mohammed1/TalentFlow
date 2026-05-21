from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pathlib import Path
import shutil
import tempfile

from app.schemas.resume import ResumeRead, ResumeTextRead
from app.services.text_extractor_service import TextExtractionService

router = APIRouter(prefix="/resumes", tags=["resumes"])


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