"""
Data Cleaning Module for Job Market Analytics.

Handles:
- Duplicate record identification and removal
- Missing-value handling & salary imputation
- Salary validation (swapping min > max anomalies, checking ranges)
- Date formatting & parsing
- Data-type casting and string whitespace trimming
"""

from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np


class DataCleaner:
    """Class encapsulating data cleaning operations."""

    def __init__(self):
        self.stats: Dict[str, Any] = {
            "initial_records": 0,
            "removed_duplicates": 0,
            "missing_salary_imputed": 0,
            "inverted_salaries_swapped": 0,
            "missing_education_filled": 0,
            "missing_skills_filled": 0,
            "missing_location_filled": 0,
            "cleaned_records": 0,
        }

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify and remove duplicate records by job_id or core post content.

        Args:
            df: Raw input DataFrame

        Returns:
            pd.DataFrame: Deduplicated DataFrame
        """
        initial_count = len(df)
        
        # Deduplicate first by job_id if present
        if "job_id" in df.columns:
            df_clean = df.drop_duplicates(subset=["job_id"], keep="first").copy()
        else:
            df_clean = df.copy()
        
        # Deduplicate by key text combination available
        dedup_subset = [c for c in ["job_title", "company", "location", "posting_date"] if c in df_clean.columns]
        if dedup_subset:
            df_clean = df_clean.drop_duplicates(subset=dedup_subset, keep="first")

        removed_count = initial_count - len(df_clean)
        self.stats["removed_duplicates"] = removed_count
        return df_clean

    def clean_salaries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and impute missing or anomalous salary fields.

        Decision Rationale:
        1. If salary_min > salary_max: swap values to correct inverted input errors.
        2. If one salary boundary is missing: calculate the missing boundary using standard ratio (1.25x / 0.80x).
        3. If both salaries are missing: impute median salary by experience_level and set `salary_is_imputed` flag.
        """
        df = df.copy()

        # Ensure numeric float type
        if "salary_min" in df.columns:
            df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
        else:
            df["salary_min"] = np.nan

        if "salary_max" in df.columns:
            df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")
        else:
            df["salary_max"] = np.nan

        # Track salary imputation flag
        df["salary_is_imputed"] = False

        # 1. Swap min > max inverted salaries
        inverted_mask = (df["salary_min"].notna()) & (df["salary_max"].notna()) & (df["salary_min"] > df["salary_max"])
        num_inverted = int(inverted_mask.sum())
        if num_inverted > 0:
            df.loc[inverted_mask, ["salary_min", "salary_max"]] = df.loc[inverted_mask, ["salary_max", "salary_min"]].values
            self.stats["inverted_salaries_swapped"] = num_inverted

        # 2. Impute single missing salary boundaries
        min_missing_max_present = df["salary_min"].isna() & df["salary_max"].notna()
        max_missing_min_present = df["salary_max"].isna() & df["salary_min"].notna()

        df.loc[min_missing_max_present, "salary_min"] = (df.loc[min_missing_max_present, "salary_max"] * 0.80).round(-3)
        df.loc[min_missing_max_present, "salary_is_imputed"] = True

        df.loc[max_missing_min_present, "salary_max"] = (df.loc[max_missing_min_present, "salary_min"] * 1.25).round(-3)
        df.loc[max_missing_min_present, "salary_is_imputed"] = True

        # 3. Impute both missing salaries using median by experience level
        both_missing = df["salary_min"].isna() & df["salary_max"].isna()
        num_both_missing = int(both_missing.sum())
        self.stats["missing_salary_imputed"] = num_both_missing

        if num_both_missing > 0:
            if "experience_level" in df.columns:
                exp_medians_min = df.groupby("experience_level")["salary_min"].transform("median")
                exp_medians_max = df.groupby("experience_level")["salary_max"].transform("median")
            else:
                exp_medians_min = pd.Series(75000.0, index=df.index)
                exp_medians_max = pd.Series(115000.0, index=df.index)

            global_median_min = df["salary_min"].median() if df["salary_min"].notna().any() else 75000.0
            global_median_max = df["salary_max"].median() if df["salary_max"].notna().any() else 115000.0

            df.loc[both_missing, "salary_min"] = exp_medians_min.loc[both_missing].fillna(global_median_min)
            df.loc[both_missing, "salary_max"] = exp_medians_max.loc[both_missing].fillna(global_median_max)
            df.loc[both_missing, "salary_is_imputed"] = True

        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill non-salary missing fields with documented default placeholders."""
        df = df.copy()

        def is_missing_series(s: pd.Series) -> pd.Series:
            return s.isna() | s.astype(str).str.strip().str.lower().isin(["nan", "none", "null", ""])

        for col in ["education", "required_skills", "location"]:
            if col in df.columns:
                df[col] = df[col].astype(object)

        if "education" in df.columns:
            edu_missing = is_missing_series(df["education"])
            self.stats["missing_education_filled"] = int(edu_missing.sum())
            df.loc[edu_missing, "education"] = "Unspecified"
        else:
            df["education"] = "Unspecified"

        if "required_skills" in df.columns:
            skills_missing = is_missing_series(df["required_skills"])
            self.stats["missing_skills_filled"] = int(skills_missing.sum())
            df.loc[skills_missing, "required_skills"] = ""
        else:
            df["required_skills"] = ""

        if "location" in df.columns:
            loc_missing = is_missing_series(df["location"])
            self.stats["missing_location_filled"] = int(loc_missing.sum())
            df.loc[loc_missing, "location"] = "Remote"
        else:
            df["location"] = "Remote"

        return df

    def clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse posting_date column to standardized ISO YYYY-MM-DD date format."""
        df = df.copy()
        if "posting_date" in df.columns:
            df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            df["posting_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")

        df["posting_date"] = df["posting_date"].fillna(pd.Timestamp.now().strftime("%Y-%m-%d"))
        return df

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run complete data cleaning workflow.

        Args:
            df: Raw job postings DataFrame

        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        self.stats["initial_records"] = len(df)
        
        # 1. Remove duplicates
        df_clean = self.remove_duplicates(df)

        # 2. Handle non-salary missing values BEFORE string casting
        df_clean = self.handle_missing_values(df_clean)

        # 3. Clean salaries
        df_clean = self.clean_salaries(df_clean)

        # 4. Trim string columns
        string_cols = df_clean.select_dtypes(include=["object"]).columns
        for col in string_cols:
            df_clean[col] = df_clean[col].astype(str).str.strip()

        # 5. Clean and parse dates
        df_clean = self.clean_dates(df_clean)

        self.stats["cleaned_records"] = len(df_clean)
        return df_clean
