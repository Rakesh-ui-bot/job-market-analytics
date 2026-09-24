"""
Utility module for applying standard job filters to SQLAlchemy queries.
"""

from typing import Optional
from datetime import date
from sqlalchemy.orm import Query
from sqlalchemy import func, or_
from app.database.models import Job, Location, Skill, JobSkill


def apply_job_filters(
    query: Query,
    role: Optional[str] = None,
    skill: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    remote_type: Optional[str] = None,
    employment_type: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> Query:
    """
    Apply standard filtering criteria to a Job query.

    Returns:
        Query: Filtered SQLAlchemy query object
    """
    if role and role.strip():
        query = query.filter(func.lower(Job.job_title) == role.strip().lower())

    if location and location.strip():
        # Join location if not already joined
        query = query.join(Location, Job.location_id == Location.id).filter(
            or_(
                func.lower(Location.location_name).contains(location.strip().lower()),
                func.lower(Location.country).contains(location.strip().lower())
            )
        )

    if experience_level and experience_level.strip():
        query = query.filter(func.lower(Job.experience_level) == experience_level.strip().lower())

    if remote_type and remote_type.strip():
        query = query.filter(func.lower(Job.remote_type) == remote_type.strip().lower())

    if employment_type and employment_type.strip():
        query = query.filter(func.lower(Job.employment_type) == employment_type.strip().lower())

    if salary_min is not None:
        query = query.filter(Job.salary_min >= salary_min)

    if salary_max is not None:
        query = query.filter(Job.salary_max <= salary_max)

    if date_from is not None:
        query = query.filter(Job.posting_date >= date_from)

    if date_to is not None:
        query = query.filter(Job.posting_date <= date_to)

    if skill and skill.strip():
        query = query.join(JobSkill, Job.id == JobSkill.job_id).join(Skill, Skill.id == JobSkill.skill_id).filter(
            func.lower(Skill.skill_name) == skill.strip().lower()
        )

    return query
