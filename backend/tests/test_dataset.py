"""
Unit tests for synthetic dataset generation and validation.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Ensure backend root is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data.generate_dataset import generate_dataset, generate_single_record
from app.data.validate_dataset import validate_dataset
from app.config import RAW_DATASET_FILE


def test_generate_single_record():
    """Test generating a single synthetic record structure and synthetic flag."""
    record = generate_single_record(1)
    assert isinstance(record, dict)
    assert record["is_synthetic"] is True
    assert "job_id" in record
    assert "job_title" in record
    assert "required_skills" in record


def test_generate_dataset_structure():
    """Test generating a small batch of synthetic records."""
    df = generate_dataset(num_records=100, duplicate_percentage=0.05)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 100
    assert df["is_synthetic"].all() is np_bool_true(True) or df["is_synthetic"].all() == True
    assert "salary_min" in df.columns
    assert "salary_max" in df.columns


def test_validate_generated_dataset():
    """Test full dataset validation against raw CSV file if present."""
    if RAW_DATASET_FILE.exists():
        is_valid = validate_dataset(RAW_DATASET_FILE)
        assert is_valid is True
    else:
        pytest.skip("Dataset CSV file not generated yet.")


def np_bool_true(val):
    return val is True or bool(val) is True
