"""
Dataset Generator for Job Market Analytics & Skill Demand Analyzer.

Generates a synthetic dataset of job postings containing realistic distributions,
intentional data quality issues (missing values, duplicate rows, casing inconsistencies),
and explicit synthetic tagging (`is_synthetic = True`).
"""

import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Add project backend root to path if running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import RAW_DATASET_FILE, RAW_DATA_DIR


# Define domain constants
JOB_TITLES = [
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

TITLE_PREFIXES = ["", "", "", "Senior ", "Junior ", "Lead ", "Principal "]

COMPANIES = [
    "TechCorp Solutions",
    "DataPulse Analytics",
    "CloudScale Systems",
    "FinTech Dynamics",
    "Apex AI Labs",
    "CodeCraft Studio",
    "ByteWave Technologies",
    "InnoTech Global",
    "CyberGuard Networks",
    "DevStudio Inc",
    "Quantum Soft",
    "Vanguard Data",
    "Echo Software",
    "Nexus Cloud Services",
    "Synergy Systems",
]

LOCATIONS_BY_COUNTRY = {
    "United States": [
        ("New York, NY", "New York", "NY, USA"),
        ("San Francisco, CA", "San Francisco, California", "San Francisco"),
        ("Austin, TX", "Austin, Texas", "Austin"),
        ("Seattle, WA", "Seattle"),
    ],
    "United Kingdom": [
        ("London, UK", "London", "London, England"),
        ("Manchester, UK", "Manchester"),
    ],
    "India": [
        ("Bengaluru, KA", "Bengaluru", "Bangalore"),
        ("Hyderabad, TS", "Hyderabad"),
    ],
    "Canada": [
        ("Toronto, ON", "Toronto, Canada", "Toronto"),
        ("Vancouver, BC", "Vancouver"),
    ],
    "Germany": [
        ("Berlin, Germany", "Berlin"),
        ("Munich, Germany", "Munich"),
    ],
}

SKILL_POOL_BY_TITLE = {
    "Frontend Developer": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Vue.js", "Redux", "Tailwind CSS", "Git"],
    "Backend Developer": ["Python", "Java", "Node.js", "FastAPI", "Django", "SQL", "PostgreSQL", "MySQL", "Docker", "AWS", "Git"],
    "Full Stack Developer": ["JavaScript", "TypeScript", "React", "Python", "Node.js", "HTML", "CSS", "SQL", "PostgreSQL", "Docker", "Git"],
    "Software Engineer": ["Python", "Java", "C++", "SQL", "Git", "GitHub", "AWS", "Docker", "Data Structures", "OOP"],
    "Data Analyst": ["Python", "SQL", "Pandas", "NumPy", "Power BI", "Tableau", "Excel", "PostgreSQL", "Statistics"],
    "Data Scientist": ["Python", "Pandas", "NumPy", "SQL", "Scikit-Learn", "TensorFlow", "PyTorch", "Tableau", "Statistics", "Machine Learning"],
    "Python Developer": ["Python", "FastAPI", "Django", "Pandas", "NumPy", "SQL", "PostgreSQL", "Docker", "Git", "REST APIs"],
    "Android Developer": ["Kotlin", "Java", "Android SDK", "Git", "REST APIs", "SQLite", "Jetpack Compose", "Coroutines"],
    "React Developer": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Redux", "Next.js", "Node.js", "Git"],
    "DevOps Engineer": ["AWS", "Docker", "Kubernetes", "Linux", "Python", "Bash", "Terraform", "CI/CD", "Git", "GitHub"],
    "QA Engineer": ["Python", "Selenium", "Postman", "SQL", "Jira", "Automated Testing", "Git", "PyTest", "CI/CD"],
}

SKILL_CASING_VARIATIONS = {
    "Python": ["Python", "python", "PYTHON"],
    "React": ["React", "ReactJS", "react.js", "REACT"],
    "PostgreSQL": ["PostgreSQL", "postgres", "Postgresql"],
    "Node.js": ["Node.js", "NodeJS", "node"],
    "AWS": ["AWS", "Amazon Web Services", "aws"],
    "C++": ["C++", "cpp", "CPP"],
    "Git": ["Git", "git"],
    "SQL": ["SQL", "sql"],
    "JavaScript": ["JavaScript", "javascript", "JS"],
    "TypeScript": ["TypeScript", "typescript", "TS"],
}

EMPLOYMENT_TYPES = ["Full-time", "Full Time", "full_time", "Part-time", "Contract", "contractor", "Internship"]
EXPERIENCE_LEVELS = ["Entry-level", "Junior", "Mid-level", "Senior", "Lead", "Executive"]
REMOTE_TYPES = ["Remote", "Full Remote", "remote", "Hybrid", "hybrid", "On-site", "Onsite"]
EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "High School", "Associate's Degree"]
INDUSTRIES = ["Information Technology", "Financial Services", "Healthcare", "E-commerce", "Cybersecurity", "Automotive", "Education"]
CURRENCIES = ["USD", "EUR", "GBP", "INR", "CAD"]


def get_varied_skill(skill: str) -> str:
    """Randomly apply realistic casing variations to skill names."""
    if skill in SKILL_CASING_VARIATIONS and random.random() < 0.3:
        return random.choice(SKILL_CASING_VARIATIONS[skill])
    return skill


