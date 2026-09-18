import tempfile
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

import config
from db.storage.base import FileStorage
from excep.document import DocumentNotFoundError
from model.chunk import Chunk
from model.document import DocumentStatus
from rag.ingestion.chunking import chunk_text
from rag.ingestion.embedding import EmbeddingProvider
from rag.ingestion.extraction import extract_text
from repository.chunk_repository import ChunkRepository
from repository.document_repository import DocumentRepository


class IngestionPipeline:
    def __init__(
        self,
        session: Session,
        storage: FileStorage,
        embedding_provider: EmbeddingProvider,
    ):
        self.session = session
        self.storage = storage
        self.embedding_provider = embedding_provider
        self.document_repository = DocumentRepository(session)
        self.chunk_repository = ChunkRepository(session)

    def process(self, document_id: UUID) -> None:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        try:
            document.status = DocumentStatus.PROCESSING
            document.status_reason = None
            self.session.commit()

            raw_bytes = self.storage.read(document.storage_path)
            text = self._extract(raw_bytes, document.filename, document.file_type)
            text_chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

            if not text_chunks:
                raise ValueError("No chunks produced from document text")

            embeddings = self.embedding_provider.embed([c.text for c in text_chunks])

            self.chunk_repository.delete_by_document_id(document_id)
            chunk_rows = [
                Chunk(
                    document_id=document_id,
                    chunk_index=tc.index,
                    text=tc.text,
                    token_count=tc.token_count,
                    embedding=emb,
                )
                for tc, emb in zip(text_chunks, embeddings)
            ]
            self.chunk_repository.add_all(chunk_rows)

            document.status = DocumentStatus.READY
            document.chunk_count = len(chunk_rows)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            document.status = DocumentStatus.FAILED
            document.status_reason = str(e)[:1000]  # bound the length for the DB column
            self.session.commit()
            # re-raise so the caller (background task runner / logger) knows it failed
            raise

    def _extract(self, raw_bytes: bytes, filename: str, file_type) -> str:
        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(raw_bytes)
            tmp.flush()
            return extract_text(Path(tmp.name), file_type)
