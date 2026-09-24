"""
Unit tests for analytics and business logic modules (backend/app/analytics/).
Verifies dynamic metric calculations, statistics, percentiles, distributions, and co-occurrences.
"""

import pytest
from pathlib import Path
import sys
from sqlalchemy.orm import Session

# Ensure backend root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import get_engine, get_session_factory, init_db
from app.database.import_data import import_processed_data
from app.config import PROCESSED_DATA_DIR

from app.analytics import (
    get_overview_metrics,
    get_most_demanded_skills,
    get_skill_distribution_percentages,
    get_skills_by_role,
    get_skills_by_location,
    get_related_skills,
    get_most_common_roles,
    get_jobs_per_role,
    get_skills_per_role,
    get_salary_per_role,
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
)


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def analytics_db_session():
    """Module-level fixture setting up database session for analytics testing."""
    engine = get_engine(TEST_DB_URL)
    init_db(engine)

    SessionLocal = get_session_factory(TEST_DB_URL)
    session = SessionLocal()

    cleaned_jobs = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
    job_skills = PROCESSED_DATA_DIR / "job_skills.csv"

    if cleaned_jobs.exists() and job_skills.exists():
        import_processed_data(db_url=TEST_DB_URL, jobs_csv=cleaned_jobs, skills_csv=job_skills)

    yield session
    session.close()


def test_overview_metrics(analytics_db_session: Session):
    overview = get_overview_metrics(analytics_db_session)
    assert overview["total_jobs"] > 5000
    assert overview["total_companies"] > 0
    assert overview["total_locations"] > 0
    assert overview["total_unique_skills"] > 0
    assert overview["remote_job_percentage"] > 0
    assert overview["average_salary"]["midpoint"] > 0


def test_skills_analytics(analytics_db_session: Session):
    top_skills = get_most_demanded_skills(analytics_db_session, top_n=5)
    assert len(top_skills) == 5
    assert top_skills[0]["job_count"] >= top_skills[1]["job_count"]

    percentages = get_skill_distribution_percentages(analytics_db_session)
    assert len(percentages) > 0

    role_skills = get_skills_by_role(analytics_db_session, role_name="Backend Developer", top_n=5)
    assert len(role_skills) > 0

    loc_skills = get_skills_by_location(analytics_db_session, top_n=5)
    assert len(loc_skills) > 0

    related = get_related_skills(analytics_db_session, target_skill="Python", top_n=5)
    assert len(related) > 0
    assert related[0]["target_skill"] == "Python"
    assert "related_skill" in related[0]


def test_roles_analytics(analytics_db_session: Session):
    top_roles = get_most_common_roles(analytics_db_session, top_n=5)
    assert len(top_roles) == 5
    assert "percentage" in top_roles[0]

    all_roles = get_jobs_per_role(analytics_db_session)
    assert len(all_roles) > 0

    skills_role = get_skills_per_role(analytics_db_session, role_name="Frontend Developer", top_n=5)
    assert len(skills_role) > 0

    sal_role = get_salary_per_role(analytics_db_session)
    assert len(sal_role) > 0
    assert sal_role[0]["avg_midpoint_salary"] > 0


def test_locations_analytics(analytics_db_session: Session):
    cities = get_jobs_per_city(analytics_db_session, top_n=5)
    assert len(cities) == 5

    countries = get_jobs_per_country(analytics_db_session)
    assert len(countries) > 0

    loc_skills = get_skills_per_location(analytics_db_session, location_name="New York, NY", top_n=5)
    assert len(loc_skills) > 0

    remote_loc = get_remote_jobs_by_location(analytics_db_session)
    assert len(remote_loc) > 0


def test_salary_analytics(analytics_db_session: Session):
    stats = get_salary_summary_statistics(analytics_db_session)
    assert stats["sample_size"] > 0
    mid = stats["midpoint_metrics"]
    assert mid["average"] > 0
    assert mid["median"] > 0
    assert mid["minimum"] > 0
    assert mid["maximum"] >= mid["minimum"]
    assert mid["percentile_75"] >= mid["percentile_25"]

    sal_exp = get_salary_by_experience(analytics_db_session)
    assert len(sal_exp) > 0

    sal_loc = get_salary_by_location(analytics_db_session, min_jobs=1)
    assert len(sal_loc) > 0


def test_experience_analytics(analytics_db_session: Session):
    dist = get_experience_level_distribution(analytics_db_session)
    assert len(dist) > 0

    role_exp = get_role_distribution_by_experience(analytics_db_session)
    assert len(role_exp) > 0


def test_remote_analytics(analytics_db_session: Session):
    dist = get_remote_work_distribution(analytics_db_session)
    assert len(dist) > 0

    by_role = get_remote_by_role(analytics_db_session)
    assert len(by_role) > 0

    sal_comp = get_remote_salary_comparison(analytics_db_session)
    assert len(sal_comp) > 0
