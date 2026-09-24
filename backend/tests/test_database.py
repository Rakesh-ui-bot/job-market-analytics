"""
Unit tests for database module, ORM models, data importer, and repository queries.
Uses SQLite in-memory database to execute tests without requiring external MySQL server.
"""

import pytest
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
import sys

# Ensure backend root is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import get_engine, get_session_factory, init_db
from app.database.models import Company, Location, Job, Skill, JobSkill
from app.database.import_data import import_processed_data
from app.database.repository import JobRepository
from app.config import PROCESSED_DATA_DIR


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def test_db_session():
    """Module-level fixture initializing in-memory SQLite database and importing processed data."""
    engine = get_engine(TEST_DB_URL)
    init_db(engine)
    
    SessionLocal = get_session_factory(TEST_DB_URL)
    session = SessionLocal()

    # Perform import
    cleaned_jobs = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
    job_skills = PROCESSED_DATA_DIR / "job_skills.csv"

    if cleaned_jobs.exists() and job_skills.exists():
        import_processed_data(db_url=TEST_DB_URL, jobs_csv=cleaned_jobs, skills_csv=job_skills)

    yield session

    session.close()


def test_db_table_creation():
    """Test that all database tables are created."""
    engine = get_engine(TEST_DB_URL)
    init_db(engine)
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "jobs" in tables
    assert "companies" in tables
    assert "locations" in tables
    assert "skills" in tables
    assert "job_skills" in tables


def test_data_imported_records(test_db_session: Session):
    """Test that records were imported into ORM tables."""
    total_jobs = test_db_session.query(Job).count()
    assert total_jobs > 5000

    total_companies = test_db_session.query(Company).count()
    assert total_companies > 0

    total_skills = test_db_session.query(Skill).count()
    assert total_skills > 0

    total_js = test_db_session.query(JobSkill).count()
    assert total_js > 10000


def test_idempotency_duplicate_prevention(test_db_session: Session):
    """Test that re-running import skips existing records and does not insert duplicates."""
    cleaned_jobs = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
    job_skills = PROCESSED_DATA_DIR / "job_skills.csv"

    csv_rows_count = len(pd.read_csv(cleaned_jobs))

    # Re-run import
    stats = import_processed_data(db_url=TEST_DB_URL, jobs_csv=cleaned_jobs, skills_csv=job_skills)

    # Assert 0 new jobs inserted and exact duplicate count skipped
    assert stats["jobs_inserted"] == 0
    assert stats["jobs_skipped_duplicate"] == csv_rows_count


def test_repository_analytics_queries(test_db_session: Session):
    """Test all repository analytics query methods."""
    repo = JobRepository(test_db_session)

    # 1. Total jobs
    total = repo.get_total_jobs()
    assert total > 5000

    # 2. Jobs by role
    by_role = repo.get_jobs_by_role()
    assert len(by_role) > 0
    assert "job_title" in by_role[0]
    assert "job_count" in by_role[0]

    # 3. Jobs by location
    by_loc = repo.get_jobs_by_location(limit=10)
    assert len(by_loc) > 0
    assert "location_name" in by_loc[0]

    # 4. Jobs by skill
    by_skill = repo.get_jobs_by_skill(limit=10)
    assert len(by_skill) > 0
    assert "skill_name" in by_skill[0]
    assert "demand_count" in by_skill[0]

    # 5. Jobs by experience
    by_exp = repo.get_jobs_by_experience()
    assert len(by_exp) > 0
    assert "experience_level" in by_exp[0]

    # 6. Jobs by remote type
    by_remote = repo.get_jobs_by_remote_type()
    assert len(by_remote) > 0
    assert "remote_type" in by_remote[0]

    # 7. Salary analytics
    sal_analytics = repo.get_salary_analytics()
    assert "overall_avg_salary" in sal_analytics
    assert sal_analytics["overall_avg_salary"] > 0

    # 8. Salary by role
    sal_role = repo.get_salary_by_role()
    assert len(sal_role) > 0
    assert "avg_midpoint_salary" in sal_role[0]

    # 9. Salary by location
    sal_loc = repo.get_salary_by_location(min_jobs=1)
    assert len(sal_loc) > 0
    assert "avg_midpoint_salary" in sal_loc[0]
