"""
Pydantic Schemas for Analytics Endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AverageSalarySchema(BaseModel):
    currency: str = "USD"
    min: float
    max: float
    midpoint: float


class OverviewMetricsResponse(BaseModel):
    total_jobs: int
    total_companies: int
    total_locations: int
    total_unique_skills: int
    remote_jobs_count: int
    remote_job_percentage: float
    average_salary: AverageSalarySchema


class SkillDemandItem(BaseModel):
    skill_name: str
    job_count: int
    market_penetration_pct: float


class RelatedSkillItem(BaseModel):
    target_skill: str
    related_skill: str
    co_occurrence_count: int
    co_occurrence_pct: float


class RoleDistributionItem(BaseModel):
    job_title: str
    job_count: int
    percentage: float


class RoleSkillItem(BaseModel):
    job_title: str
    skill_name: str
    count: int
    percentage: Optional[float] = None


class RoleSalaryItem(BaseModel):
    job_title: str
    job_count: int
    avg_salary_min: float
    avg_salary_max: float
    median_salary: float
    avg_midpoint_salary: float


class LocationDistributionItem(BaseModel):
    location_name: str
    country: str
    job_count: int
    percentage: float


class LocationSkillItem(BaseModel):
    location_name: str
    skill_name: str
    count: int
    percentage: Optional[float] = None


class MidpointMetricsSchema(BaseModel):
    average: float
    median: float
    minimum: float
    maximum: float
    std_dev: float
    percentile_25: float
    percentile_75: float


class SalaryMinMaxMetricsSchema(BaseModel):
    average: float
    median: float
    minimum: float
    maximum: float


class SalarySummaryResponse(BaseModel):
    currency: str = "USD"
    sample_size: int
    midpoint_metrics: MidpointMetricsSchema
    salary_min_metrics: SalaryMinMaxMetricsSchema
    salary_max_metrics: SalaryMinMaxMetricsSchema


class ExperienceDistributionItem(BaseModel):
    experience_level: str
    job_count: int
    percentage: float


class RemoteDistributionItem(BaseModel):
    remote_type: str
    job_count: int
    percentage: float


class RemoteSalaryComparisonItem(BaseModel):
    remote_type: str
    job_count: int
    avg_salary_min: float
    avg_salary_max: float
    avg_midpoint_salary: float


class SkillGapRequest(BaseModel):
    target_role: str
    user_skills: List[str]


class SkillGapResponse(BaseModel):
    target_role: str
    user_skills: List[str]
    role_skills_evaluated: List[str]
    matching_skills: List[str]
    missing_skills: List[str]
    related_skills: List[str]
    disclaimer: str
