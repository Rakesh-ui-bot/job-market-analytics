"""
Experience Level Analytics Module.

Analyzes job market distributions across experience tiers:
- Entry-level
- Junior
- Mid-level
- Senior
- Lead / Executive
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Job
from app.analytics.salary import get_salary_by_experience


def get_experience_level_distribution(db: Session) -> List[Dict[str, Any]]:
    """Get job post counts and market share percentages per experience tier."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 1
    results = (
        db.query(
            Job.experience_level,
            func.count(Job.id).label("job_count")
        )
        .group_by(Job.experience_level)
        .order_by(desc("job_count"))
        .all()
    )

    return [
        {
            "experience_level": row.experience_level,
            "job_count": row.job_count,
            "percentage": round((row.job_count / total_jobs) * 100, 2),
        }
        for row in results
    ]


def get_role_distribution_by_experience(db: Session) -> List[Dict[str, Any]]:
    """Get Breakdown of job titles across experience tiers."""
    results = (
        db.query(
            Job.experience_level,
            Job.job_title,
            func.count(Job.id).label("job_count")
        )
        .group_by(Job.experience_level, Job.job_title)
        .order_by(Job.experience_level, desc("job_count"))
        .all()
    )

    return [
        {
            "experience_level": row.experience_level,
            "job_title": row.job_title,
            "job_count": row.job_count,
        }
        for row in results
    ]
