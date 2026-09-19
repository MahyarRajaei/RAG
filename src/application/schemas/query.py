from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[UUID] | None = Field(
        default=None,
        description="Restrict the query to these documents. Omit to search all ready documents.",
    )

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question must not be empty or whitespace only")
        return v.strip()

    @field_validator("document_ids")
    @classmethod
    def document_ids_not_empty_list(cls, v: list[UUID] | None) -> list[UUID] | None:
        if v is not None and len(v) == 0:
            raise ValueError(
                "document_ids must be omitted or non-empty; an empty list matches nothing"
            )
        return v


class SourceItem(BaseModel):
    document_id: UUID
    filename: str
    chunk_index: int


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
