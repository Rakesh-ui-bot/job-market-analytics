"""
Skill Analytics Module.

Calculates skill demand, market penetration percentages, role-specific skills,
location-specific skills, skill co-occurrence (related skills), and single skill detail analytics.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select
from app.database.models import Job, Skill, JobSkill, Location


def get_most_demanded_skills(db: Session, top_n: int = 15) -> List[Dict[str, Any]]:
    """Get top N most demanded tech skills by total job count."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 1
    results = (
        db.query(
            Skill.skill_name,
            func.count(JobSkill.job_id).label("job_count")
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .group_by(Skill.id, Skill.skill_name)
        .order_by(desc("job_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "skill_name": row.skill_name,
            "job_count": row.job_count,
            "market_penetration_pct": round((row.job_count / total_jobs) * 100, 2),
        }
        for row in results
    ]


def get_skill_distribution_percentages(db: Session) -> List[Dict[str, Any]]:
    """Get demand percentage distribution for all skills."""
    return get_most_demanded_skills(db, top_n=100)


def get_skills_by_role(
    db: Session, role_name: Optional[str] = None, top_n: int = 10
) -> List[Dict[str, Any]]:
    """Get top required skills filtered by job title/role."""
    query = (
        db.query(
            Job.job_title,
            Skill.skill_name,
            func.count(JobSkill.job_id).label("skill_count")
        )
        .join(JobSkill, Job.id == JobSkill.job_id)
        .join(Skill, Skill.id == JobSkill.skill_id)
    )

    if role_name:
        query = query.filter(Job.job_title == role_name)

    results = (
        query.group_by(Job.job_title, Skill.id, Skill.skill_name)
        .order_by(desc("skill_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "job_title": row.job_title,
            "skill_name": row.skill_name,
            "count": row.skill_count,
        }
        for row in results
    ]


def get_skills_by_location(
    db: Session, location_name: Optional[str] = None, top_n: int = 10
) -> List[Dict[str, Any]]:
    """Get top required skills filtered by location."""
    query = (
        db.query(
            Location.location_name,
            Skill.skill_name,
            func.count(JobSkill.job_id).label("skill_count")
        )
        .join(Job, Location.id == Job.location_id)
        .join(JobSkill, Job.id == JobSkill.job_id)
        .join(Skill, Skill.id == JobSkill.skill_id)
    )

    if location_name:
        query = query.filter(Location.location_name == location_name)

    results = (
        query.group_by(Location.location_name, Skill.id, Skill.skill_name)
        .order_by(desc("skill_count"))
        .limit(top_n)
        .all()
    )

    return [
        {
            "location_name": row.location_name,
            "skill_name": row.skill_name,
            "count": row.skill_count,
        }
        for row in results
    ]


def get_related_skills(
    db: Session, target_skill: str, top_n: int = 5
) -> List[Dict[str, Any]]:
    """Find skills that co-occur most frequently in the same job postings as target_skill."""
    target_skill_obj = db.query(Skill).filter(func.lower(Skill.skill_name) == target_skill.strip().lower()).first()
    if not target_skill_obj:
        return []

    target_job_ids_select = select(JobSkill.job_id).where(JobSkill.skill_id == target_skill_obj.id)

    results = (
        db.query(
            Skill.skill_name,
            func.count(JobSkill.job_id).label("co_occurrence_count")
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .filter(JobSkill.job_id.in_(target_job_ids_select))
        .filter(Skill.id != target_skill_obj.id)
        .group_by(Skill.id, Skill.skill_name)
        .order_by(desc("co_occurrence_count"))
        .limit(top_n)
        .all()
    )

    total_target_jobs = db.scalar(select(func.count()).select_from(target_job_ids_select.subquery())) or 1

    return [
        {
            "target_skill": target_skill_obj.skill_name,
            "related_skill": row.skill_name,
            "co_occurrence_count": row.co_occurrence_count,
            "co_occurrence_pct": round((row.co_occurrence_count / total_target_jobs) * 100, 2),
        }
        for row in results
    ]


def get_skill_detail_analytics(
    db: Session, skill_name: str, currency: str = "USD"
) -> Dict[str, Any]:
    """
    Get detailed analytics breakdown for a single skill:
    - job_count
    - market_penetration_pct
    - average_salary
    - top_roles
    - top_locations
    - related_skills
    """
    skill_obj = db.query(Skill).filter(func.lower(Skill.skill_name) == skill_name.strip().lower()).first()
    if not skill_obj:
        return {}

    total_market_jobs = db.query(func.count(Job.id)).scalar() or 1
    job_ids_subquery = select(JobSkill.job_id).where(JobSkill.skill_id == skill_obj.id)

    # 1. Total jobs requiring skill
    job_count = db.scalar(select(func.count()).select_from(job_ids_subquery.subquery())) or 0
    market_pct = round((job_count / total_market_jobs) * 100, 2)

    # 2. Average Salary
    salary_res = (
        db.query(
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
            func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid")
        )
        .filter(Job.id.in_(job_ids_subquery))
        .filter(Job.salary_currency == currency)
        .first()
    )

    avg_mid = round(float(salary_res.avg_mid or 0), 2) if salary_res and salary_res.avg_mid else 0.0

    # 3. Top Roles
    top_roles = (
        db.query(Job.job_title, func.count(Job.id).label("count"))
        .filter(Job.id.in_(job_ids_subquery))
        .group_by(Job.job_title)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    # 4. Top Locations
    top_locations = (
        db.query(Location.location_name, Location.country, func.count(Job.id).label("count"))
        .join(Job, Location.id == Job.location_id)
        .filter(Job.id.in_(job_ids_subquery))
        .group_by(Location.location_name, Location.country)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    # 5. Related Co-occurring Skills
    related = get_related_skills(db, target_skill=skill_obj.skill_name, top_n=5)

    return {
        "skill_name": skill_obj.skill_name,
        "job_count": job_count,
        "market_penetration_pct": market_pct,
        "average_salary": avg_mid,
        "top_roles": [{"job_title": r.job_title, "count": r.count} for r in top_roles],
        "top_locations": [{"location_name": l.location_name, "country": l.country, "count": l.count} for l in top_locations],
        "related_skills": related,
    }
