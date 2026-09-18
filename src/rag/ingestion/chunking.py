from dataclasses import dataclass

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

_ENCODING = tiktoken.get_encoding("cl100k_base")


@dataclass
class TextChunk:
    index: int
    text: str
    token_count: int


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[TextChunk]:
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )
    raw_chunks = splitter.split_text(text)

    return [
        TextChunk(
            index=i,
            text=chunk,
            token_count=len(_ENCODING.encode(chunk)),
        )
        for i, chunk in enumerate(raw_chunks)
    ]
