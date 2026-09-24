"""
Analytics API Routes with Dynamic Filtering & Skill Gap Analysis.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_session
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    OverviewMetricsResponse,
    SkillDemandItem,
    SkillGapRequest,
    SkillGapResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewMetricsResponse, summary="Get Overview Metrics with Dynamic Filtering")
def get_overview(
    currency: str = Query("USD", description="Currency code (e.g. USD)"),
    role: Optional[str] = Query(None, description="Filter by job role"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    location: Optional[str] = Query(None, description="Filter by location"),
    experience_level: Optional[str] = Query(None, description="Filter by experience tier"),
    remote_type: Optional[str] = Query(None, description="Filter by remote flexibility"),
    employment_type: Optional[str] = Query(None, description="Filter by contract type"),
    salary_min: Optional[float] = Query(None, description="Minimum salary threshold"),
    salary_max: Optional[float] = Query(None, description="Maximum salary threshold"),
    db: Session = Depends(get_session),
):
    """
    Returns top-level macro metrics dynamically re-calculated against active filters.
    """
    return AnalyticsService.overview(
        db,
        currency=currency,
        role=role,
        skill=skill,
        location=location,
        experience_level=experience_level,
        remote_type=remote_type,
        employment_type=employment_type,
        salary_min=salary_min,
        salary_max=salary_max,
    )


@router.get("/skills", response_model=List[SkillDemandItem], summary="Get Top Demanded Skills")
def get_skills_analytics(
    limit: int = Query(15, ge=1, le=100, description="Top N skills to return"),
    db: Session = Depends(get_session),
):
    """
    Returns top demanded tech skills with market penetration percentages.
    """
    return AnalyticsService.skills(db, limit=limit)


@router.get("/skill-detail", summary="Get Single Skill Deep-Dive Analytics")
def get_single_skill_detail(
    skill: str = Query(..., description="Target skill name (e.g. Python, React)"),
    currency: str = Query("USD", description="Currency code"),
    db: Session = Depends(get_session),
):
    """
    Returns detailed metrics for a single selected skill (job count, market penetration %, avg salary, top roles, top locations, related co-occurring skills).
    """
    return AnalyticsService.skill_detail(db, skill=skill, currency=currency)


@router.get("/role-detail", summary="Get Single Role Deep-Dive Analytics")
def get_single_role_detail(
    role: str = Query(..., description="Target job role name (e.g. Frontend Developer)"),
    currency: str = Query("USD", description="Currency code"),
    db: Session = Depends(get_session),
):
    """
    Returns detailed metrics for a single selected role (job count, required skills, salary bounds, experience distribution, remote %, top locations).
    """
    return AnalyticsService.role_detail(db, role=role, currency=currency)


@router.post("/skill-gap", response_model=SkillGapResponse, summary="Analyze Career Skill Gap")
def analyze_skill_gap(
    payload: SkillGapRequest,
    db: Session = Depends(get_session),
):
    """
    Descriptive career skill gap tool comparing user's current skills against target role requirements.
    NOTE: Does NOT predict hiring probability or make placement claims.
    """
    return AnalyticsService.skill_gap(
        db, target_role=payload.target_role, user_skills=payload.user_skills
    )


@router.get("/skills-by-role", summary="Get Skills Filtered by Role")
def get_skills_by_role_analytics(
    role: Optional[str] = Query(None, description="Job role filter (e.g. Frontend Developer)"),
    limit: int = Query(10, ge=1, le=50, description="Top N skills to return"),
    db: Session = Depends(get_session),
):
    """
    Returns top skills required for a specific job role or across all roles.
    """
    return AnalyticsService.skills_by_role(db, role=role, limit=limit)


@router.get("/skills-by-location", summary="Get Skills Filtered by Location")
def get_skills_by_location_analytics(
    location: Optional[str] = Query(None, description="Location filter (e.g. New York, NY)"),
    limit: int = Query(10, ge=1, le=50, description="Top N skills to return"),
    db: Session = Depends(get_session),
):
    """
    Returns top skills required in a specific city/location.
    """
    return AnalyticsService.skills_by_location(db, location=location, limit=limit)


@router.get("/roles", summary="Get Role Distribution & Salary per Role")
def get_roles_analytics(
    limit: int = Query(10, ge=1, le=50, description="Top N roles"),
    db: Session = Depends(get_session),
):
    """
    Returns most common job roles and job volume breakdown.
    """
    return AnalyticsService.roles(db, limit=limit)


@router.get("/locations", summary="Get Jobs per City & Country")
def get_locations_analytics(
    limit: int = Query(15, ge=1, le=50, description="Top N cities"),
    db: Session = Depends(get_session),
):
    """
    Returns job volume distribution across cities and countries.
    """
    return AnalyticsService.locations(db, limit=limit)


@router.get("/salary", summary="Get Salary Statistical Summary & Comparisons")
def get_salary_analytics(
    currency: str = Query("USD", description="Currency code (e.g. USD)"),
    db: Session = Depends(get_session),
):
    """
    Returns summary salary statistics (avg, median, min, max, percentiles, std dev) and breakdowns by role, experience, and location.
    """
    return AnalyticsService.salary(db, currency=currency)


@router.get("/experience", summary="Get Experience Level Distribution")
def get_experience_analytics(db: Session = Depends(get_session)):
    """
    Returns job distribution across experience tiers.
    """
    return AnalyticsService.experience(db)


@router.get("/remote", summary="Get Remote Flexibility Distribution & Salary Comparison")
def get_remote_analytics(
    currency: str = Query("USD", description="Currency code"),
    db: Session = Depends(get_session),
):
    """
    Returns market share and salary comparisons for Remote, Hybrid, and On-site roles.
    """
    return AnalyticsService.remote(db, currency=currency)
