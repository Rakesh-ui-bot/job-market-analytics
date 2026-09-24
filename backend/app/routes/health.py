"""
Health Check API Route.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_session

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="API Health Check")
def health_check(db: Session = Depends(get_session)):
    """
    Returns API status, version, and verifies database connectivity.
    """
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "app_name": "Job Market Analytics & Skill Demand Analyzer",
        "version": "1.0.0",
        "database_status": db_status,
    }
