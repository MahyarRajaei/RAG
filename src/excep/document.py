from uuid import UUID

from excep.base import AppError


class DocumentNotFoundError(AppError):
    """The requested document does not exist."""

    code = "document_not_found"
    status_code = 404

    def __init__(self, document_id: UUID):
        self.document_id = document_id
        super().__init__(f"Document {document_id} not found")


class DuplicateDocumentError(AppError):
    """A document with identical content already exists."""

    code = "duplicate_document"
    status_code = 409

    def __init__(self, existing_document_id: UUID):
        self.existing_document_id = existing_document_id
        super().__init__(f"Document already exists with id {existing_document_id}")


class UnsupportedFileTypeError(AppError):
    """The uploaded file type is not supported."""

    code = "unsupported_file_type"
    status_code = 400

    def __init__(self, suffix: str):
        self.suffix = suffix
        super().__init__(f"Unsupported file type: '{suffix}'")


class EmptyFileError(AppError):
    """The uploaded file is empty."""

    code = "empty_file"
    status_code = 400

    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"File '{filename}' is empty")


class DocumentNotReadyError(AppError):
    """The document exists but is not yet ready for querying."""

    code = "document_not_ready"
    status_code = 409

    def __init__(self, document_id: UUID, status: str):
        self.document_id = document_id
        self.status = status
        super().__init__(f"Document {document_id} is not ready (status={status})")
