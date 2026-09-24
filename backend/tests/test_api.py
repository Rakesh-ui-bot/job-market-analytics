"""
Integration unit tests for FastAPI REST API endpoints using TestClient.
Uses SQLite in-memory database to execute tests without requiring external MySQL server.
"""

import pytest
from pathlib import Path
import sys
import io
from fastapi.testclient import TestClient

# Ensure backend root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.database.connection import get_engine, get_session_factory, init_db, get_session
from app.database.import_data import import_processed_data
from app.config import PROCESSED_DATA_DIR

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def api_client():
    """Module-level fixture configuring TestClient with SQLite in-memory DB."""
    engine = get_engine(TEST_DB_URL)
    init_db(engine)

    cleaned_jobs = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
    job_skills = PROCESSED_DATA_DIR / "job_skills.csv"

    if cleaned_jobs.exists() and job_skills.exists():
        import_processed_data(db_url=TEST_DB_URL, jobs_csv=cleaned_jobs, skills_csv=job_skills)

    SessionLocal = get_session_factory(TEST_DB_URL)

    # Override get_session dependency
    def _override_get_session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = _override_get_session
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_swagger_docs(api_client: TestClient):
    """Test interactive OpenAPI docs endpoint."""
    response = api_client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower() or "html" in response.text.lower()


def test_health_check_endpoint(api_client: TestClient):
    """Test GET /api/health."""
    response = api_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database_status"] == "healthy"


def test_get_jobs_paginated(api_client: TestClient):
    """Test GET /api/jobs default pagination."""
    response = api_client.get("/api/jobs?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 5000
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["items"]) == 10
    assert "job_title" in data["items"][0]


def test_get_jobs_with_filters(api_client: TestClient):
    """Test GET /api/jobs with multi-field filtering parameters."""
    url = "/api/jobs?role=Backend%20Developer&skill=Python&remote_type=Remote&limit=5"
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
    assert len(data["items"]) <= 5
    if len(data["items"]) > 0:
        assert data["items"][0]["job_title"] == "Backend Developer"


def test_upload_csv_validation_and_ingestion(api_client: TestClient):
    """Test POST /api/jobs/upload with CSV content."""
    csv_content = (
        "job_id,job_title,company,location,country,employment_type,experience_level,remote_type,salary_min,salary_max,description,required_skills\n"
        "JOB-TEST-101,Python Developer,Acme Corp,New York,United States,Full-time,Senior,Remote,140000,180000,Seeking Python and Docker developer,Python, Docker, SQL\n"
    )
    files = {"file": ("test_upload.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = api_client.post("/api/jobs/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["records_read"] == 1
    assert data["jobs_inserted"] >= 0


def test_upload_invalid_csv_schema_error(api_client: TestClient):
    """Test POST /api/jobs/upload with missing required columns triggers 422 error."""
    csv_content = "invalid_col1,invalid_col2\nval1,val2\n"
    files = {"file": ("bad_schema.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = api_client.post("/api/jobs/upload", files=files)
    assert response.status_code == 422
    assert "missing required columns" in response.json()["detail"].lower()


def test_get_job_by_id_success(api_client: TestClient):
    """Test GET /api/jobs/{id} with existing integer ID."""
    list_res = api_client.get("/api/jobs?limit=1")
    job_id = list_res.json()["items"][0]["id"]

    response = api_client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert "company" in data
    assert "skills" in data


def test_get_job_by_id_not_found(api_client: TestClient):
    """Test GET /api/jobs/{id} with non-existent ID."""
    response = api_client.get("/api/jobs/99999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_analytics_overview_endpoint(api_client: TestClient):
    """Test GET /api/analytics/overview."""
    response = api_client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] > 5000
    assert "average_salary" in data


def test_analytics_skill_gap_endpoint(api_client: TestClient):
    """Test POST /api/analytics/skill-gap."""
    payload = {
        "target_role": "Python Developer",
        "user_skills": ["Python", "Git", "SQL"],
    }
    response = api_client.post("/api/analytics/skill-gap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_role"] == "Python Developer"
    assert "matching_skills" in data
    assert "missing_skills" in data
    assert "disclaimer" in data


def test_analytics_skills_endpoint(api_client: TestClient):
    """Test GET /api/analytics/skills."""
    response = api_client.get("/api/analytics/skills?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert "skill_name" in data[0]


def test_analytics_roles_endpoint(api_client: TestClient):
    """Test GET /api/analytics/roles."""
    response = api_client.get("/api/analytics/roles?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert "job_title" in data[0]


def test_analytics_locations_endpoint(api_client: TestClient):
    """Test GET /api/analytics/locations."""
    response = api_client.get("/api/analytics/locations")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert "countries" in data


def test_analytics_salary_endpoint(api_client: TestClient):
    """Test GET /api/analytics/salary."""
    response = api_client.get("/api/analytics/salary")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "by_role" in data


def test_analytics_experience_endpoint(api_client: TestClient):
    """Test GET /api/analytics/experience."""
    response = api_client.get("/api/analytics/experience")
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data


def test_analytics_remote_endpoint(api_client: TestClient):
    """Test GET /api/analytics/remote."""
    response = api_client.get("/api/analytics/remote")
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "salary_comparison" in data
