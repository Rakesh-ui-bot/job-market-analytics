"""
Unit tests for data normalizer module (backend/app/processing/normalizer.py).
"""

import pytest
from app.processing.normalizer import (
    normalize_skill,
    normalize_location,
    normalize_job_title,
    normalize_employment_type,
    normalize_remote_type,
    normalize_experience_level,
)


def test_normalize_skill_aliases():
    assert normalize_skill("ReactJS") == "React"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("REACT") == "React"
    assert normalize_skill("JS") == "JavaScript"
    assert normalize_skill("javascript") == "JavaScript"
    assert normalize_skill("TS") == "TypeScript"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("PostgreSQL") == "PostgreSQL"
    assert normalize_skill("My SQL") == "MySQL"
    assert normalize_skill("mysql") == "MySQL"
    assert normalize_skill("cpp") == "C++"
    assert normalize_skill("aws") == "AWS"
    assert normalize_skill("node") == "Node.js"
    assert normalize_skill("NodeJS") == "Node.js"


def test_normalize_location():
    assert normalize_location("New York") == "New York, NY"
    assert normalize_location("NY, USA") == "New York, NY"
    assert normalize_location("san francisco, california") == "San Francisco, CA"
    assert normalize_location("london") == "London, UK"
    assert normalize_location("bangalore") == "Bengaluru, India"
    assert normalize_location(None, "Germany") == "Remote, Germany"


def test_normalize_job_title():
    role, seniority = normalize_job_title("Senior Python Developer")
    assert role == "Backend Developer"
    assert seniority == "Senior"

    role, seniority = normalize_job_title("Junior React Developer")
    assert role == "Frontend Developer"
    assert seniority == "Junior"

    role, seniority = normalize_job_title("Lead Data Scientist")
    assert role == "Data Scientist"
    assert seniority == "Lead"


def test_normalize_employment_type():
    assert normalize_employment_type("full_time") == "Full-time"
    assert normalize_employment_type("Full Time") == "Full-time"
    assert normalize_employment_type("contractor") == "Contract"


def test_normalize_remote_type():
    assert normalize_remote_type("Full Remote") == "Remote"
    assert normalize_remote_type("onsite") == "On-site"
    assert normalize_remote_type("hybrid") == "Hybrid"
