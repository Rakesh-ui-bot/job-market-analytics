"""
Data Ingestion Script for Job Market Analytics.

Imports cleaned CSV datasets (`data/processed/cleaned_jobs.csv` and `data/processed/job_skills.csv`)
into MySQL using SQLAlchemy ORM.

Deduplicates records during ingestion to avoid duplicate insertions.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

# Ensure backend root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import PROCESSED_DATA_DIR
from app.database.connection import get_session_factory, init_db, get_engine
from app.database.models import Company, Location, Job, Skill, JobSkill


CLEANED_JOBS_FILE = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
JOB_SKILLS_FILE = PROCESSED_DATA_DIR / "job_skills.csv"


def import_processed_data(
    db_url: str = None,
    jobs_csv: Path = CLEANED_JOBS_FILE,
    skills_csv: Path = JOB_SKILLS_FILE,
) -> dict:
    """
    Import processed job postings and skill mappings into database.

    Args:
        db_url: Optional explicit DB connection string (defaults to env config).
        jobs_csv: Path to cleaned_jobs.csv
        skills_csv: Path to job_skills.csv

    Returns:
        dict: Ingestion execution summary report
    """
    print("=" * 60)
    print("STARTING DATA IMPORT TO DATABASE (PHASE 3)")
    print("=" * 60)

    if not jobs_csv.exists() or not skills_csv.exists():
        raise FileNotFoundError(
            f"Processed datasets not found! Please run Phase 2 pipeline first.\n"
            f"Expected: {jobs_csv} and {skills_csv}"
        )

    # Initialize tables if not exist
    engine = get_engine(db_url)
    init_db(engine)

    SessionLocal = get_session_factory(db_url)
    db: Session = SessionLocal()

    stats = {
        "jobs_inserted": 0,
        "jobs_skipped_duplicate": 0,
        "companies_created": 0,
        "locations_created": 0,
        "skills_created": 0,
        "job_skills_inserted": 0,
    }

    try:
        # Load CSVs
        print(f"Loading cleaned jobs CSV: {jobs_csv}")
        jobs_df = pd.read_csv(jobs_csv)
        print(f"Loading job skills CSV: {skills_csv}")
        skills_df = pd.read_csv(skills_csv)

        # 1. Lookups Cache for fast batch insertion
        existing_companies = {c.name: c.id for c in db.query(Company).all()}
        existing_locations = {(l.location_name, l.country): l.id for l in db.query(Location).all()}
        existing_skills = {s.skill_name: s.id for s in db.query(Skill).all()}
        existing_job_ids = {j.job_id: j.id for j in db.query(Job.job_id, Job.id).all()}

        print("Ingesting Companies & Locations...")
        # 2. Extract & Insert Unique Companies
        new_companies = []
        for _, row in jobs_df.iterrows():
            c_name = str(row.get("company", "")).strip()
            c_ind = str(row.get("industry", "Information Technology")).strip()
            if c_name and c_name not in existing_companies:
                comp = Company(name=c_name, industry=c_ind)
                db.add(comp)
                existing_companies[c_name] = None  # placeholder
                new_companies.append(comp)

        if new_companies:
            db.commit()
            # Refresh IDs
            for comp in new_companies:
                existing_companies[comp.name] = comp.id
            stats["companies_created"] = len(new_companies)

        # 3. Extract & Insert Unique Locations
        new_locations = []
        for _, row in jobs_df.iterrows():
            loc_name = str(row.get("location", "Remote")).strip()
            country = str(row.get("country", "United States")).strip()
            key = (loc_name, country)
            if loc_name and key not in existing_locations:
                loc = Location(location_name=loc_name, country=country)
                db.add(loc)
                existing_locations[key] = None  # placeholder
                new_locations.append(loc)

        if new_locations:
            db.commit()
            for loc in new_locations:
                existing_locations[(loc.location_name, loc.country)] = loc.id
            stats["locations_created"] = len(new_locations)

        # 4. Extract & Insert Unique Skills
        print("Ingesting Skills Dictionary...")
        unique_skill_names = skills_df["skill_name"].dropna().unique()
        new_skills = []
        for s_name in unique_skill_names:
            s_clean = str(s_name).strip()
            if s_clean and s_clean not in existing_skills:
                sk = Skill(skill_name=s_clean, category="Technical")
                db.add(sk)
                existing_skills[s_clean] = None
                new_skills.append(sk)

        if new_skills:
            db.commit()
            for sk in new_skills:
                existing_skills[sk.skill_name] = sk.id
            stats["skills_created"] = len(new_skills)

        # 5. Insert Jobs (avoiding existing job_id duplicates)
        print("Ingesting Job Postings...")
        job_id_to_db_id = dict(existing_job_ids)
        jobs_to_insert = []

        for _, row in jobs_df.iterrows():
            j_id = str(row["job_id"]).strip()
            if j_id in existing_job_ids:
                stats["jobs_skipped_duplicate"] += 1
                continue

            c_name = str(row.get("company", "")).strip()
            loc_name = str(row.get("location", "Remote")).strip()
            country = str(row.get("country", "United States")).strip()

            comp_id = existing_companies.get(c_name)
            loc_id = existing_locations.get((loc_name, country))

            # Parse posting date
            p_date_raw = str(row.get("posting_date", ""))
            try:
                p_date = datetime.strptime(p_date_raw, "%Y-%m-%d").date()
            except ValueError:
                p_date = datetime.now().date()

            job_obj = Job(
                job_id=j_id,
                job_title=str(row.get("job_title", "")).strip(),
                raw_job_title=str(row.get("raw_job_title", "")).strip(),
                seniority_level=str(row.get("seniority_level", "Mid-level")).strip(),
                company_id=comp_id,
                location_id=loc_id,
                employment_type=str(row.get("employment_type", "Full-time")).strip(),
                experience_level=str(row.get("experience_level", "Mid-level")).strip(),
                remote_type=str(row.get("remote_type", "On-site")).strip(),
                salary_min=float(row["salary_min"]) if pd.notna(row.get("salary_min")) else None,
                salary_max=float(row["salary_max"]) if pd.notna(row.get("salary_max")) else None,
                salary_currency=str(row.get("salary_currency", "USD")).strip(),
                salary_is_imputed=bool(row.get("salary_is_imputed", False)),
                description=str(row.get("description", "")),
                education=str(row.get("education", "Unspecified")),
                posting_date=p_date,
                is_synthetic=bool(row.get("is_synthetic", True)),
            )
            jobs_to_insert.append(job_obj)

        if jobs_to_insert:
            db.bulk_save_objects(jobs_to_insert)
            db.commit()
            stats["jobs_inserted"] = len(jobs_to_insert)
            
            # Re-fetch database IDs for inserted job_ids
            refetched_jobs = db.query(Job.job_id, Job.id).all()
            job_id_to_db_id = {j.job_id: j.id for j in refetched_jobs}

        # 6. Insert JobSkills Mapping
        print("Ingesting Job-Skills Mapping...")
        job_skills_to_insert = []
        existing_js_keys = set(
            (js.job_id, js.skill_id) for js in db.query(JobSkill.job_id, JobSkill.skill_id).all()
        )

        for _, row in skills_df.iterrows():
            j_id = str(row["job_id"]).strip()
            s_name = str(row["skill_name"]).strip()

            db_job_id = job_id_to_db_id.get(j_id)
            db_skill_id = existing_skills.get(s_name)

            if db_job_id and db_skill_id:
                key = (db_job_id, db_skill_id)
                if key not in existing_js_keys:
                    job_skills_to_insert.append(
                        JobSkill(
                            job_id=db_job_id,
                            skill_id=db_skill_id,
                            source=str(row.get("source", "required_skills")),
                            is_normalized=bool(row.get("is_normalized", True)),
                        )
                    )
                    existing_js_keys.add(key)

        if job_skills_to_insert:
            db.bulk_save_objects(job_skills_to_insert)
            db.commit()
            stats["job_skills_inserted"] = len(job_skills_to_insert)

        print("-" * 60)
        print("DATA IMPORT COMPLETED SUCCESSFULLY")
        print("-" * 60)
        print(f"Jobs Inserted          : {stats['jobs_inserted']:,}")
        print(f"Jobs Skipped (Duplicate): {stats['jobs_skipped_duplicate']:,}")
        print(f"Companies Created      : {stats['companies_created']:,}")
        print(f"Locations Created      : {stats['locations_created']:,}")
        print(f"Skills Created         : {stats['skills_created']:,}")
        print(f"Job Skills Inserted    : {stats['job_skills_inserted']:,}")
        print("=" * 60)

        return stats

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database import: {e}")
        raise e
    finally:
        db.close()


def main():
    """CLI entry point for data import."""
    import_processed_data()


if __name__ == "__main__":
    main()
