"""
Skill Extraction Module for Job Market Analytics.

Extracts and normalizes tech skills from:
1. Structured required_skills field (comma-separated lists)
2. Unstructured job description text

Uses lookaround-based regex term matching to eliminate false-positive substring matches
(e.g., preventing 'Java' from matching inside 'JavaScript', or 'C' inside 'CSS').
"""

import re
from typing import List, Set, Dict, Tuple
from app.processing.normalizer import CANONICAL_SKILL_MAP, normalize_skill


class SkillExtractor:
    """Extracts and normalizes skills from text and skill lists."""

    def __init__(self, skill_map: Dict[str, str] = CANONICAL_SKILL_MAP):
        self.skill_map = skill_map
        # Precompile compiled regex patterns for each canonical skill/alias
        self.compiled_patterns = self._build_compiled_patterns()

    def _build_compiled_patterns(self) -> Dict[str, Tuple[re.Pattern, str]]:
        """
        Build compiled regex patterns using negative lookarounds to prevent false positives.
        
        Example:
            'Java' pattern: (?<![a-zA-Z0-9_])Java(?![a-zA-Z0-9_])
            This matches 'Java' but NOT 'JavaScript'.
        """
        patterns = {}
        for alias, canonical in self.skill_map.items():
            escaped_alias = re.escape(alias)
            # Use negative lookaround boundary pattern
            pattern_str = rf"(?<![a-zA-Z0-9_]){escaped_alias}(?![a-zA-Z0-9_])"
            patterns[alias] = (re.compile(pattern_str, re.IGNORECASE), canonical)
        return patterns

    def extract_from_list_string(self, skills_str: str) -> List[str]:
        """
        Parse and normalize skills from a comma/semicolon-separated string.

        Args:
            skills_str: Raw skills string (e.g., "python, react.js, Postgres, Docker")

        Returns:
            List[str]: Deduplicated list of canonical skill names
        """
        if not skills_str or not isinstance(skills_str, str):
            return []

        # Split by comma or semicolon
        raw_items = [item.strip() for item in re.split(r"[,;]\s*", skills_str) if item.strip()]
        
        extracted: Set[str] = set()
        for item in raw_items:
            norm = normalize_skill(item)
            if norm:
                extracted.add(norm)

        return sorted(list(extracted))

    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract canonical skills from unstructured job description text.
        Guarantees NO false-positive substring matches.

        Args:
            text: Job description text snippet or full text

        Returns:
            List[str]: Deduplicated list of canonical skill names found in text
        """
        if not text or not isinstance(text, str):
            return []

        extracted: Set[str] = set()
        for alias, (pattern, canonical) in self.compiled_patterns.items():
            if pattern.search(text):
                extracted.add(canonical)

        return sorted(list(extracted))

    def extract_all_skills(self, required_skills_str: str, description_text: str) -> List[dict]:
        """
        Combine skills from required_skills field and description text.

        Returns:
            List[dict]: List of skill dicts containing {'skill_name': str, 'source': str, 'is_normalized': bool}
        """
        skills_from_req = self.extract_from_list_string(required_skills_str)
        skills_from_desc = self.extract_from_text(description_text)

        result_map: Dict[str, dict] = {}

        # Add skills from structured field
        for skill in skills_from_req:
            result_map[skill] = {
                "skill_name": skill,
                "source": "required_skills",
                "is_normalized": True,
            }

        # Add skills from description text
        for skill in skills_from_desc:
            if skill not in result_map:
                result_map[skill] = {
                    "skill_name": skill,
                    "source": "description",
                    "is_normalized": True,
                }
            elif result_map[skill]["source"] == "required_skills":
                # If present in both, mark source as both
                result_map[skill]["source"] = "both"

        return list(result_map.values())
