import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, UploadFile
from sqlalchemy.orm import Session

from application.api.deps import get_db, get_ingestion_pipeline, get_storage
from application.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    UploadDocumentResponse,
)
from excep.document import (
    DocumentNotFoundError,
    EmptyFileError,
    UnsupportedFileTypeError,
)
from model.document import DocumentStatus, MIMEType

# from repository.chunk_repository import ChunkRepository
# from repository.document_repository import DocumentRepository
from service.document_service import DocumentService

logger = logging.getLogger("adan.documents")
router = APIRouter()

SUFFIX_TO_MIME = {
    ".txt": MIMEType.TXT,
    ".md": MIMEType.MARKDOWN,
    ".docx": MIMEType.DOCX,
}


def _resolve_file_type(filename: str) -> MIMEType:
    from pathlib import Path

    suffix = Path(filename).suffix.lower()
    file_type = SUFFIX_TO_MIME.get(suffix)
    if file_type is None:
        raise UnsupportedFileTypeError(filename)
    return file_type


@router.post("", response_model=UploadDocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: Session = Depends(get_db),
    storage=Depends(get_storage),
):
    file_type = _resolve_file_type(file.filename)
    raw_bytes = await file.read()
    if len(raw_bytes) == 0:
        raise EmptyFileError(file.filename)

    document_service = DocumentService(db, storage)
    document = document_service.insert_file(raw_bytes, file.filename)

    pipeline = get_ingestion_pipeline(db)
    background_tasks.add_task(pipeline.process, document.id)

    return UploadDocumentResponse(
        id=document.id, filename=document.filename, status=document.status
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: DocumentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
    storage=Depends(get_storage),
):
    document_service = DocumentService(db, storage)
    items, total = document_service.list_doc(limit=limit, offset=offset, status=status)
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    storage=Depends(get_storage),
):
    document_service = DocumentService(db, storage)
    document = document_service.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(document_id)
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    storage=Depends(get_storage),
):
    document_service = DocumentService(db, storage)
    document = document_service.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(document_id)

    document_service = DocumentService(db, storage)
    document_service.delete(document_id)

    db.commit()
