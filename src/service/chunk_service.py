import logging
from uuid import UUID

from sqlalchemy.orm import Session

from excep import DocumentNotFoundError
from model.chunk import Chunk
from rag.ingestion.chunking import TextChunk
from repository.chunk_repository import ChunkRepository
from repository.document_repository import DocumentRepository

logger = logging.getLogger("adan.chunks")


class ChunkService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ChunkRepository(session)
        self.document_repository = DocumentRepository(session)

    def replace_chunks(
        self,
        document_id: UUID,
        text_chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> list[Chunk]:
        if len(text_chunks) != len(embeddings):
            raise ValueError(
                f"text_chunks ({len(text_chunks)}) and embeddings ({len(embeddings)}) "
                "must be the same length"
            )

        self.repository.delete_by_document_id(document_id)

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
        self.repository.add_all(chunk_rows)

        logger.info(
            "chunks_replaced",
            extra={"document_id": str(document_id), "chunk_count": len(chunk_rows)},
        )
        return chunk_rows

    def delete_chunks_for_document(self, document_id: UUID) -> None:
        self.repository.delete_by_document_id(document_id)
        logger.info("chunks_deleted", extra={"document_id": str(document_id)})

    def list_chunks_for_document(self, document_id: UUID) -> list[Chunk]:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return self.repository.list_by_document_id(document_id)

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        document_ids: list[UUID] | None = None,
    ) -> list[tuple[Chunk, str, float]]:
        return self.repository.search_by_embedding(
            query_embedding, top_k=top_k, document_ids=document_ids
        )
