"""
Pydantic Schemas Package.
"""

from app.schemas.jobs import (
    JobSummarySchema,
    JobDetailSchema,
    PaginatedJobsResponse,
    CompanySchema,
    LocationSchema,
    SkillSchema,
)
from app.schemas.analytics import (
    OverviewMetricsResponse,
    SkillDemandItem,
    RelatedSkillItem,
    RoleDistributionItem,
    RoleSkillItem,
    RoleSalaryItem,
    LocationDistributionItem,
    LocationSkillItem,
    SalarySummaryResponse,
    ExperienceDistributionItem,
    RemoteDistributionItem,
    RemoteSalaryComparisonItem,
)

__all__ = [
    "JobSummarySchema",
    "JobDetailSchema",
    "PaginatedJobsResponse",
    "CompanySchema",
    "LocationSchema",
    "SkillSchema",
    "OverviewMetricsResponse",
    "SkillDemandItem",
    "RelatedSkillItem",
    "RoleDistributionItem",
    "RoleSkillItem",
    "RoleSalaryItem",
    "LocationDistributionItem",
    "LocationSkillItem",
    "SalarySummaryResponse",
    "ExperienceDistributionItem",
    "RemoteDistributionItem",
    "RemoteSalaryComparisonItem",
]
