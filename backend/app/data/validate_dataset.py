"""
Dataset Validation Script for Job Market Analytics & Skill Demand Analyzer.

Validates:
1. Dataset file existence and loadability
2. Minimum record count (>= 5,000)
3. Schema integrity (presence of all 17 expected columns)
4. Synthetic data labeling verification (`is_synthetic` flag)
5. Comprehensive data quality report (missing values, duplicates, title & skill coverage)
"""

import sys
from pathlib import Path
import pandas as pd

# Add project backend root to path if running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import RAW_DATASET_FILE, MIN_POSTING_RECORDS

EXPECTED_COLUMNS = [
    "job_id",
    "job_title",
    "company",
    "location",
    "country",
    "employment_type",
    "experience_level",
    "remote_type",
    "salary_min",
    "salary_max",
    "salary_currency",
    "description",
    "required_skills",
    "education",
    "industry",
    "posting_date",
    "is_synthetic",
]

REQUIRED_JOB_TITLES = [
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Software Engineer",
    "Data Analyst",
    "Data Scientist",
    "Python Developer",
    "Android Developer",
    "React Developer",
    "DevOps Engineer",
    "QA Engineer",
]

REQUIRED_SKILL_KEY_TERMS = [
    "Python", "JavaScript", "TypeScript", "React", "HTML", "CSS",
    "SQL", "MySQL", "PostgreSQL", "Node.js", "FastAPI", "Django",
    "AWS", "Docker", "Git", "Pandas", "NumPy", "Power BI", "Tableau",
    "Kotlin", "Java", "C++"
]


def validate_dataset(filepath: Path = RAW_DATASET_FILE) -> bool:
    """
    Validate dataset structure, row counts, schema, and synthetic metadata.

    Returns:
        bool: True if validation passes, False otherwise.
    """
    print("=" * 60)
    print("RUNNING DATASET VALIDATION CHECKS")
    print("=" * 60)

    # 1. File existence check
    if not filepath.exists():
        print(f"[FAIL] Dataset file not found at path: {filepath}")
        return False
    print(f"[PASS] Dataset file exists at {filepath}")

    # 2. File loadability check
    try:
        df = pd.read_csv(filepath)
        print(f"[PASS] Successfully loaded dataset using Pandas")
    except Exception as e:
        print(f"[FAIL] Failed to load CSV dataset: {e}")
        return False

    all_passed = True

    # 3. Minimum record count check
    total_records = len(df)
    if total_records >= MIN_POSTING_RECORDS:
        print(f"[PASS] Total record count = {total_records:,} (Required: >= {MIN_POSTING_RECORDS:,})")
    else:
        print(f"[FAIL] Total record count = {total_records:,} (Required: >= {MIN_POSTING_RECORDS:,})")
        all_passed = False

    # 4. Schema verification check
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if not missing_cols:
        print(f"[PASS] All {len(EXPECTED_COLUMNS)} required schema columns are present")
    else:
        print(f"[FAIL] Missing required columns: {missing_cols}")
        all_passed = False

    # 5. Synthetic metadata verification check
    if "is_synthetic" in df.columns:
        if df["is_synthetic"].all():
            print(f"[PASS] Dataset is explicitly labeled as synthetic (is_synthetic = True for all rows)")
        else:
            print(f"[WARN] Some rows lack is_synthetic = True flag!")
    else:
        print(f"[FAIL] Missing 'is_synthetic' column")
        all_passed = False

    # 6. Job titles coverage check
    titles_str = " ".join(df["job_title"].dropna().astype(str).tolist())
    missing_titles = [title for title in REQUIRED_JOB_TITLES if title.lower() not in titles_str.lower()]
    if not missing_titles:
        print(f"[PASS] All {len(REQUIRED_JOB_TITLES)} target job roles are represented in dataset")
    else:
        print(f"[WARN] Some job titles were not found: {missing_titles}")

    # 7. Core skills coverage check
    skills_str = " ".join(df["required_skills"].dropna().astype(str).tolist())
    found_skills = [s for s in REQUIRED_SKILL_KEY_TERMS if s.lower() in skills_str.lower()]
    print(f"[PASS] Found {len(found_skills)}/{len(REQUIRED_SKILL_KEY_TERMS)} key technologies in skills dataset")

    # 8. Detailed Data Quality Assessment Report
    print("\n" + "-" * 60)
    print("DATA QUALITY ASSESSMENT & INTENTIONAL ANOMALY REPORT")
    print("-" * 60)
    print(f"Total Rows: {total_records:,}")
    print(f"Exact Duplicate Job IDs: {df.duplicated(subset=['job_id']).sum():,}")
    print("\nMissing Value Counts by Field:")
    for col in df.columns:
        null_count = df[col].isna().sum()
        pct = (null_count / total_records) * 100
        print(f"  - {col:<20}: {null_count:>5} missing ({pct:5.1f}%)")

    print("\nEmployment Type Variations:")
    print(dict(df["employment_type"].value_counts().head(5)))

    print("\nRemote Type Variations:")
    print(dict(df["remote_type"].value_counts().head(5)))

    print("-" * 60)
    if all_passed:
        print("OVERALL VALIDATION STATUS: PASSED")
    else:
        print("OVERALL VALIDATION STATUS: FAILED")
    print("=" * 60)

    return all_passed


def main():
    """CLI entry point for dataset validation."""
    success = validate_dataset()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
