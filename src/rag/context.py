# rag/context.py
from dataclasses import dataclass
from uuid import UUID

from model.chunk import Chunk


@dataclass
class ContextBlock:
    label: str
    document_id: UUID
    document_filename: str
    chunk_index: int
    text: str


def build_context(results: list[tuple[Chunk, float]]) -> tuple[str, list[ContextBlock]]:
    blocks = []
    for i, (chunk, _distance, filename) in enumerate(results, start=1):
        blocks.append(
            ContextBlock(
                label=f"[{i}]",
                document_id=chunk.document_id,
                document_filename=filename,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )
        )

    context_str = "\n\n".join(
        f"{b.label} (from {b.document_filename}, section {b.chunk_index}):\n{b.text}"
        for b in blocks
    )
    return context_str, blocks
