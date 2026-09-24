"""
Unit tests for data cleaner module (backend/app/processing/cleaner.py).
"""

import pytest
import pandas as pd
import numpy as np
from app.processing.cleaner import DataCleaner


def test_remove_duplicates():
    cleaner = DataCleaner()
    raw_data = [
        {"job_id": "JOB-1", "job_title": "Dev", "company": "A", "location": "NY", "posting_date": "2025-01-01"},
        {"job_id": "JOB-1", "job_title": "Dev", "company": "A", "location": "NY", "posting_date": "2025-01-01"},  # Exact Duplicate ID
        {"job_id": "JOB-2", "job_title": "Dev", "company": "A", "location": "NY", "posting_date": "2025-01-01"},  # Duplicate Content
        {"job_id": "JOB-3", "job_title": "QA", "company": "B", "location": "SF", "posting_date": "2025-01-02"},
    ]
    df = pd.DataFrame(raw_data)
    clean_df = cleaner.remove_duplicates(df)

    assert len(clean_df) == 2
    assert cleaner.stats["removed_duplicates"] == 2
    assert set(clean_df["job_id"]) == {"JOB-1", "JOB-3"}


def test_clean_salaries_swap_inverted():
    cleaner = DataCleaner()
    df = pd.DataFrame([
        {"job_id": "JOB-1", "experience_level": "Senior", "salary_min": 150000.0, "salary_max": 90000.0}
    ])
    clean_df = cleaner.clean_salaries(df)

    assert clean_df.loc[0, "salary_min"] == 90000.0
    assert clean_df.loc[0, "salary_max"] == 150000.0
    assert cleaner.stats["inverted_salaries_swapped"] == 1


def test_clean_salaries_imputation():
    cleaner = DataCleaner()
    df = pd.DataFrame([
        {"job_id": "1", "experience_level": "Senior", "salary_min": 100000.0, "salary_max": np.nan},
        {"job_id": "2", "experience_level": "Junior", "salary_min": np.nan, "salary_max": 80000.0},
        {"job_id": "3", "experience_level": "Mid-level", "salary_min": np.nan, "salary_max": np.nan},
    ])
    clean_df = cleaner.clean_salaries(df)

    # Missing max -> min * 1.25
    assert clean_df.loc[0, "salary_max"] == 125000.0
    # Missing min -> max * 0.8
    assert clean_df.loc[1, "salary_min"] == 64000.0
    # Both missing -> Imputed
    assert clean_df.loc[2, "salary_min"] > 0
    assert clean_df.loc[2, "salary_max"] > clean_df.loc[2, "salary_min"]
    assert bool(clean_df["salary_is_imputed"].any()) is True


def test_handle_missing_values():
    cleaner = DataCleaner()
    df = pd.DataFrame([
        {"education": np.nan, "required_skills": np.nan, "location": np.nan}
    ])
    clean_df = cleaner.handle_missing_values(df)

    assert clean_df.loc[0, "education"] == "Unspecified"
    assert clean_df.loc[0, "required_skills"] == ""
    assert clean_df.loc[0, "location"] == "Remote"
