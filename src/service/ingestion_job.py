# src/service/ingestion_jobs.py
import logging
from uuid import UUID

from db.session import SessionLocal
from db.storage.filesystem import LocalFileStorage
from rag.ingestion.embedding import LangChainEmbeddingProvider
from service.ingestion_pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

# One provider instance per worker process, not per job — same reasoning as your
# API's dependency setup: these wrap HTTP clients, no need to recreate them per call.
_storage = LocalFileStorage()
_embedding_provider = LangChainEmbeddingProvider()


def process_document_job(document_id: UUID | str) -> None:
    """Entry point enqueued via RQ. Owns its own DB session since it runs in a
    separate worker process with no access to the request-scoped session that
    enqueued it."""
    if isinstance(document_id, str):
        document_id = UUID(document_id)

    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db, _storage, _embedding_provider)
        pipeline.process(document_id)
    except Exception:
        logger.exception(
            "ingestion_job_failed", extra={"document_id": str(document_id)}
        )
        raise
    finally:
        db.close()
