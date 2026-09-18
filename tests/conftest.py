from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.db.session import Base, SessionLocal, engine
from src.model import Chunk, Document


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def clean_tables(db_session: Session):
    db_session.execute(text("TRUNCATE TABLE chunk, document RESTART IDENTITY CASCADE;"))
    db_session.commit()
    yield
    db_session.execute(text("TRUNCATE TABLE chunk, document RESTART IDENTITY CASCADE;"))
    db_session.commit()


@pytest.fixture
def sample_md_files() -> list[Path]:
    docs_dir = Path(__file__).resolve().parent.parent / "documents"
    md_files = sorted(list(docs_dir.glob("*.md")))
    assert len(md_files) > 0, "No markdown files found in documents/ directory."
    return md_files
