from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

import config
from model import Chunk, Document, DocumentStatus


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
        document_ids: list[UUID] | None = None,
    ) -> list[tuple[Chunk, float]]:
        distance_col = Chunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(Chunk, Document.filename, distance_col.label("distance"))
            .join(Document, Chunk.document_id == Document.id)
            .where(Document.status == DocumentStatus.READY)
            .order_by(distance_col)
            .limit(top_k)
        )
        if document_ids is not None:
            stmt = stmt.where(Chunk.document_id.in_(document_ids))

        return [
            (row.Chunk, row.distance, row.filename)
            for row in self.session.execute(stmt)
        ]
