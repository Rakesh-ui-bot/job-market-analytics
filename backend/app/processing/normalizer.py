"""
Data Normalization Module for Job Market Analytics.

Provides normalization functions for:
- Skill names (mapping aliases/variations to canonical skills)
- Job titles & Seniority levels
- Locations & Country names
- Employment types
- Experience levels
- Remote work types
"""

import re
from typing import Dict, Tuple, Optional


# Canonical Skill Mapping Dictionary (alias -> canonical name)
CANONICAL_SKILL_MAP: Dict[str, str] = {
    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "redux": "Redux",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "nextjs": "Next.js",
    "next.js": "Next.js",

    # Backend & Programming Languages
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "kotlin": "Kotlin",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",

    # Backend Frameworks
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",

    # Databases & Data Tools
    "sql": "SQL",
    "structured query language": "SQL",
    "mysql": "MySQL",
    "my sql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "excel": "Excel",

    # DevOps & Cloud
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "linux": "Linux",
    "bash": "Bash",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",

    # Tools & Methodologies
    "git": "Git",
    "github": "GitHub",
    "jira": "Jira",
    "agile": "Agile",
    "scrum": "Scrum",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "graphql": "GraphQL",
    "selenium": "Selenium",
    "postman": "Postman",
    "pytest": "PyTest",
}

# Standard Employment Types Map
EMPLOYMENT_TYPE_MAP: Dict[str, str] = {
    "full-time": "Full-time",
    "full time": "Full-time",
    "full_time": "Full-time",
    "part-time": "Part-time",
    "part time": "Part-time",
    "part_time": "Part-time",
    "contract": "Contract",
    "contractor": "Contract",
    "freelance": "Contract",
    "internship": "Internship",
    "intern": "Internship",
}

# Standard Remote Types Map
REMOTE_TYPE_MAP: Dict[str, str] = {
    "remote": "Remote",
    "full remote": "Remote",
    "fully remote": "Remote",
    "hybrid": "Hybrid",
    "on-site": "On-site",
    "onsite": "On-site",
    "in-office": "On-site",
}

# Standard Experience Levels Map
EXPERIENCE_LEVEL_MAP: Dict[str, str] = {
    "entry-level": "Entry-level",
    "entry level": "Entry-level",
    "junior": "Junior",
    "mid-level": "Mid-level",
    "mid level": "Mid-level",
    "intermediate": "Mid-level",
    "senior": "Senior",
    "lead": "Lead",
    "principal": "Lead",
    "executive": "Executive",
    "director": "Executive",
}


def normalize_skill(skill_raw: str) -> str:
    """
    Normalize raw skill string to canonical skill name.

    Args:
        skill_raw: Raw skill string (e.g. 'ReactJS', 'postgres', '  python ')

    Returns:
        str: Canonical skill name (e.g. 'React', 'PostgreSQL', 'Python')
    """
    if not skill_raw or not isinstance(skill_raw, str):
        return ""

    cleaned = skill_raw.strip().lower()

    if cleaned in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[cleaned]

    # Default fallback: Title Case trimmed string
    return skill_raw.strip().title()


def normalize_employment_type(emp_type_raw: Optional[str]) -> str:
    """Standardize employment type string."""
    if not emp_type_raw or not isinstance(emp_type_raw, str):
        return "Full-time"
    cleaned = emp_type_raw.strip().lower()
    return EMPLOYMENT_TYPE_MAP.get(cleaned, emp_type_raw.strip().title())


def normalize_remote_type(remote_raw: Optional[str]) -> str:
    """Standardize remote work type string."""
    if not remote_raw or not isinstance(remote_raw, str):
        return "On-site"
    cleaned = remote_raw.strip().lower()
    return REMOTE_TYPE_MAP.get(cleaned, remote_raw.strip().title())


