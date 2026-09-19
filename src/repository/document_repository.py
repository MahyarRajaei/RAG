import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from model.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, document: Document) -> Document:
        self.session.add(document)
        self.session.flush()
        return document

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.session.get(Document, document_id)

    def get_by_file_hash(self, file_hash: str) -> Document | None:
        stmt = select(Document).where(Document.file_hash == file_hash)
        return self.session.scalar(stmt)

    def list_all(self) -> Sequence[Document]:
        stmt = select(Document).order_by(Document.created_at.desc())
        return self.session.scalars(stmt).all()

    def list_paginated(
        self,
        limit: int,
        offset: int,
        status: DocumentStatus | None = None,
    ) -> tuple[Sequence[Document], int]:
        stmt = select(Document)
        count_stmt = select(func.count()).select_from(Document)

        if status is not None:
            stmt = stmt.where(Document.status == status)
            count_stmt = count_stmt.where(Document.status == status)

        total = self.session.scalar(count_stmt) or 0

        stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)
        items = self.session.scalars(stmt).all()

        return items, total

    def delete(self, document: Document) -> None:
        self.session.delete(document)
        self.session.flush()
