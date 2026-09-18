from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

import config
from model.chunk import Chunk


class ChunkRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_all(self, chunks: list[Chunk]) -> None:
        self.session.add_all(chunks)

    def delete_by_document_id(self, document_id: UUID) -> None:
        self.session.query(Chunk).filter_by(document_id=document_id).delete()

    def search_by_embedding(
        self,
        query_embedding: list[float],
        top_k: int = config.RETRIEVER_TOP_K,
        document_id: UUID | None = None,
    ) -> list[Chunk]:
        stmt = (
            select(Chunk)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )

        if document_id is not None:
            stmt = stmt.where(Chunk.document_id == document_id)

        return list(self.session.scalars(stmt))
