"""
Location Analytics Module.

Calculates job density per city/country, location-specific skill demand,
and remote job distribution by location.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Job, Location, Skill, JobSkill


def get_jobs_per_city(db: Session, top_n: int = 15) -> List[Dict[str, Any]]:
    """Get job volume distribution per city/location."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 1
    results = (
        db.query(
            Location.location_name,
            Location.country,
            func.count(Job.id).label("job_count")
        )
        .join(Job, Location.id == Job.location_id)
        .group_by(Location.id, Location.location_name, Location.country)
        .order_by(desc("job_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "location_name": row.location_name,
            "country": row.country,
            "job_count": row.job_count,
            "percentage": round((row.job_count / total_jobs) * 100, 2),
        }
        for row in results
    ]


def get_jobs_per_country(db: Session) -> List[Dict[str, Any]]:
    """Get job volume distribution per country."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 1
    results = (
        db.query(
            Location.country,
            func.count(Job.id).label("job_count")
        )
        .join(Job, Location.id == Job.location_id)
        .group_by(Location.country)
        .order_by(desc("job_count"))
        .all()
    )

    return [
        {
            "country": row.country,
            "job_count": row.job_count,
            "percentage": round((row.job_count / total_jobs) * 100, 2),
        }
        for row in results
    ]


def get_skills_per_location(
    db: Session, location_name: str, top_n: int = 10
) -> List[Dict[str, Any]]:
    """Get top in-demand skills for a specific location."""
    loc_job_count = (
        db.query(func.count(Job.id))
        .join(Location, Location.id == Job.location_id)
        .filter(func.lower(Location.location_name) == location_name.strip().lower())
        .scalar() or 1
    )

    results = (
        db.query(
            Skill.skill_name,
            func.count(JobSkill.job_id).label("skill_count")
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .join(Job, Job.id == JobSkill.job_id)
        .join(Location, Location.id == Job.location_id)
        .filter(func.lower(Location.location_name) == location_name.strip().lower())
        .group_by(Skill.id, Skill.skill_name)
        .order_by(desc("skill_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "location_name": location_name,
            "skill_name": row.skill_name,
            "count": row.skill_count,
            "percentage": round((row.skill_count / loc_job_count) * 100, 2),
        }
        for row in results
    ]


def get_remote_jobs_by_location(db: Session) -> List[Dict[str, Any]]:
    """Get count of remote vs hybrid vs on-site jobs grouped by location."""
    results = (
        db.query(
            Location.location_name,
            Location.country,
            Job.remote_type,
            func.count(Job.id).label("job_count")
        )
        .join(Job, Location.id == Job.location_id)
        .group_by(Location.location_name, Location.country, Job.remote_type)
        .order_by(Location.location_name, desc("job_count"))
        .all()
    )

    return [
        {
            "location_name": row.location_name,
            "country": row.country,
            "remote_type": row.remote_type,
            "job_count": row.job_count,
        }
        for row in results
    ]
