"""
Role/Job Title Analytics Module.

Calculates common job roles, jobs per role, skills per role, salary metrics per role,
and single role deep-dive analytics.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select
from app.database.models import Job, Skill, JobSkill, Location


def get_most_common_roles(db: Session, top_n: int = 10) -> List[Dict[str, Any]]:
    """Get top most common job roles."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 1
    results = (
        db.query(
            Job.job_title,
            func.count(Job.id).label("job_count")
        )
        .group_by(Job.job_title)
        .order_by(desc("job_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "job_title": row.job_title,
            "job_count": row.job_count,
            "percentage": round((row.job_count / total_jobs) * 100, 2),
        }
        for row in results
    ]


def get_jobs_per_role(db: Session) -> List[Dict[str, Any]]:
    """Get total jobs count grouped by role."""
    return get_most_common_roles(db, top_n=100)


def get_skills_per_role(
    db: Session, role_name: str, top_n: int = 10
) -> List[Dict[str, Any]]:
    """Get top required skills for a specific job role."""
    role_job_count = (
        db.query(func.count(Job.id))
        .filter(func.lower(Job.job_title) == role_name.strip().lower())
        .scalar() or 1
    )

    results = (
        db.query(
            Skill.skill_name,
            func.count(JobSkill.job_id).label("skill_count")
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .join(Job, Job.id == JobSkill.job_id)
        .filter(func.lower(Job.job_title) == role_name.strip().lower())
        .group_by(Skill.id, Skill.skill_name)
        .order_by(desc("skill_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "role": role_name,
            "skill_name": row.skill_name,
            "count": row.skill_count,
            "percentage": round((row.skill_count / role_job_count) * 100, 2),
        }
        for row in results
    ]


def get_salary_per_role(db: Session, currency: str = "USD") -> List[Dict[str, Any]]:
    """Get salary analytics metrics grouped by job role."""
    results = (
        db.query(
            Job.job_title,
            func.count(Job.id).label("job_count"),
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
            func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_midpoint"),
            func.min(Job.salary_min).label("min_salary"),
            func.max(Job.salary_max).label("max_salary")
        )
        .filter(Job.salary_currency == currency)
        .group_by(Job.job_title)
        .order_by(desc("avg_midpoint"))
        .all()
    )

    return [
        {
            "job_title": row.job_title,
            "job_count": row.job_count,
            "avg_salary_min": round(float(row.avg_min or 0), 2),
            "avg_salary_max": round(float(row.avg_max or 0), 2),
            "avg_midpoint_salary": round(float(row.avg_midpoint or 0), 2),
            "min_salary": round(float(row.min_salary or 0), 2),
            "max_salary": round(float(row.max_salary or 0), 2),
        }
        for row in results
    ]


def get_role_detail_analytics(
    db: Session, role_name: str, currency: str = "USD"
) -> Dict[str, Any]:
    """
    Get detailed analytics breakdown for a single role:
    - job_count
    - required_skills
    - salary (avg_min, avg_max, midpoint)
    - experience_distribution
    - remote_percentage
    - top_locations
    """
    query_role = func.lower(Job.job_title) == role_name.strip().lower()
    total_role_jobs = db.query(func.count(Job.id)).filter(query_role).scalar() or 0

    if total_role_jobs == 0:
        return {}

    # 1. Salary metrics
    salary_res = (
        db.query(
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
            func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid")
        )
        .filter(query_role)
        .filter(Job.salary_currency == currency)
        .first()
    )

    avg_min = round(float(salary_res.avg_min or 0), 2) if salary_res and salary_res.avg_min else 0.0
    avg_max = round(float(salary_res.avg_max or 0), 2) if salary_res and salary_res.avg_max else 0.0
    avg_mid = round(float(salary_res.avg_mid or 0), 2) if salary_res and salary_res.avg_mid else 0.0

    # 2. Remote percentage for role
    remote_jobs = (
        db.query(func.count(Job.id))
        .filter(query_role)
        .filter(Job.remote_type.in_(["Remote", "Full Remote"]))
        .scalar() or 0
    )
    remote_pct = round((remote_jobs / total_role_jobs) * 100, 2)

    # 3. Required skills
    required_skills = get_skills_per_role(db, role_name=role_name, top_n=10)

    # 4. Experience distribution
    exp_dist = (
        db.query(Job.experience_level, func.count(Job.id).label("count"))
        .filter(query_role)
        .group_by(Job.experience_level)
        .order_by(desc("count"))
        .all()
    )

    # 5. Top locations
    top_locs = (
        db.query(Location.location_name, Location.country, func.count(Job.id).label("count"))
        .join(Job, Location.id == Job.location_id)
        .filter(query_role)
        .group_by(Location.location_name, Location.country)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    return {
        "job_title": role_name,
        "job_count": total_role_jobs,
        "remote_percentage": remote_pct,
        "salary": {
            "currency": currency,
            "avg_min": avg_min,
            "avg_max": avg_max,
            "avg_midpoint": avg_mid,
        },
        "required_skills": required_skills,
        "experience_distribution": [{"experience_level": e.experience_level, "count": e.count} for e in exp_dist],
        "top_locations": [{"location_name": l.location_name, "country": l.country, "count": l.count} for l in top_locs],
    }
