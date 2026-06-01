from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict


class ResumeBase(BaseModel):
	path: str


class ResumeCreate(BaseModel):
	file: UploadFile


class ResumeRead(ResumeBase):
	id: int
	created_at: datetime | None = None

	model_config = ConfigDict(from_attributes=True)


class ResumeTextRead(BaseModel):
	raw_text: str | list
