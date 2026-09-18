import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.chunk import EMBEDDING_DIM, Chunk
from src.model.document import Document, DocumentStatus, MIMEType
from src.service.document_service import DocumentService


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def test_markdown_files_exist(sample_md_files: list[Path]):
    """Verify that multiple .md files exist as documents."""
    assert len(sample_md_files) >= 3
    for file_path in sample_md_files:
        assert file_path.suffix == ".md"
        assert file_path.stat().st_size > 0


def test_insert_single_markdown_document_direct(
    db_session: Session, sample_md_files: list[Path]
):
    """Test inserting a markdown document directly into the document table."""
    md_file = sample_md_files[0]
    content = md_file.read_bytes()
    file_hash = compute_sha256(content)

    doc = Document(
        filename=md_file.name,
        file_hash=file_hash,
        content_hash=file_hash,
        file_type=MIMEType.MARKDOWN,
        file_size_bytes=len(content),
        status=DocumentStatus.PENDING,
        chunk_count=0,
    )
    db_session.add(doc)
    db_session.commit()

    # Query back from table
    queried = db_session.scalar(select(Document).where(Document.id == doc.id))
    assert queried is not None
    assert queried.filename == md_file.name
    assert queried.file_hash == file_hash
    assert queried.content_hash == file_hash
    assert queried.file_type == MIMEType.MARKDOWN
    assert queried.file_size_bytes == len(content)
    assert queried.status == DocumentStatus.PENDING
    assert queried.created_at is not None
    assert queried.updated_at is not None


def test_insert_multiple_markdown_documents_via_service(
    db_session: Session, sample_md_files: list[Path]
):
    """Test inserting multiple .md documents into the document table via service."""
    service = DocumentService(db_session)
    inserted_docs = []

    for file_path in sample_md_files:
        doc = service.insert_from_file(file_path, status=DocumentStatus.READY)
        db_session.commit()
        inserted_docs.append(doc)

    assert len(inserted_docs) == len(sample_md_files)

    # Verify each document exists in the database table
    for doc, file_path in zip(inserted_docs, sample_md_files):
        stored = db_session.scalar(select(Document).where(Document.id == doc.id))
        assert stored is not None
        assert stored.filename == file_path.name
        assert stored.file_type == MIMEType.MARKDOWN
        assert stored.status == DocumentStatus.READY
        assert stored.file_size_bytes == file_path.stat().st_size
        assert len(stored.file_hash) == 64


def test_duplicate_document_handling(db_session: Session, sample_md_files: list[Path]):
    """Test that inserting the same markdown document twice returns the existing record."""
    service = DocumentService(db_session)
    target_file = sample_md_files[0]

    doc1 = service.insert_from_file(target_file)
    db_session.commit()

    doc2 = service.insert_from_file(target_file)
    db_session.commit()

    assert doc1.id == doc2.id
    assert doc1.file_hash == doc2.file_hash


def test_insert_document_with_chunks(db_session: Session, sample_md_files: list[Path]):
    """Test inserting a document with associated chunks and pgvector embeddings."""
    service = DocumentService(db_session)
    doc = service.insert_from_file(sample_md_files[0])
    db_session.commit()

    chunk = Chunk(
        document_id=doc.id,
        chunk_index=0,
        text="Retrieval-Augmented Generation enhances Large Language Model responses.",
        token_count=10,
        embedding=[0.05] * EMBEDDING_DIM,
    )
    db_session.add(chunk)
    doc.chunk_count = 1
    db_session.commit()

    queried_doc = db_session.scalar(select(Document).where(Document.id == doc.id))
    assert queried_doc is not None
    assert len(queried_doc.chunks) == 1
    assert queried_doc.chunks[0].chunk_index == 0
    assert len(queried_doc.chunks[0].embedding) == EMBEDDING_DIM
