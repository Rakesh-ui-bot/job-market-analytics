"""
Pydantic Schemas for Job Postings and Pagination.
"""

from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class LocationSchema(BaseModel):
    id: int
    location_name: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class CompanySchema(BaseModel):
    id: int
    name: str
    industry: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SkillSchema(BaseModel):
    id: int
    skill_name: str
    category: Optional[str] = "Technical"

    model_config = ConfigDict(from_attributes=True)


class JobSkillSchema(BaseModel):
    skill_name: str
    source: str
    is_normalized: bool

    model_config = ConfigDict(from_attributes=True)


class JobSummarySchema(BaseModel):
    id: int
    job_id: str
    job_title: str
    raw_job_title: Optional[str] = None
    seniority_level: Optional[str] = "Mid-level"
    company: str
    location: str
    country: str
    employment_type: str
    experience_level: str
    remote_type: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    salary_is_imputed: bool = False
    posting_date: date
    is_synthetic: bool = True
    skills: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class JobDetailSchema(BaseModel):
    id: int
    job_id: str
    job_title: str
    raw_job_title: Optional[str] = None
    seniority_level: Optional[str] = "Mid-level"
    company: CompanySchema
    location: LocationSchema
    employment_type: str
    experience_level: str
    remote_type: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    salary_is_imputed: bool = False
    description: Optional[str] = None
    education: Optional[str] = "Unspecified"
    posting_date: date
    is_synthetic: bool = True
    created_at: Optional[datetime] = None
    skills: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedJobsResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: List[JobSummarySchema]
