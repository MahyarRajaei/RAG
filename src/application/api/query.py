from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from application.api.deps import get_db, get_query_service
from application.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("", response_model=QueryResponse)
def run_query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
):
    query_service = get_query_service(db)
    result = query_service.answer(
        question=payload.question,
        document_ids=payload.document_ids,
    )
    return QueryResponse(**result)
