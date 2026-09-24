"""
Repository Module for Job Market Analytics.

Provides data access logic and analytics queries using SQLAlchemy ORM.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Job, Company, Location, Skill, JobSkill


class JobRepository:
    """Repository class encapsulating SQL query logic."""

    def __init__(self, db: Session):
        self.db = db

    def get_total_jobs(self) -> int:
        """Get total number of job postings in the database."""
        return self.db.query(func.count(Job.id)).scalar() or 0

    def get_jobs_by_role(self) -> List[Dict[str, Any]]:
        """Get job counts and percentages grouped by standardized job_title."""
        total = self.get_total_jobs()
        if total == 0:
            return []

        results = (
            self.db.query(
                Job.job_title,
                func.count(Job.id).label("job_count")
            )
            .group_by(Job.job_title)
            .order_by(desc("job_count"))
            .all()
        )

        return [
            {
                "job_title": row.job_title,
                "job_count": row.job_count,
                "percentage": round((row.job_count / total) * 100, 2)
            }
            for row in results
        ]

    def get_jobs_by_location(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Get job counts grouped by location and country."""
        results = (
            self.db.query(
                Location.location_name,
                Location.country,
                func.count(Job.id).label("job_count")
            )
            .join(Job, Job.location_id == Location.id)
            .group_by(Location.location_name, Location.country)
            .order_by(desc("job_count"))
            .limit(limit)
            .all()
        )

        return [
            {
                "location_name": row.location_name,
                "country": row.country,
                "job_count": row.job_count,
            }
            for row in results
        ]

    def get_jobs_by_skill(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top in-demand skills by job frequency."""
        total = self.get_total_jobs()
        results = (
            self.db.query(
                Skill.skill_name,
                func.count(JobSkill.job_id).label("demand_count")
            )
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .group_by(Skill.id, Skill.skill_name)
            .order_by(desc("demand_count"))
            .limit(limit)
            .all()
        )

        return [
            {
                "skill_name": row.skill_name,
                "demand_count": row.demand_count,
                "market_penetration_pct": round((row.demand_count / total) * 100, 2) if total > 0 else 0.0
            }
            for row in results
        ]

    def get_jobs_by_experience(self) -> List[Dict[str, Any]]:
        """Get job count distribution by experience level."""
        results = (
            self.db.query(
                Job.experience_level,
                func.count(Job.id).label("job_count")
            )
            .group_by(Job.experience_level)
            .order_by(desc("job_count"))
            .all()
        )

        return [
            {"experience_level": row.experience_level, "job_count": row.job_count}
            for row in results
        ]

    def get_jobs_by_remote_type(self) -> List[Dict[str, Any]]:
        """Get job count distribution by remote work type."""
        total = self.get_total_jobs()
        results = (
            self.db.query(
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
                "percentage": round((row.job_count / total) * 100, 2) if total > 0 else 0.0
            }
            for row in results
        ]

    def get_salary_analytics(self, currency: str = "USD") -> Dict[str, Any]:
        """Get overall aggregate salary metrics for specified currency."""
        result = (
            self.db.query(
                func.count(Job.id).label("count"),
                func.avg(Job.salary_min).label("avg_min"),
                func.avg(Job.salary_max).label("avg_max"),
                func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid"),
                func.min(Job.salary_min).label("min_salary"),
                func.max(Job.salary_max).label("max_salary")
            )
            .filter(Job.salary_currency == currency)
            .first()
        )

        if not result or result.count == 0:
            return {}

        return {
            "currency": currency,
            "total_jobs_with_salary": result.count,
            "avg_salary_min": round(float(result.avg_min or 0), 2),
            "avg_salary_max": round(float(result.avg_max or 0), 2),
            "overall_avg_salary": round(float(result.avg_mid or 0), 2),
            "min_recorded_salary": round(float(result.min_salary or 0), 2),
            "max_recorded_salary": round(float(result.max_salary or 0), 2),
        }

    def get_salary_by_role(self, currency: str = "USD") -> List[Dict[str, Any]]:
        """Get average salary metrics grouped by job_title."""
        results = (
            self.db.query(
                Job.job_title,
                func.count(Job.id).label("job_count"),
                func.avg(Job.salary_min).label("avg_min"),
                func.avg(Job.salary_max).label("avg_max"),
                func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid")
            )
            .filter(Job.salary_currency == currency)
            .group_by(Job.job_title)
            .order_by(desc("avg_mid"))
            .all()
        )

        return [
            {
                "job_title": row.job_title,
                "job_count": row.job_count,
                "avg_salary_min": round(float(row.avg_min or 0), 2),
                "avg_salary_max": round(float(row.avg_max or 0), 2),
                "avg_midpoint_salary": round(float(row.avg_mid or 0), 2),
            }
            for row in results
        ]

    def get_salary_by_location(self, currency: str = "USD", min_jobs: int = 5) -> List[Dict[str, Any]]:
        """Get average salary metrics grouped by location."""
        results = (
            self.db.query(
                Location.location_name,
                Location.country,
                func.count(Job.id).label("job_count"),
                func.avg(Job.salary_min).label("avg_min"),
                func.avg(Job.salary_max).label("avg_max"),
                func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid")
            )
            .join(Job, Job.location_id == Location.id)
            .filter(Job.salary_currency == currency)
            .group_by(Location.location_name, Location.country)
            .having(func.count(Job.id) >= min_jobs)
            .order_by(desc("avg_mid"))
            .all()
        )

        return [
            {
                "location_name": row.location_name,
                "country": row.country,
                "job_count": row.job_count,
                "avg_salary_min": round(float(row.avg_min or 0), 2),
                "avg_salary_max": round(float(row.avg_max or 0), 2),
                "avg_midpoint_salary": round(float(row.avg_mid or 0), 2),
            }
            for row in results
        ]
