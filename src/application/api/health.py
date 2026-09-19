from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from application.api.deps import get_db

router = APIRouter()


@router.get("/health")
def health():
    """Liveness: is the process up. Always 200 if the server can respond at all."""
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    """Readiness: can we actually serve traffic — DB reachable."""
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    status = "ok" if db_ok else "degraded"
    return {
        "status": status,
        "dependencies": {"database": "ok" if db_ok else "unreachable"},
    }
