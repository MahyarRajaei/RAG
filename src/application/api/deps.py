from collections.abc import Generator

from sqlalchemy.orm import Session

from db.session import SessionLocal  # adjust to your actual session factory
from db.storage.base import FileStorage
from db.storage.filesystem import (
    LocalFileStorage,  # or whatever concrete impl you're using
)
from rag.ingestion.embedding import LangChainEmbeddingProvider
from rag.llm import LLMProvider
from repository.chunk_repository import ChunkRepository
from repository.document_repository import DocumentRepository
from service.ingestion_pipeline import IngestionPipeline
from service.query_service import QueryService

_embedding_provider = LangChainEmbeddingProvider()
_llm_provider = LLMProvider()
_storage: FileStorage = LocalFileStorage()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_storage() -> FileStorage:
    return _storage


def get_document_repository(db: Session = None) -> DocumentRepository:
    return DocumentRepository(db)


def get_ingestion_pipeline(db: Session) -> IngestionPipeline:
    return IngestionPipeline(db, _storage, _embedding_provider)


def get_query_service(db: Session) -> QueryService:
    return QueryService(ChunkRepository(db), _embedding_provider, _llm_provider)
