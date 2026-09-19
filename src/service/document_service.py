import hashlib
import logging
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

import db
from excep import DocumentNotFoundError, UnsupportedFileTypeError
from model.document import Document, DocumentStatus, MIMEType
from repository.document_repository import DocumentRepository

logger = logging.getLogger("adan.documents")

SUFFIX_TO_MIME = {
    ".md": MIMEType.MARKDOWN,
    ".markdown": MIMEType.MARKDOWN,
    ".txt": MIMEType.TXT,
    ".docx": MIMEType.DOCX,
}


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class DocumentService:
    def __init__(self, session: Session, storage: db.FileStorage) -> None:
        self.session = session
        self.repository = DocumentRepository(session)
        self.storage = storage

    def insert_from_file(
        self,
        file_path: str | Path,
        status: DocumentStatus = DocumentStatus.PENDING,
    ) -> Document:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        return self._insert(path.read_bytes(), path.name, status)

    def insert_file(
        self,
        raw_bytes: bytes,
        file_name: str | Path,
        status: DocumentStatus = DocumentStatus.PENDING,
    ) -> Document:
        return self._insert(raw_bytes, str(file_name), status)

    def _insert(
        self, raw_bytes: bytes, filename: str, status: DocumentStatus
    ) -> Document:
        file_type = self._resolve_file_type(filename)

        file_hash = compute_sha256(raw_bytes)
        existing = self.repository.get_by_file_hash(file_hash)
        if existing:
            logger.info(
                "duplicate_upload",
                extra={"filename": filename, "existing_id": str(existing.id)},
            )
            return existing

        document_id = uuid.uuid4()
        storage_path = self.storage.save(document_id, filename, raw_bytes)

        document = Document(
            id=document_id,
            filename=filename,
            file_hash=file_hash,
            storage_path=storage_path,
            file_type=file_type,
            file_size_bytes=len(raw_bytes),
            status=status,
            chunk_count=0,
        )
        logger.info(
            "document_created",
            extra={"document_id": str(document_id), "filename": filename},
        )
        return self.repository.add(document)

    @staticmethod
    def _resolve_file_type(filename: str) -> MIMEType:
        suffix = Path(filename).suffix.lower()
        file_type = SUFFIX_TO_MIME.get(suffix)
        if file_type is None:
            raise UnsupportedFileTypeError(filename)
        return file_type

    def list_doc(
        self,
        limit: int = 20,
        offset: int = 0,
        status: DocumentStatus | None = None,
    ) -> tuple[list[Document], int]:
        return self.repository.list_paginated(limit=limit, offset=offset, status=status)

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.session.get(Document, document_id)

    def get_content(self, document_id: uuid.UUID) -> bytes:
        document = self.repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return self.storage.read(document.storage_path)

    def delete(self, document_id: uuid.UUID) -> None:
        document = self.repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        self.repository.delete(document)
        self.session.commit()

        try:
            self.storage.delete(document.storage_path)
        except FileNotFoundError:
            logger.warning(
                "storage_file_missing_on_delete",
                extra={
                    "document_id": str(document_id),
                    "storage_path": document.storage_path,
                },
            )
        except Exception:
            logger.exception(
                "storage_delete_failed",
                extra={
                    "document_id": str(document_id),
                    "storage_path": document.storage_path,
                },
            )
        logger.info("document_deleted", extra={"document_id": str(document_id)})
