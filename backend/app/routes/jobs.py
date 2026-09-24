"""
Jobs API Routes.
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.connection import get_session
from app.services.job_service import JobService
from app.schemas.jobs import PaginatedJobsResponse, JobDetailSchema

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=PaginatedJobsResponse, summary="Get Paginated & Filtered Jobs")
def get_jobs(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    role: Optional[str] = Query(None, description="Filter by job role (e.g. Frontend Developer)"),
    skill: Optional[str] = Query(None, description="Filter by required tech skill (e.g. Python)"),
    location: Optional[str] = Query(None, description="Filter by city or country (e.g. New York)"),
    experience_level: Optional[str] = Query(None, description="Filter by experience tier (e.g. Senior)"),
    remote_type: Optional[str] = Query(None, description="Filter by work flexibility (e.g. Remote)"),
    employment_type: Optional[str] = Query(None, description="Filter by contract type (e.g. Full-time)"),
    salary_min: Optional[float] = Query(None, description="Minimum salary threshold"),
    salary_max: Optional[float] = Query(None, description="Maximum salary threshold"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
):
    """
    Retrieve job postings with dynamic multi-field filtering and pagination.
    """
    return JobService.get_jobs(
        db=db,
        page=page,
        limit=limit,
        role=role,
        skill=skill,
        location=location,
        experience_level=experience_level,
        remote_type=remote_type,
        employment_type=employment_type,
        salary_min=salary_min,
        salary_max=salary_max,
        date_from=date_from,
        date_to=date_to,
    )


@router.post("/upload", summary="Upload & Ingest CSV Dataset")
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
):
    """
    Upload a CSV file of job postings.
    Workflow: Upload -> Validate Schema -> Clean -> Extract Skills -> Ingest into DB -> Refresh Analytics.
    """
    return JobService.process_csv_upload(db=db, file=file)


@router.get("/{id}", response_model=JobDetailSchema, summary="Get Single Job Detail")
def get_job_by_id(id: str, db: Session = Depends(get_session)):
    """
    Retrieve full detailed job posting record by integer ID or string job_id (e.g. JOB-10001).
    """
    job = JobService.get_job_by_identifier(db=db, identifier=id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job post with identifier '{id}' was not found.",
        )
    return job
