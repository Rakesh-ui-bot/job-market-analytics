"""
Analytics Service Module.

Exposes service layer wrapper methods for analytical queries.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.analytics import (
    get_overview_metrics,
    get_most_demanded_skills,
    get_skill_distribution_percentages,
    get_skills_by_role,
    get_skills_by_location,
    get_related_skills,
    get_skill_detail_analytics,
    get_most_common_roles,
    get_jobs_per_role,
    get_skills_per_role,
    get_salary_per_role,
    get_role_detail_analytics,
    get_jobs_per_city,
    get_jobs_per_country,
    get_skills_per_location,
    get_remote_jobs_by_location,
    get_salary_summary_statistics,
    get_salary_by_role,
    get_salary_by_experience,
    get_salary_by_location,
    get_experience_level_distribution,
    get_role_distribution_by_experience,
    get_remote_work_distribution,
    get_remote_by_role,
    get_remote_salary_comparison,
    calculate_skill_gap,
)


class AnalyticsService:

    @staticmethod
    def overview(
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
    ):
        return get_overview_metrics(
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

    @staticmethod
    def skills(db: Session, limit: int = 15):
        return get_most_demanded_skills(db, top_n=limit)

    @staticmethod
    def skill_detail(db: Session, skill: str, currency: str = "USD"):
        return get_skill_detail_analytics(db, skill_name=skill, currency=currency)

    @staticmethod
    def skills_by_role(db: Session, role: Optional[str] = None, limit: int = 10):
        if role:
            return get_skills_per_role(db, role_name=role, top_n=limit)
        return get_skills_by_role(db, role_name=None, top_n=limit)

    @staticmethod
    def skills_by_location(db: Session, location: Optional[str] = None, limit: int = 10):
        if location:
            return get_skills_per_location(db, location_name=location, top_n=limit)
        return get_skills_by_location(db, location_name=None, top_n=limit)

    @staticmethod
    def related_skills(db: Session, skill: str, limit: int = 5):
        return get_related_skills(db, target_skill=skill, top_n=limit)

    @staticmethod
    def skill_gap(db: Session, target_role: str, user_skills: List[str]):
        return calculate_skill_gap(db, target_role=target_role, user_skills=user_skills)

    @staticmethod
    def roles(db: Session, limit: int = 10):
        return get_most_common_roles(db, top_n=limit)

    @staticmethod
    def role_detail(db: Session, role: str, currency: str = "USD"):
        return get_role_detail_analytics(db, role_name=role, currency=currency)

    @staticmethod
    def locations(db: Session, limit: int = 15):
        return {
            "cities": get_jobs_per_city(db, top_n=limit),
            "countries": get_jobs_per_country(db),
        }

    @staticmethod
    def salary(db: Session, currency: str = "USD"):
        return {
            "summary": get_salary_summary_statistics(db, currency=currency),
            "by_role": get_salary_by_role(db, currency=currency),
            "by_experience": get_salary_by_experience(db, currency=currency),
            "by_location": get_salary_by_location(db, currency=currency),
        }

    @staticmethod
    def experience(db: Session):
        return {
            "distribution": get_experience_level_distribution(db),
            "role_breakdown": get_role_distribution_by_experience(db),
        }

    @staticmethod
    def remote(db: Session, currency: str = "USD"):
        return {
            "distribution": get_remote_work_distribution(db),
            "by_role": get_remote_by_role(db),
            "salary_comparison": get_remote_salary_comparison(db, currency=currency),
        }
