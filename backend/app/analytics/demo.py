"""
Analytics Demonstration Script.

Executes and prints sample outputs for all analytics modules using the real processed dataset.
"""

import sys
import json
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database.connection import get_engine, get_session_factory, init_db
from app.database.import_data import import_processed_data
from app.config import PROCESSED_DATA_DIR, RAW_DATASET_FILE
from app.processing.pipeline import run_pipeline

from app.analytics import (
    get_overview_metrics,
    get_most_demanded_skills,
    get_related_skills,
    get_most_common_roles,
    get_jobs_per_city,
    get_salary_summary_statistics,
    get_experience_level_distribution,
    get_remote_work_distribution,
    get_remote_salary_comparison,
)


def main():
    db_url = "sqlite:///:memory:"
    
    # 1. Ensure processed files exist
    cleaned_jobs = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
    job_skills = PROCESSED_DATA_DIR / "job_skills.csv"

    if not cleaned_jobs.exists() or not job_skills.exists():
        print("Running Phase 2 pipeline first to prepare processed data...")
        run_pipeline()

    # 2. Ingest into database
    print("Populating database for analytics demonstration...")
    engine = get_engine(db_url)
    init_db(engine)
    import_processed_data(db_url=db_url, jobs_csv=cleaned_jobs, skills_csv=job_skills)

    SessionLocal = get_session_factory(db_url)
    db = SessionLocal()

    print("\n" + "=" * 70)
    print("ANALYTICS & BUSINESS LOGIC SAMPLE OUTPUTS")
    print("=" * 70)

    # Overview
    print("\n--- 1. OVERVIEW METRICS ---")
    print(json.dumps(get_overview_metrics(db), indent=2))

    # Top Skills
    print("\n--- 2. MOST DEMANDED TECH SKILLS (Top 5) ---")
    print(json.dumps(get_most_demanded_skills(db, top_n=5), indent=2))

    # Related Skills for Python
    print("\n--- 3. RELATED SKILLS (Co-occurring with 'Python') ---")
    print(json.dumps(get_related_skills(db, "Python", top_n=5), indent=2))

    # Roles
    print("\n--- 4. MOST COMMON JOB ROLES (Top 5) ---")
    print(json.dumps(get_most_common_roles(db, top_n=5), indent=2))

    # Cities
    print("\n--- 5. JOBS PER CITY (Top 5) ---")
    print(json.dumps(get_jobs_per_city(db, top_n=5), indent=2))

    # Salary Summary Statistics
    print("\n--- 6. SALARY SUMMARY STATISTICAL METRICS (USD) ---")
    print(json.dumps(get_salary_summary_statistics(db), indent=2))

    # Experience Distribution
    print("\n--- 7. EXPERIENCE LEVEL DISTRIBUTION ---")
    print(json.dumps(get_experience_level_distribution(db), indent=2))

    # Remote Distribution & Salary Comparison
    print("\n--- 8. REMOTE WORK DISTRIBUTION & SALARY COMPARISON ---")
    print(json.dumps(get_remote_work_distribution(db), indent=2))
    print("\nRemote Salary Comparison:")
    print(json.dumps(get_remote_salary_comparison(db), indent=2))

    print("=" * 70)
    db.close()


if __name__ == "__main__":
    main()
