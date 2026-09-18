# rag/schemas.py
from pydantic import BaseModel, Field


class RagAnswer(BaseModel):
    has_sufficient_context: bool = Field(
        description="True only if the provided context actually answers the question."
    )
    answer: str = Field(
        description="The answer, or a brief refusal message if context is insufficient."
    )
    used_labels: list[str] = Field(
        default_factory=list,
        description="Labels (e.g. '[1]', '[2]') of context sections actually used to answer.",
    )