def normalize_experience_level(exp_raw: Optional[str]) -> str:
    """Standardize experience level string."""
    if not exp_raw or not isinstance(exp_raw, str):
        return "Mid-level"
    cleaned = exp_raw.strip().lower()
    return EXPERIENCE_LEVEL_MAP.get(cleaned, exp_raw.strip().title())


def normalize_location(location_raw: Optional[str], country_raw: Optional[str] = None) -> str:
    """
    Standardize location format (e.g., 'New York, NY', 'San Francisco, CA').

    Args:
        location_raw: Raw location string
        country_raw: Optional country name string

    Returns:
        str: Standardized location string
    """
    if not location_raw or not isinstance(location_raw, str) or location_raw.strip().lower() in ["nan", "none", "unknown", ""]:
        if country_raw and isinstance(country_raw, str) and country_raw.strip():
            return f"Remote, {country_raw.strip()}"
        return "Remote"

    loc = location_raw.strip()

    # Normalization mappings for common variants
    location_aliases = {
        "new york": "New York, NY",
        "ny, usa": "New York, NY",
        "new york, ny": "New York, NY",
        "san francisco": "San Francisco, CA",
        "san francisco, california": "San Francisco, CA",
        "san francisco, ca": "San Francisco, CA",
        "austin": "Austin, TX",
        "austin, texas": "Austin, TX",
        "austin, tx": "Austin, TX",
        "seattle": "Seattle, WA",
        "london": "London, UK",
        "london, england": "London, UK",
        "london, uk": "London, UK",
        "bangalore": "Bengaluru, India",
        "bengaluru": "Bengaluru, India",
        "bengaluru, ka": "Bengaluru, India",
        "toronto": "Toronto, ON",
        "toronto, canada": "Toronto, ON",
        "toronto, on": "Toronto, ON",
        "berlin": "Berlin, Germany",
        "berlin, germany": "Berlin, Germany",
    }

    cleaned_key = loc.lower()
    if cleaned_key in location_aliases:
        return location_aliases[cleaned_key]

    return loc


def normalize_job_title(title_raw: Optional[str]) -> Tuple[str, str]:
    """
    Standardize job title into standard role category and extracted seniority level.

    Args:
        title_raw: Raw job title (e.g., 'Senior Python Developer')

    Returns:
        Tuple[str, str]: (standardized_title, seniority_level)
    """
    if not title_raw or not isinstance(title_raw, str):
        return ("Software Engineer", "Mid-level")

    title = title_raw.strip()
    title_lower = title.lower()

    # Detect Seniority Level
    seniority = "Mid-level"
    if any(term in title_lower for term in ["senior", "sr.", "sr"]):
        seniority = "Senior"
    elif any(term in title_lower for term in ["junior", "jr.", "jr", "entry"]):
        seniority = "Junior"
    elif any(term in title_lower for term in ["lead", "principal", "staff"]):
        seniority = "Lead"
    elif any(term in title_lower for term in ["intern", "trainee"]):
        seniority = "Entry-level"

    # Standard Role Categories
    standard_roles = [
        ("Frontend Developer", ["frontend", "front-end", "front end", "react developer", "vue developer", "angular developer"]),
        ("Backend Developer", ["backend", "back-end", "back end", "python developer", "node developer", "java developer"]),
        ("Full Stack Developer", ["full stack", "fullstack", "full-stack"]),
        ("Data Scientist", ["data scientist", "machine learning engineer", "ai engineer", "ml engineer"]),
        ("Data Analyst", ["data analyst", "bi analyst", "analytics engineer"]),
        ("DevOps Engineer", ["devops", "site reliability", "sre", "cloud engineer", "infrastructure"]),
        ("Android Developer", ["android", "mobile developer", "ios developer"]),
        ("QA Engineer", ["qa", "quality assurance", "test engineer", "automation engineer"]),
        ("Software Engineer", ["software engineer", "software developer", "developer", "engineer"]),
    ]

    for role_name, keywords in standard_roles:
        if any(kw in title_lower for kw in keywords):
            return (role_name, seniority)

    return (title.title(), seniority)
