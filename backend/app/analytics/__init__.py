"""
Analytics & Business Logic Package for Job Market Analytics.
"""

from app.analytics.overview import get_overview_metrics
from app.analytics.skills import (
    get_most_demanded_skills,
    get_skill_distribution_percentages,
    get_skills_by_role,
    get_skills_by_location,
    get_related_skills,
    get_skill_detail_analytics,
)
from app.analytics.roles import (
    get_most_common_roles,
    get_jobs_per_role,
    get_skills_per_role,
    get_salary_per_role,
    get_role_detail_analytics,
)
from app.analytics.locations import (
    get_jobs_per_city,
    get_jobs_per_country,
    get_skills_per_location,
    get_remote_jobs_by_location,
)
from app.analytics.salary import (
    get_salary_summary_statistics,
    get_salary_by_role,
    get_salary_by_experience,
    get_salary_by_location,
)
from app.analytics.experience import (
    get_experience_level_distribution,
    get_role_distribution_by_experience,
)
from app.analytics.remote import (
    get_remote_work_distribution,
    get_remote_by_role,
    get_remote_salary_comparison,
)
from app.analytics.skill_gap import calculate_skill_gap

__all__ = [
    "get_overview_metrics",
    "get_most_demanded_skills",
    "get_skill_distribution_percentages",
    "get_skills_by_role",
    "get_skills_by_location",
    "get_related_skills",
    "get_skill_detail_analytics",
    "get_most_common_roles",
    "get_jobs_per_role",
    "get_skills_per_role",
    "get_salary_per_role",
    "get_role_detail_analytics",
    "get_jobs_per_city",
    "get_jobs_per_country",
    "get_skills_per_location",
    "get_remote_jobs_by_location",
    "get_salary_summary_statistics",
    "get_salary_by_role",
    "get_salary_by_experience",
    "get_salary_by_location",
    "get_experience_level_distribution",
    "get_role_distribution_by_experience",
    "get_remote_work_distribution",
    "get_remote_by_role",
    "get_remote_salary_comparison",
    "calculate_skill_gap",
]
