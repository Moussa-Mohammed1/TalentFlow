from fastapi import HTTPException, UploadFile
from pathlib import Path
import shutil
import uuid

from sqlalchemy.orm import Session

from app.models.resume import Resume


# UPLOAD_DIR = Path(__file__).resolve().parents[2] / "storage" / "resumes"
UPLOAD_DIR = Path("storage/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions and MIME types for resumes
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
	"application/pdf",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def create_resume(file: UploadFile, db: Session) -> Resume:
	if not file.filename:
		raise HTTPException(status_code=400, detail="Resume file is required")

	# Validate file extension and content type
	file_ext = Path(file.filename).suffix.lower()
	content_type = (file.content_type or "").lower()
	if file_ext not in ALLOWED_EXTENSIONS or content_type not in ALLOWED_CONTENT_TYPES:
		raise HTTPException(
			status_code=400,
			detail="Invalid file type. Only PDF and DOCX files are accepted.",
		)

	unique_name = f"{uuid.uuid4()}-{Path(file.filename).name}"
	file_path = UPLOAD_DIR / unique_name

	with file_path.open("wb") as buffer:
		shutil.copyfileobj(file.file, buffer)

	resume = Resume(path=str(file_path))
	db.add(resume)
	db.commit()
	db.refresh(resume)
	return resume
