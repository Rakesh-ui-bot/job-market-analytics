"""
FastAPI Main Application Entry Point.

Exposes REST API endpoints for job market analytics, skills demand, compensation benchmarks,
and job posting search with filtering and pagination.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.routes import health_router, jobs_router, analytics_router
from app.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown."""
    try:
        init_db()
    except Exception as e:
        print(f"Startup DB init notification: {e}")
    yield


app = FastAPI(
    title="Job Market Analytics & Skill Demand Analyzer API",
    description=(
        "REST API providing real-time tech job market insights, skill demand analysis, "
        "salary benchmarks, remote work trends, and filtered job search."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev and React integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root path to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected backend errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected internal server error occurred.",
            "detail": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
