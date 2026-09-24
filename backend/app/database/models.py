"""
SQLAlchemy ORM Data Models for Job Market Analytics.

Defines schemas for:
- Company
- Location
- Job
- Skill
- JobSkill (Mapping table)
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), default="Information Technology")
    created_at = Column(DateTime, server_default=func.now())

    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("location_name", "country", name="uk_location_country"),
    )

    jobs = relationship("Job", back_populates="location", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), nullable=False, unique=True, index=True)
    job_title = Column(String(150), nullable=False, index=True)
    raw_job_title = Column(String(255))
    seniority_level = Column(String(50), default="Mid-level")
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    employment_type = Column(String(50), default="Full-time")
    experience_level = Column(String(50), default="Mid-level", index=True)
    remote_type = Column(String(50), default="On-site", index=True)
    salary_min = Column(Float, index=True)
    salary_max = Column(Float, index=True)
    salary_currency = Column(String(10), default="USD")
    salary_is_imputed = Column(Boolean, default=False)
    description = Column(Text)
    education = Column(String(100), default="Unspecified")
    posting_date = Column(Date, nullable=False, index=True)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="jobs")
    location = relationship("Location", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), default="Technical")
    created_at = Column(DateTime, server_default=func.now())

    job_skills = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True, index=True)
    source = Column(String(50), default="required_skills")
    is_normalized = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill", back_populates="job_skills")
