from abc import ABC, abstractmethod

from langchain_openai import OpenAIEmbeddings

import config


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def dimension(self) -> int: ...


class LangChainEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        model: str = config.EMBEDDING_MODEL,
        api_key: str | None = config.API_KEY,
    ):
        self._client = OpenAIEmbeddings(
            base_url=config.BASE_URL,
            model=model,
            api_key=api_key,
            check_embedding_ctx_length=False,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._client.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._client.embed_query(text)

    @property
    def dimension(self) -> int:
        return self._dimension
