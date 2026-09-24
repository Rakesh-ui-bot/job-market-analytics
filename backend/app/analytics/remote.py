"""
Remote Work Analytics Module.

Analyzes remote flexibility trends across job postings:
- Remote
- Hybrid
- On-site
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Job


def get_remote_work_distribution(db: Session) -> List[Dict[str, Any]]:
    """Get job volume and market share per remote work type."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 1
    results = (
        db.query(
            Job.remote_type,
            func.count(Job.id).label("job_count")
        )
        .group_by(Job.remote_type)
        .order_by(desc("job_count"))
        .all()
    )

    return [
        {
            "remote_type": row.remote_type,
            "job_count": row.job_count,
            "percentage": round((row.job_count / total_jobs) * 100, 2),
        }
        for row in results
    ]


def get_remote_by_role(db: Session) -> List[Dict[str, Any]]:
    """Get remote work flexibility distribution broken down by job role."""
    results = (
        db.query(
            Job.job_title,
            Job.remote_type,
            func.count(Job.id).label("job_count")
        )
        .group_by(Job.job_title, Job.remote_type)
        .order_by(Job.job_title, desc("job_count"))
        .all()
    )

    return [
        {
            "job_title": row.job_title,
            "remote_type": row.remote_type,
            "job_count": row.job_count,
        }
        for row in results
    ]


def get_remote_salary_comparison(
    db: Session, currency: str = "USD"
) -> List[Dict[str, Any]]:
    """Compare average salaries across Remote, Hybrid, and On-site positions."""
    results = (
        db.query(
            Job.remote_type,
            func.count(Job.id).label("job_count"),
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
            func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_midpoint")
        )
        .filter(Job.salary_currency == currency)
        .group_by(Job.remote_type)
        .order_by(desc("avg_midpoint"))
        .all()
    )

    return [
        {
            "remote_type": row.remote_type,
            "job_count": row.job_count,
            "avg_salary_min": round(float(row.avg_min or 0), 2),
            "avg_salary_max": round(float(row.avg_max or 0), 2),
            "avg_midpoint_salary": round(float(row.avg_midpoint or 0), 2),
        }
        for row in results
    ]
