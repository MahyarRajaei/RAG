# rag/graph.py
from typing import TypedDict
from uuid import UUID

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

import config
from rag.context import ContextBlock, build_context
from rag.ingestion.embedding import EmbeddingProvider
from rag.llm import LLMProvider
from rag.schemas import RagAnswer
from repository.chunk_repository import ChunkRepository

SYSTEM_PROMPT = """You are a document Q&A assistant. Answer the question using ONLY \
the numbered context sections provided. Do not use outside knowledge.

Set has_sufficient_context to false if the context does not actually answer the \
question, even if it's topically related — and in that case, set answer to a brief \
statement that there isn't enough information in the documents.

When you do answer, list in used_labels only the section labels (e.g. "[1]") whose \
content you actually relied on."""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)


class QueryState(TypedDict):
    question: str
    document_ids: list[UUID] | None
    top_k: int
    retrieved: list[tuple]  # list[(Chunk, distance)]
    context_blocks: list[ContextBlock]
    result: RagAnswer


def build_query_graph(
    chunk_repository: ChunkRepository,
    embedding_provider: EmbeddingProvider,
    llm_provider: LLMProvider,
):
    structured_llm = llm_provider.client.with_structured_output(RagAnswer)

    def retrieve(state: QueryState) -> QueryState:
        query_embedding = embedding_provider.embed([state["question"]])[0]
        results = chunk_repository.search_by_embedding(
            query_embedding, top_k=state["top_k"], document_ids=state["document_ids"]
        )
        return {**state, "retrieved": results}

    def route_on_relevance(state: QueryState) -> str:
        results = state["retrieved"]
        if not results or results[0][1] < config.MIN_RELEVANCE_THRESHOLD:
            return "insufficient"
        return "generate"

    def generate(state: QueryState) -> QueryState:
        context_str, blocks = build_context(state["retrieved"])
        chain = prompt | structured_llm
        result: RagAnswer = chain.invoke(
            {"context": context_str, "question": state["question"]}
        )
        return {**state, "context_blocks": blocks, "result": result}

    def insufficient(state: QueryState) -> QueryState:
        result = RagAnswer(
            has_sufficient_context=False,
            answer="I don't have enough information in the provided documents to answer this question.",
            used_labels=[],
        )
        return {**state, "context_blocks": [], "result": result}

    graph = StateGraph(QueryState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_node("insufficient", insufficient)

    graph.set_entry_point("retrieve")
    graph.add_conditional_edges(
        "retrieve",
        route_on_relevance,
        {
            "generate": "generate",
            "insufficient": "insufficient",
        },
    )
    graph.add_edge("generate", END)
    graph.add_edge("insufficient", END)

    return graph.compile()
