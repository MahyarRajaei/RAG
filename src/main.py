# main.py
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from application.api import documents, health, query
from excep.document import (
    DocumentNotFoundError,
    DuplicateDocumentError,
    EmptyFileError,
    UnsupportedFileTypeError,
)
from excep.query import GenerationError, QueryError, RetrievalError

logger = logging.getLogger("adan.api")

app = FastAPI(title="Adan RAG Backend")

app.include_router(health.router)
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(query.router, prefix="/query", tags=["query"])


@app.get("/")
def read_root():
    return FileResponse("index.html")


def _error(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.info(
        "validation_error", extra={"path": str(request.url), "errors": exc.errors()}
    )
    return _error("VALIDATION_ERROR", "Request validation failed.", 422)


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request: Request, exc: DocumentNotFoundError):
    return _error("DOCUMENT_NOT_FOUND", str(exc), 404)


@app.exception_handler(UnsupportedFileTypeError)
async def unsupported_file_type_handler(
    request: Request, exc: UnsupportedFileTypeError
):
    return _error("UNSUPPORTED_FILE_TYPE", str(exc), 415)


@app.exception_handler(EmptyFileError)
async def empty_file_handler(request: Request, exc: EmptyFileError):
    return _error("EMPTY_FILE", str(exc), 400)


@app.exception_handler(DuplicateDocumentError)
async def duplicate_document_handler(request: Request, exc: DuplicateDocumentError):
    return _error("DUPLICATE_DOCUMENT", str(exc), 409)


# @app.exception_handler(DocumentError)
# async def document_error_handler(request: Request, exc: DocumentError):
#     logger.warning("document_error", extra={"path": str(request.url)}, exc_info=True)
#     return _error("DOCUMENT_ERROR", str(exc), 400)


@app.exception_handler(RetrievalError)
async def retrieval_error_handler(request: Request, exc: RetrievalError):
    logger.error("retrieval_error", extra={"path": str(request.url)}, exc_info=True)
    return _error("RETRIEVAL_FAILED", "Failed to retrieve relevant context.", 502)


@app.exception_handler(GenerationError)
async def generation_error_handler(request: Request, exc: GenerationError):
    logger.error("generation_error", extra={"path": str(request.url)}, exc_info=True)
    return _error("GENERATION_FAILED", "Failed to generate an answer.", 502)


@app.exception_handler(QueryError)
async def query_error_handler(request: Request, exc: QueryError):
    logger.error("query_error", extra={"path": str(request.url)}, exc_info=True)
    return _error("QUERY_ERROR", "Failed to process the query.", 502)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_error", extra={"path": str(request.url)})
    return _error("INTERNAL_ERROR", "An unexpected error occurred.", 500)
