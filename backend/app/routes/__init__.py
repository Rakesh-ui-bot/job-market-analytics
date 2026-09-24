"""
Routes Package.
"""

from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.analytics import router as analytics_router

__all__ = ["health_router", "jobs_router", "analytics_router"]
