"""
Job Service Module.

Handles querying, filtering, pagination, and CSV file upload ingestion.
"""

from typing import Optional, Dict, Any, List
from math import ceil
from datetime import datetime, date
import io
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from fastapi import UploadFile, HTTPException, status

from app.database.models import Job, Company, Location, Skill, JobSkill
from app.schemas.jobs import JobSummarySchema, JobDetailSchema, PaginatedJobsResponse
from app.utils.filter_utils import apply_job_filters
from app.processing.cleaner import DataCleaner
from app.processing.normalizer import (
    normalize_job_title,
    normalize_location,
    normalize_employment_type,
    normalize_remote_type,
    normalize_experience_level,
)
from app.processing.skill_extractor import SkillExtractor


REQUIRED_CSV_COLUMNS = ["job_title", "company", "location"]


class JobService:

    @staticmethod
    def get_jobs(
        db: Session,
        page: int = 1,
        limit: int = 20,
        role: Optional[str] = None,
        skill: Optional[str] = None,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote_type: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> PaginatedJobsResponse:
        """
        Query job postings with multi-field filtering and pagination.
        """
        query = db.query(Job).options(
            joinedload(Job.company),
            joinedload(Job.location),
            joinedload(Job.job_skills).joinedload(JobSkill.skill),
        )

        # 1. Apply Filtering using filter_utils
        query = apply_job_filters(
            query,
            role=role,
            skill=skill,
            location=location,
            experience_level=experience_level,
            remote_type=remote_type,
            employment_type=employment_type,
            salary_min=salary_min,
            salary_max=salary_max,
            date_from=date_from,
            date_to=date_to,
        )

        # 2. Count Total Records
        total = query.distinct().count()

        # 3. Calculate Pagination bounds
        limit = max(1, min(limit, 100))
        page = max(1, page)
        pages = ceil(total / limit) if total > 0 else 1
        offset = (page - 1) * limit

        # 4. Fetch Page Items
        jobs = query.distinct().order_by(Job.id.desc()).offset(offset).limit(limit).all()

        items = []
        for job in jobs:
            skills_list = [js.skill.skill_name for js in job.job_skills if js.skill]
            items.append(
                JobSummarySchema(
                    id=job.id,
                    job_id=job.job_id,
                    job_title=job.job_title,
                    raw_job_title=job.raw_job_title,
                    seniority_level=job.seniority_level,
                    company=job.company.name if job.company else "Unknown",
                    location=job.location.location_name if job.location else "Remote",
                    country=job.location.country if job.location else "United States",
                    employment_type=job.employment_type,
                    experience_level=job.experience_level,
                    remote_type=job.remote_type,
                    salary_min=job.salary_min,
                    salary_max=job.salary_max,
                    salary_currency=job.salary_currency,
                    salary_is_imputed=job.salary_is_imputed,
                    posting_date=job.posting_date,
                    is_synthetic=job.is_synthetic,
                    skills=skills_list,
                )
            )

        return PaginatedJobsResponse(
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items,
        )

    @staticmethod
    def get_job_by_identifier(db: Session, identifier: str) -> Optional[JobDetailSchema]:
        """
        Fetch single job detail by integer primary key ID or string job_id.
        """
        query = db.query(Job).options(
            joinedload(Job.company),
            joinedload(Job.location),
            joinedload(Job.job_skills).joinedload(JobSkill.skill),
        )

        if identifier.isdigit():
            job = query.filter(Job.id == int(identifier)).first()
        else:
            job = query.filter(Job.job_id == identifier.strip()).first()

        if not job:
            return None

        skills_list = [js.skill.skill_name for js in job.job_skills if js.skill]

        return JobDetailSchema(
            id=job.id,
            job_id=job.job_id,
            job_title=job.job_title,
            raw_job_title=job.raw_job_title,
            seniority_level=job.seniority_level,
            company=job.company,
            location=job.location,
            employment_type=job.employment_type,
            experience_level=job.experience_level,
            remote_type=job.remote_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            salary_is_imputed=job.salary_is_imputed,
            description=job.description,
            education=job.education,
            posting_date=job.posting_date,
            is_synthetic=job.is_synthetic,
            created_at=job.created_at,
            skills=skills_list,
        )

    @staticmethod
    def process_csv_upload(db: Session, file: UploadFile) -> Dict[str, Any]:
        """
        Process, validate, clean, extract skills, and ingest an uploaded CSV file.
        """
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Uploaded file must be a .csv file.",
            )

        try:
            content = file.file.read()
            df_raw = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Malformed CSV file. Error parsing file content: {str(e)}",
            )

        # Validate Schema Columns
        missing_cols = [c for c in REQUIRED_CSV_COLUMNS if c not in df_raw.columns]
        if missing_cols:
            raise HTTPException(
                status_code=422,
                detail=f"Validation Error: Dataset is missing required columns: {missing_cols}",
            )

        records_read = len(df_raw)
        if records_read == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded CSV dataset contains 0 records.",
            )

        # 1. Clean Data
        cleaner = DataCleaner()

        # Add job_id if missing
        if "job_id" not in df_raw.columns:
            start_num = 80000 + db.query(Job.id).count()
            df_raw["job_id"] = [f"JOB-UPL-{start_num + i}" for i in range(records_read)]

        df_cleaned = cleaner.clean_dataframe(df_raw)
        duplicates_removed = cleaner.stats["removed_duplicates"]

        # 2. Normalize
        title_results = df_cleaned["job_title"].apply(normalize_job_title)
        df_cleaned["raw_job_title"] = df_cleaned["job_title"]
        df_cleaned["job_title"] = [t[0] for t in title_results]
        df_cleaned["seniority_level"] = [t[1] for t in title_results]

        if "country" not in df_cleaned.columns:
            df_cleaned["country"] = "United States"

        df_cleaned["location"] = df_cleaned.apply(
            lambda r: normalize_location(r["location"], r["country"]), axis=1
        )
        df_cleaned["employment_type"] = df_cleaned["employment_type"].apply(normalize_employment_type)
        df_cleaned["remote_type"] = df_cleaned["remote_type"].apply(normalize_remote_type)
        df_cleaned["experience_level"] = df_cleaned["experience_level"].apply(normalize_experience_level)

        # 3. Lookups Cache for DB Ingestion
        existing_companies = {c.name: c.id for c in db.query(Company).all()}
        existing_locations = {(l.location_name, l.country): l.id for l in db.query(Location).all()}
        existing_skills = {s.skill_name: s.id for s in db.query(Skill).all()}
        existing_job_ids = {j.job_id: j.id for j in db.query(Job.job_id, Job.id).all()}

        # 4. Companies & Locations Ingestion
        for _, row in df_cleaned.iterrows():
            c_name = str(row.get("company", "Unknown")).strip()
            c_ind = str(row.get("industry", "Information Technology")).strip()
            if c_name and c_name not in existing_companies:
                comp = Company(name=c_name, industry=c_ind)
                db.add(comp)
                db.commit()
                existing_companies[c_name] = comp.id

            loc_name = str(row.get("location", "Remote")).strip()
            country = str(row.get("country", "United States")).strip()
            key = (loc_name, country)
            if loc_name and key not in existing_locations:
                loc = Location(location_name=loc_name, country=country)
                db.add(loc)
                db.commit()
                existing_locations[key] = loc.id

        # 5. Job Postings Ingestion
        extractor = SkillExtractor()
        jobs_inserted = 0
        total_skills_extracted = 0

        for _, row in df_cleaned.iterrows():
            j_id = str(row["job_id"]).strip()
            if j_id in existing_job_ids:
                continue

            c_name = str(row.get("company", "Unknown")).strip()
            loc_name = str(row.get("location", "Remote")).strip()
            country = str(row.get("country", "United States")).strip()

            comp_id = existing_companies.get(c_name)
            loc_id = existing_locations.get((loc_name, country))

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
                is_synthetic=bool(row.get("is_synthetic", False)),
            )
            db.add(job_obj)
            db.commit()
            jobs_inserted += 1
            existing_job_ids[j_id] = job_obj.id

            # Skill extraction & mapping
            req_skills = str(row.get("required_skills", ""))
            desc_text = str(row.get("description", ""))
            extracted = extractor.extract_all_skills(req_skills, desc_text)

            for item in extracted:
                s_name = item["skill_name"]
                if s_name not in existing_skills:
                    sk = Skill(skill_name=s_name, category="Technical")
                    db.add(sk)
                    db.commit()
                    existing_skills[s_name] = sk.id

                s_id = existing_skills[s_name]
                js = JobSkill(job_id=job_obj.id, skill_id=s_id, source=item["source"])
                db.add(js)
                total_skills_extracted += 1

            db.commit()

        return {
            "status": "success",
            "filename": file.filename,
            "records_read": records_read,
            "duplicates_removed": duplicates_removed,
            "jobs_inserted": jobs_inserted,
            "skills_extracted": total_skills_extracted,
        }
