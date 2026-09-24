"""
Unit tests for skill extractor module (backend/app/processing/skill_extractor.py).
Focuses on verifying accuracy and zero false-positive substring matches.
"""

import pytest
from app.processing.skill_extractor import SkillExtractor


@pytest.fixture
def extractor():
    return SkillExtractor()


def test_extract_from_list_string(extractor):
    raw_skills = "python, ReactJS, postgres, My SQL, docker, TS"
    extracted = extractor.extract_from_list_string(raw_skills)
    assert "Python" in extracted
    assert "React" in extracted
    assert "PostgreSQL" in extracted
    assert "MySQL" in extracted
    assert "Docker" in extracted
    assert "TypeScript" in extracted


def test_extract_from_text_valid_skills(extractor):
    text = "Looking for a Software Engineer experienced in Python, React, PostgreSQL, and AWS."
    extracted = extractor.extract_from_text(text)
    assert "Python" in extracted
    assert "React" in extracted
    assert "PostgreSQL" in extracted
    assert "AWS" in extracted


def test_no_false_positives_substring_matching(extractor):
    """
    CRITICAL TEST: Verify substring matching does NOT produce false positives.
    - 'JavaScript' must NOT match 'Java'
    - 'CSS' must NOT match 'C'
    - 'Docker' must NOT match 'R'
    - 'Django' must NOT match 'Go'
    - 'React' must NOT match 'R'
    """
    # Test 1: JavaScript should NOT trigger Java
    text_js = "Must have strong skills in JavaScript and HTML."
    skills_js = extractor.extract_from_text(text_js)
    assert "JavaScript" in skills_js
    assert "Java" not in skills_js, "False positive: 'Java' matched inside 'JavaScript'"

    # Test 2: CSS should NOT trigger C
    text_css = "Proficient in CSS, HTML5, and Tailwind."
    skills_css = extractor.extract_from_text(text_css)
    assert "CSS" in skills_css
    assert "C" not in skills_css, "False positive: 'C' matched inside 'CSS'"

    # Test 3: Django should NOT trigger Go
    text_django = "Building backend REST services using Django and Python."
    skills_django = extractor.extract_from_text(text_django)
    assert "Django" in skills_django
    assert "Go" not in skills_django, "False positive: 'Go' matched inside 'Django'"

    # Test 4: React should NOT trigger R
    text_react = "Building UI components with React."
    skills_react = extractor.extract_from_text(text_react)
    assert "React" in skills_react
    assert "R" not in skills_react, "False positive: 'R' matched inside 'React'"


def test_extract_all_skills_combined(extractor):
    req_skills = "Python, Docker"
    desc_text = "We are seeking a developer with Python, AWS, and PostgreSQL experience."
    
    all_skills = extractor.extract_all_skills(req_skills, desc_text)
    skill_names = [s["skill_name"] for s in all_skills]
    
    assert "Python" in skill_names
    assert "Docker" in skill_names
    assert "AWS" in skill_names
    assert "PostgreSQL" in skill_names
    
    # Check source tagging for Python (present in both)
    py_skill = next(s for s in all_skills if s["skill_name"] == "Python")
    assert py_skill["source"] == "both"
