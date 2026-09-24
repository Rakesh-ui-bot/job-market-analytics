"""
Salary Analytics Module.

Performs statistical analysis (average, median, min, max, std dev, 25th/75th percentiles)
using Pandas and NumPy on job compensation data.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Job, Location


def get_salary_summary_statistics(db: Session, currency: str = "USD") -> Dict[str, Any]:
    """
    Compute comprehensive summary statistics for job salaries using Pandas & NumPy.

    Returns:
        dict: Detailed statistical metrics (average, median, min, max, std_dev, 25th & 75th percentiles)
    """
    # Fetch raw salary min and max data
    query = (
        db.query(Job.salary_min, Job.salary_max)
        .filter(Job.salary_currency == currency)
        .filter(Job.salary_min.isnot(None))
        .filter(Job.salary_max.isnot(None))
    )
    
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        return {}

    df["salary_midpoint"] = (df["salary_min"] + df["salary_max"]) / 2.0

    midpoints = df["salary_midpoint"].values
    mins = df["salary_min"].values
    maxs = df["salary_max"].values

    return {
        "currency": currency,
        "sample_size": len(df),
        "midpoint_metrics": {
            "average": round(float(np.mean(midpoints)), 2),
            "median": round(float(np.median(midpoints)), 2),
            "minimum": round(float(np.min(midpoints)), 2),
            "maximum": round(float(np.max(midpoints)), 2),
            "std_dev": round(float(np.std(midpoints)), 2),
            "percentile_25": round(float(np.percentile(midpoints, 25)), 2),
            "percentile_75": round(float(np.percentile(midpoints, 75)), 2),
        },
        "salary_min_metrics": {
            "average": round(float(np.mean(mins)), 2),
            "median": round(float(np.median(mins)), 2),
            "minimum": round(float(np.min(mins)), 2),
            "maximum": round(float(np.max(mins)), 2),
        },
        "salary_max_metrics": {
            "average": round(float(np.mean(maxs)), 2),
            "median": round(float(np.median(maxs)), 2),
            "minimum": round(float(np.min(maxs)), 2),
            "maximum": round(float(np.max(maxs)), 2),
        },
    }


def get_salary_by_role(db: Session, currency: str = "USD") -> List[Dict[str, Any]]:
    """Get salary analytics grouped by job_title."""
    query = (
        db.query(Job.job_title, Job.salary_min, Job.salary_max)
        .filter(Job.salary_currency == currency)
        .filter(Job.salary_min.isnot(None))
    )
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        return []

    df["salary_mid"] = (df["salary_min"] + df["salary_max"]) / 2.0

    grouped = (
        df.groupby("job_title")
        .agg(
            job_count=("salary_mid", "count"),
            avg_salary_min=("salary_min", "mean"),
            avg_salary_max=("salary_max", "mean"),
            median_salary=("salary_mid", "median"),
            avg_midpoint_salary=("salary_mid", "mean"),
        )
        .reset_index()
        .sort_values(by="avg_midpoint_salary", ascending=False)
    )

    return [
        {
            "job_title": row["job_title"],
            "job_count": int(row["job_count"]),
            "avg_salary_min": round(float(row["avg_salary_min"]), 2),
            "avg_salary_max": round(float(row["avg_salary_max"]), 2),
            "median_salary": round(float(row["median_salary"]), 2),
            "avg_midpoint_salary": round(float(row["avg_midpoint_salary"]), 2),
        }
        for _, row in grouped.iterrows()
    ]


def get_salary_by_experience(db: Session, currency: str = "USD") -> List[Dict[str, Any]]:
    """Get salary analytics grouped by experience level."""
    query = (
        db.query(Job.experience_level, Job.salary_min, Job.salary_max)
        .filter(Job.salary_currency == currency)
        .filter(Job.salary_min.isnot(None))
    )
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        return []

    df["salary_mid"] = (df["salary_min"] + df["salary_max"]) / 2.0

    grouped = (
        df.groupby("experience_level")
        .agg(
            job_count=("salary_mid", "count"),
            avg_salary_min=("salary_min", "mean"),
            avg_salary_max=("salary_max", "mean"),
            median_salary=("salary_mid", "median"),
            avg_midpoint_salary=("salary_mid", "mean"),
        )
        .reset_index()
        .sort_values(by="avg_midpoint_salary", ascending=False)
    )

    return [
        {
            "experience_level": row["experience_level"],
            "job_count": int(row["job_count"]),
            "avg_salary_min": round(float(row["avg_salary_min"]), 2),
            "avg_salary_max": round(float(row["avg_salary_max"]), 2),
            "median_salary": round(float(row["median_salary"]), 2),
            "avg_midpoint_salary": round(float(row["avg_midpoint_salary"]), 2),
        }
        for _, row in grouped.iterrows()
    ]


def get_salary_by_location(
    db: Session, currency: str = "USD", min_jobs: int = 5
) -> List[Dict[str, Any]]:
    """Get salary analytics grouped by location."""
    query = (
        db.query(Location.location_name, Location.country, Job.salary_min, Job.salary_max)
        .join(Job, Location.id == Job.location_id)
        .filter(Job.salary_currency == currency)
        .filter(Job.salary_min.isnot(None))
    )
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        return []

    df["salary_mid"] = (df["salary_min"] + df["salary_max"]) / 2.0

    grouped = (
        df.groupby(["location_name", "country"])
        .agg(
            job_count=("salary_mid", "count"),
            avg_salary_min=("salary_min", "mean"),
            avg_salary_max=("salary_max", "mean"),
            median_salary=("salary_mid", "median"),
            avg_midpoint_salary=("salary_mid", "mean"),
        )
        .reset_index()
    )

    filtered = grouped[grouped["job_count"] >= min_jobs].sort_values(
        by="avg_midpoint_salary", ascending=False
    )

    return [
        {
            "location_name": row["location_name"],
            "country": row["country"],
            "job_count": int(row["job_count"]),
            "avg_salary_min": round(float(row["avg_salary_min"]), 2),
            "avg_salary_max": round(float(row["avg_salary_max"]), 2),
            "median_salary": round(float(row["median_salary"]), 2),
            "avg_midpoint_salary": round(float(row["avg_midpoint_salary"]), 2),
        }
        for _, row in filtered.iterrows()
    ]
