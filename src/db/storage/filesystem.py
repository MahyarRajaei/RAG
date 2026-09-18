# app/storage/local.py
import uuid
from pathlib import Path

from db.storage.base import FileStorage


class LocalFileStorage(FileStorage):
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, document_id: uuid.UUID, filename: str) -> Path:
        # namespaced by document id to avoid filename collisions entirely
        doc_dir = self.base_dir / str(document_id)
        doc_dir.mkdir(parents=True, exist_ok=True)
        return doc_dir / filename

    def save(self, document_id: uuid.UUID, filename: str, content: bytes) -> str:
        path = self._path_for(document_id, filename)
        path.write_bytes(content)
        return str(path.relative_to(self.base_dir))

    def read(self, storage_path: str) -> bytes:
        full_path = self.base_dir / storage_path
        if not full_path.exists():
            raise FileNotFoundError(storage_path)
        return full_path.read_bytes()

    def delete(self, storage_path: str) -> None:
        full_path = self.base_dir / storage_path
        if full_path.exists():
            full_path.unlink()
            # clean up now-empty document directory
            parent = full_path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
