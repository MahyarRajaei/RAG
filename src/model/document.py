import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from db.session import Base

if TYPE_CHECKING:
    from model.chunk import Chunk


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class MIMEType(StrEnum):
    TXT = "text"
    MARKDOWN = "md"
    DOCX = "docx"


class Document(Base):
    __tablename__ = "document"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[MIMEType] = mapped_column(
        Enum(MIMEType, name="file_type_enum"), nullable=False
    )
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status_enum"),
        nullable=False,
        default=DocumentStatus.PENDING,
        index=True,
    )

    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    status_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    chunk_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
