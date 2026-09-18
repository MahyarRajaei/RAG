import hashlib
from pathlib import Path

from sqlalchemy.orm import Session

from model.document import Document, DocumentStatus, MIMEType
from repository.document_repository import DocumentRepository


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class DocumentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DocumentRepository(session)

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

        document = Document(
            filename=path.name,
            file_hash=file_hash,
            content_hash=content_hash,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            status=status,
            chunk_count=0,
        )
        return self.repository.add(document)
