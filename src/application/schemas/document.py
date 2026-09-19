from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from model.document import DocumentStatus, MIMEType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    file_type: MIMEType
    status: DocumentStatus
    status_reason: str | None
    chunk_count: int | None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    limit: int
    offset: int


class UploadDocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: DocumentStatus
