# service/query_service.py
from uuid import UUID

import config
from rag.graph import build_query_graph


class QueryService:
    def __init__(self, chunk_repository, embedding_provider, llm_provider):
        self.graph = build_query_graph(
            chunk_repository, embedding_provider, llm_provider
        )

    def answer(
        self,
        question: str,
        document_ids: list[UUID] | None = None,
        top_k: int = config.RETRIEVER_TOP_K,
    ) -> dict:
        final_state = self.graph.invoke(
            {
                "question": question,
                "document_ids": document_ids,
                "top_k": top_k,
                "retrieved": [],
                "context_blocks": [],
                "result": None,
            }
        )

        result = final_state["result"]
        blocks = final_state["context_blocks"]

        used_blocks = (
            [b for b in blocks if b.label in result.used_labels]
            if result.has_sufficient_context
            else []
        )

        return {
            "answer": result.answer,
            "sources": [
                {
                    "document_id": str(b.document_id),
                    "filename": b.document_filename,
                    "chunk_index": b.chunk_index,
                }
                for b in used_blocks
            ],
        }
