import os
from pathlib import Path

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Dataset configuration
RAW_DATASET_FILE = RAW_DATA_DIR / "synthetic_job_postings.csv"
MIN_POSTING_RECORDS = 5000

# Database Configuration (placeholders for Phase 3)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "job_market_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
