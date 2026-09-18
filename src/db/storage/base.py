# app/storage/base.py
import uuid
from abc import ABC, abstractmethod


class FileStorage(ABC):
    @abstractmethod
    def save(self, document_id: uuid.UUID, filename: str, content: bytes) -> str:
        """Persist the file, return a storage-relative path/key."""

    @abstractmethod
    def read(self, storage_path: str) -> bytes:
        """Retrieve raw file bytes."""

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        """Remove the file."""