def generate_single_record(record_idx: int) -> dict:
    """Generate a single raw synthetic job posting record."""
    base_title = random.choice(JOB_TITLES)
    prefix = random.choice(TITLE_PREFIXES)
    job_title = f"{prefix}{base_title}".strip()

    company = random.choice(COMPANIES)
    country = random.choice(list(LOCATIONS_BY_COUNTRY.keys()))
    loc_options = random.choice(LOCATIONS_BY_COUNTRY[country])
    location = random.choice(loc_options)

    emp_type = random.choice(EMPLOYMENT_TYPES)
    exp_level = random.choice(EXPERIENCE_LEVELS)
    remote_type = random.choice(REMOTE_TYPES)
    industry = random.choice(INDUSTRIES)
    currency = random.choice(CURRENCIES)

    # Base salary ranges depending on experience level
    salary_range_map = {
        "Entry-level": (45000, 70000),
        "Junior": (50000, 80000),
        "Mid-level": (75000, 120000),
        "Senior": (110000, 170000),
        "Lead": (140000, 210000),
        "Executive": (180000, 280000),
    }

    min_b, max_b = salary_range_map.get(exp_level, (60000, 110000))

    # Currency conversion multipliers for realistic values
    curr_multiplier = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "CAD": 1.35,
        "INR": 83.0,
    }
    mult = curr_multiplier.get(currency, 1.0)

    salary_min = float(round(random.randint(min_b, max_b) * mult, -3))
    salary_max = float(round(salary_min + random.randint(15000, 50000) * mult, -3))

    # Data Quality Anomaly 1: Missing Salary (~12% missing min, ~15% missing max)
    if random.random() < 0.12:
        salary_min = np.nan
    if random.random() < 0.15:
        salary_max = np.nan

    # Skills generation
    base_skills = SKILL_POOL_BY_TITLE.get(base_title, ["Python", "SQL", "Git"])
    selected_skills = random.sample(base_skills, k=min(len(base_skills), random.randint(3, 6)))
    
    # Add random extra skills
    all_extra = ["AWS", "Docker", "Git", "Linux", "Agile", "Jira", "CI/CD", "REST APIs"]
    extra_skills = random.sample(all_extra, k=random.randint(1, 3))
    combined_skills = list(dict.fromkeys(selected_skills + extra_skills))
    
    varied_skills = [get_varied_skill(s) for s in combined_skills]
    
    # Data Quality Anomaly 2: Missing required_skills (~4%)
    if random.random() < 0.04:
        required_skills = np.nan
    else:
        required_skills = ", ".join(varied_skills)

    # Data Quality Anomaly 3: Missing education (~6%)
    if random.random() < 0.06:
        education = np.nan
    else:
        education = random.choice(EDUCATION_LEVELS)

    # Data Quality Anomaly 4: Missing location (~2%)
    if random.random() < 0.02:
        location = np.nan

    # Dates: past 180 days
    posting_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")

    description = (
        f"We are seeking a talented {job_title} to join our dynamic team at {company} in the {industry} sector. "
        f"In this role, you will work closely with cross-functional teams to build high-performance scalable systems. "
        f"Key requirements include hands-on experience with {', '.join(selected_skills[:3])}. "
        f"Strong communication skills and passion for technology are highly desired."
    )

    return {
        "job_id": f"JOB-{10000 + record_idx}",
        "job_title": job_title,
        "company": company,
        "location": location,
        "country": country,
        "employment_type": emp_type,
        "experience_level": exp_level,
        "remote_type": remote_type,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": currency,
        "description": description,
        "required_skills": required_skills,
        "education": education,
        "industry": industry,
        "posting_date": posting_date,
        "is_synthetic": True,
    }


def generate_dataset(num_records: int = 5500, duplicate_percentage: float = 0.03) -> pd.DataFrame:
    """
    Generate dataset with `num_records` unique rows and intentional duplicate rows.

    Args:
        num_records: Number of base unique records to generate (default: 5500).
        duplicate_percentage: Fraction of duplicate rows to inject (default: 3%).

    Returns:
        pd.DataFrame: Completed synthetic job postings DataFrame.
    """
    print(f"Generating {num_records} base synthetic job records...")
    records = [generate_single_record(i) for i in range(num_records)]

    df = pd.DataFrame(records)

    # Data Quality Anomaly 5: Duplicate records (~3%)
    num_duplicates = int(num_records * duplicate_percentage)
    if num_duplicates > 0:
        print(f"Injecting {num_duplicates} duplicate records for data quality testing...")
        dup_rows = df.sample(n=num_duplicates, replace=True, random_state=42)
        df = pd.concat([df, dup_rows], ignore_index=True)

    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    return df


def save_dataset(df: pd.DataFrame, output_path: Path = RAW_DATASET_FILE) -> Path:
    """Save DataFrame to target CSV path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df)} records to: {output_path}")
    return output_path


def main():
    """Execution entry point."""
    df = generate_dataset(num_records=5500, duplicate_percentage=0.03)
    save_dataset(df)
    
    # Print summary statistics
    print("\n" + "=" * 50)
    print("DATASET GENERATION SUMMARY")
    print("=" * 50)
    print(f"Total Records Created: {len(df)}")
    print(f"Synthetic Flag (is_synthetic): {df['is_synthetic'].all()} (100% Synthetic)")
    print(f"Columns: {list(df.columns)}")
    print("\nData Quality Inconsistencies Summary:")
    print(f"  - Missing salary_min: {df['salary_min'].isna().sum()} rows ({df['salary_min'].isna().mean():.1%})")
    print(f"  - Missing salary_max: {df['salary_max'].isna().sum()} rows ({df['salary_max'].isna().mean():.1%})")
    print(f"  - Missing education: {df['education'].isna().sum()} rows ({df['education'].isna().mean():.1%})")
    print(f"  - Missing required_skills: {df['required_skills'].isna().sum()} rows ({df['required_skills'].isna().mean():.1%})")
    print(f"  - Exact Duplicate Rows: {df.duplicated(subset=['job_id']).sum()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
