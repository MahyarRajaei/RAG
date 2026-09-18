import hashlib
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

import db
from excep import DocumentNotFoundError
from model.document import Document, DocumentStatus, MIMEType
from repository.document_repository import DocumentRepository


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

        raw_bytes = path.read_bytes()
        file_hash = compute_sha256(raw_bytes)
        content_hash = file_hash
        file_size_bytes = len(raw_bytes)

        suffix = path.suffix.lower()
        if suffix in [".md", ".markdown"]:
            file_type = MIMEType.MARKDOWN
        elif suffix == ".txt":
            file_type = MIMEType.TXT
        elif suffix == ".docx":
            file_type = MIMEType.DOCX
        else:
            file_type = MIMEType.TXT

        existing = self.repository.get_by_file_hash(file_hash)
        if existing:
            return existing

        document_id = uuid.uuid4()
        storage_path = self.storage.save(document_id, path.name, raw_bytes)

        document = Document(
            # id=document_id,
            filename=path.name,
            file_hash=file_hash,
            content_hash=content_hash,
            storage_path=storage_path,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            status=status,
            chunk_count=0,
        )
        return self.repository.add(document)

    def list_doc(self):
        return self.repository.list_all()

    def get_content(self, document_id: uuid.UUID) -> bytes:
        document = self.repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        print(document)
        return self.storage.read(document.storage_path)
