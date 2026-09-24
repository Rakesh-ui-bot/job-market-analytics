"""
Complete ETL Processing Pipeline for Job Market Analytics.

Orchestrates:
1. Raw Dataset Loading (`data/raw/synthetic_job_postings.csv`)
2. Data Cleaning & Deduplication (`DataCleaner`)
3. Data Normalization (Titles, Locations, Remote Types, Employment Types)
4. Skill Extraction & Normalization (`SkillExtractor`)
5. Output Generation (`data/processed/cleaned_jobs.csv` & `data/processed/job_skills.csv`)
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Ensure backend root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import RAW_DATASET_FILE, PROCESSED_DATA_DIR
from app.processing.cleaner import DataCleaner
from app.processing.normalizer import (
    normalize_job_title,
    normalize_location,
    normalize_employment_type,
    normalize_remote_type,
    normalize_experience_level,
)
from app.processing.skill_extractor import SkillExtractor


OUTPUT_CLEANED_JOBS = PROCESSED_DATA_DIR / "cleaned_jobs.csv"
OUTPUT_JOB_SKILLS = PROCESSED_DATA_DIR / "job_skills.csv"


def run_pipeline(
    raw_csv_path: Path = RAW_DATASET_FILE,
    cleaned_jobs_path: Path = OUTPUT_CLEANED_JOBS,
    job_skills_path: Path = OUTPUT_JOB_SKILLS,
) -> dict:
    """
    Execute complete end-to-end data processing pipeline.

    Returns:
        dict: Detailed execution statistics report
    """
    print("=" * 60)
    print("STARTING DATA PROCESSING PIPELINE (PHASE 2)")
    print("=" * 60)

    # 1. Load Raw Dataset
    if not raw_csv_path.exists():
        raise FileNotFoundError(f"Raw dataset file not found at: {raw_csv_path}")

    print(f"Loading raw dataset from: {raw_csv_path}")
    raw_df = pd.read_csv(raw_csv_path)
    input_count = len(raw_df)
    print(f"Loaded {input_count:,} raw records.")

    # 2. Data Cleaning
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean_dataframe(raw_df)
    clean_stats = cleaner.stats

    # 3. Data Normalization
    print("Normalizing job titles, locations, employment, and remote types...")
    title_results = cleaned_df["job_title"].apply(normalize_job_title)
    cleaned_df["raw_job_title"] = cleaned_df["job_title"]
    cleaned_df["job_title"] = [t[0] for t in title_results]
    cleaned_df["seniority_level"] = [t[1] for t in title_results]

    cleaned_df["location"] = cleaned_df.apply(
        lambda r: normalize_location(r["location"], r["country"]), axis=1
    )
    cleaned_df["employment_type"] = cleaned_df["employment_type"].apply(normalize_employment_type)
    cleaned_df["remote_type"] = cleaned_df["remote_type"].apply(normalize_remote_type)
    cleaned_df["experience_level"] = cleaned_df["experience_level"].apply(normalize_experience_level)

    # Reorder cleaned jobs columns
    job_columns_order = [
        "job_id",
        "job_title",
        "raw_job_title",
        "seniority_level",
        "company",
        "location",
        "country",
        "employment_type",
        "experience_level",
        "remote_type",
        "salary_min",
        "salary_max",
        "salary_currency",
        "salary_is_imputed",
        "description",
        "education",
        "industry",
        "posting_date",
        "is_synthetic",
    ]
    # Retain any extra columns present
    final_job_cols = [c for c in job_columns_order if c in cleaned_df.columns]
    cleaned_jobs_df = cleaned_df[final_job_cols].copy()

    # 4. Skill Extraction & Mapping Table Generation
    print("Extracting and normalising skills from required_skills and descriptions...")
    extractor = SkillExtractor()

    skill_rows = []
    for _, row in cleaned_df.iterrows():
        job_id = row["job_id"]
        req_skills_str = str(row.get("required_skills", ""))
        desc_text = str(row.get("description", ""))

        extracted = extractor.extract_all_skills(req_skills_str, desc_text)
        for item in extracted:
            skill_rows.append({
                "job_id": job_id,
                "skill_name": item["skill_name"],
                "source": item["source"],
                "is_normalized": item["is_normalized"],
            })

    job_skills_df = pd.DataFrame(skill_rows)

    # 5. Save Outputs to data/processed/
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    cleaned_jobs_df.to_csv(cleaned_jobs_path, index=False)
    print(f"Saved cleaned jobs dataset ({len(cleaned_jobs_df):,} rows) to: {cleaned_jobs_path}")

    job_skills_df.to_csv(job_skills_path, index=False)
    print(f"Saved job skills dataset ({len(job_skills_df):,} relations) to: {job_skills_path}")

    # 6. Pipeline Statistics Summary
    unique_skills_count = job_skills_df["skill_name"].nunique() if not job_skills_df.empty else 0
    top_skills_dict = job_skills_df["skill_name"].value_counts().head(10).to_dict() if not job_skills_df.empty else {}

    summary = {
        "input_record_count": input_count,
        "removed_duplicates": clean_stats["removed_duplicates"],
        "missing_salaries_imputed": clean_stats["missing_salary_imputed"],
        "missing_education_filled": clean_stats["missing_education_filled"],
        "missing_skills_filled": clean_stats["missing_skills_filled"],
        "missing_location_filled": clean_stats["missing_location_filled"],
        "inverted_salaries_swapped": clean_stats["inverted_salaries_swapped"],
        "output_record_count": len(cleaned_jobs_df),
        "total_skill_relations": len(job_skills_df),
        "number_of_unique_skills": unique_skills_count,
        "top_extracted_skills": top_skills_dict,
    }

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION SUMMARY REPORT")
    print("=" * 60)
    print(f"Input Record Count     : {summary['input_record_count']:,}")
    print(f"Removed Duplicates     : {summary['removed_duplicates']:,}")
    print(f"Output Record Count    : {summary['output_record_count']:,}")
    print(f"Missing Values Handled :")
    print(f"  - Salaries Imputed   : {summary['missing_salaries_imputed']:,}")
    print(f"  - Education Filled   : {summary['missing_education_filled']:,}")
    print(f"  - Skills Filled      : {summary['missing_skills_filled']:,}")
    print(f"  - Locations Filled   : {summary['missing_location_filled']:,}")
    print(f"  - Salaries Swapped   : {summary['inverted_salaries_swapped']:,}")
    print(f"Number of Unique Skills: {summary['number_of_unique_skills']:,}")
    print(f"Top Extracted Skills   :")
    for skill, count in summary["top_extracted_skills"].items():
        print(f"  - {skill:<18}: {count:,} occurrences")
    print("=" * 60)

    return summary


def main():
    """CLI entry point for processing pipeline."""
    run_pipeline()


if __name__ == "__main__":
    main()
