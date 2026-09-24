"""
Career Skill Gap Analyzer Module.

Compares user's current skills against skills commonly required for a target job role.

NOTE: This is a purely descriptive educational tool. It does NOT make hiring claims
or calculate hiring probability.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.analytics.roles import get_skills_per_role
from app.analytics.skills import get_related_skills
from app.processing.normalizer import normalize_skill


def calculate_skill_gap(
    db: Session, target_role: str, user_skills: List[str]
) -> Dict[str, Any]:
    """
    Compute skill gap comparison between user's current skills and target role requirements.

    Args:
        db: SQLAlchemy database session
        target_role: Target job title/role (e.g., 'Python Developer')
        user_skills: List of raw or canonical skill strings provided by user

    Returns:
        dict: Skill gap comparison report containing matching_skills, missing_skills, related_skills
    """
    # 1. Normalize user skills
    user_skills_normalized = set(
        normalize_skill(s) for s in user_skills if s and isinstance(s, str) and s.strip()
    )

    # 2. Get top required skills for target_role from database
    role_skills_data = get_skills_per_role(db, role_name=target_role, top_n=15)
    role_skill_names = [s["skill_name"] for s in role_skills_data]

    # 3. Compute Matching and Missing Skills
    matching = [s for s in role_skill_names if s in user_skills_normalized]
    missing = [s for s in role_skill_names if s not in user_skills_normalized]

    # 4. Compute Related Skills (co-occurring with user's top matching skills)
    related_set = set()
    for skill_name in matching[:3]:
        rel = get_related_skills(db, target_skill=skill_name, top_n=3)
        for item in rel:
            r_name = item["related_skill"]
            if r_name not in user_skills_normalized and r_name not in missing:
                related_set.add(r_name)

    return {
        "target_role": target_role,
        "user_skills": sorted(list(user_skills_normalized)),
        "role_skills_evaluated": role_skill_names,
        "matching_skills": matching,
        "missing_skills": missing,
        "related_skills": sorted(list(related_set)),
        "disclaimer": (
            "This skill gap analysis is a descriptive educational tool intended for self-assessment. "
            "It does not predict hiring probability, interview performance, or guarantee job placement."
        ),
    }
