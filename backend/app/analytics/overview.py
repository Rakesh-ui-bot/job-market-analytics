"""
Overview Analytics Module.

Calculates top-level macro metrics for the dashboard with dynamic filter support:
- Total job postings count
- Total unique companies
- Total unique locations
- Total unique tech skills
- Remote job percentage
- Average salary bounds and overall midpoint
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.database.models import Job, Company, Location, Skill, JobSkill
from app.utils.filter_utils import apply_job_filters


def get_overview_metrics(
    db: Session,
    currency: str = "USD",
    role: Optional[str] = None,
    skill: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    remote_type: Optional[str] = None,
    employment_type: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute macro overview metrics with dynamic filters.
    """
    # 1. Base Filtered Job Subquery IDs
    job_query = db.query(Job.id)
    job_query = apply_job_filters(
        job_query,
        role=role,
        skill=skill,
        location=location,
        experience_level=experience_level,
        remote_type=remote_type,
        employment_type=employment_type,
        salary_min=salary_min,
        salary_max=salary_max,
    )
    filtered_job_ids_select = select(job_query.distinct().subquery().c.id)

    total_jobs = db.scalar(select(func.count()).select_from(filtered_job_ids_select.subquery())) or 0

    # 2. Filtered Companies
    total_companies = (
        db.query(func.count(func.distinct(Job.company_id)))
        .filter(Job.id.in_(filtered_job_ids_select))
        .scalar() or 0
    )

    # 3. Filtered Locations
    total_locations = (
        db.query(func.count(func.distinct(Job.location_id)))
        .filter(Job.id.in_(filtered_job_ids_select))
        .scalar() or 0
    )

    # 4. Filtered Unique Skills
    total_skills = (
        db.query(func.count(func.distinct(JobSkill.skill_id)))
        .filter(JobSkill.job_id.in_(filtered_job_ids_select))
        .scalar() or 0
    )

    # 5. Remote Jobs Percentage
    remote_jobs = (
        db.query(func.count(Job.id))
        .filter(Job.id.in_(filtered_job_ids_select))
        .filter(Job.remote_type.in_(["Remote", "Full Remote"]))
        .scalar() or 0
    )
    remote_percentage = round((remote_jobs / total_jobs) * 100, 2) if total_jobs > 0 else 0.0

    # 6. Average Salary
    salary_res = (
        db.query(
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
            func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid")
        )
        .filter(Job.id.in_(filtered_job_ids_select))
        .filter(Job.salary_currency == currency)
        .first()
    )

    avg_min = round(float(salary_res.avg_min or 0), 2) if salary_res and salary_res.avg_min else 0.0
    avg_max = round(float(salary_res.avg_max or 0), 2) if salary_res and salary_res.avg_max else 0.0
    avg_mid = round(float(salary_res.avg_mid or 0), 2) if salary_res and salary_res.avg_mid else 0.0

    return {
        "total_jobs": total_jobs,
        "total_companies": total_companies,
        "total_locations": total_locations,
        "total_unique_skills": total_skills,
        "remote_jobs_count": remote_jobs,
        "remote_job_percentage": remote_percentage,
        "average_salary": {
            "currency": currency,
            "min": avg_min,
            "max": avg_max,
            "midpoint": avg_mid,
        },
    }
