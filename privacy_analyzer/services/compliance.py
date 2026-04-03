"""Compliance checker that validates policy text against required clauses."""

import json
import re
from pathlib import Path


_REQUIREMENT_REQUIRED = {"MANDATORY", "REQUIRED"}


def _load_clauses() -> list[dict]:
    """Load clause definitions from clauses.json."""
    clauses_path = Path(__file__).resolve().parent.parent / "data" / "clauses.json"
    with open(clauses_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["clauses"]


def _extract_keywords(scanner_check: str, clause_text: str) -> list[str]:
    """Extract search keywords from scanner_check and clause text.

    First tries quoted keywords from scanner_check (e.g. 'keyword1').
    Falls back to meaningful noun phrases from both fields.
    """
    quoted = re.findall(r"'([^']+)'", scanner_check)
    if quoted:
        return quoted

    # Fallback: extract key noun phrases from scanner_check and clause text
    combined = f"{scanner_check} {clause_text}"
    # Remove common filler words and extract meaningful multi-word phrases
    phrases = re.findall(
        r"\b(?:email address|phone number|physical address|company name|"
        r"organization name|privacy policy|contact (?:details|section)|"
        r"readability|sentence length|language toggle|separate page|"
        r"standalone|terms (?:of service|& conditions)|date|"
        r"clickable link|cookie consent|cookie settings)\b",
        combined.lower(),
    )
    if phrases:
        return phrases

    # Last resort: extract significant words from clause_text
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "can", "could", "of", "in", "to", "for",
        "with", "on", "at", "from", "by", "about", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "under",
        "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
        "neither", "each", "every", "all", "any", "few", "more", "most",
        "other", "some", "such", "no", "only", "own", "same", "than", "too",
        "very", "just", "if", "that", "this", "these", "those", "it", "its",
        "check", "whether", "how", "what", "which", "who", "whom", "whose",
        "when", "where", "why",
    }
    words = re.findall(r"\b[a-z]{3,}\b", clause_text.lower())
    return [w for w in words if w not in stopwords]


def check_compliance(policy_text: str) -> list[dict]:
    """Check which clauses are present in the policy text.

    Args:
        policy_text: The full text of the privacy policy.

    Returns:
        List of dicts with clause name, presence status, and required flag.
    """
    clauses = _load_clauses()
    text_lower = policy_text.lower()
    results = []

    for clause in clauses:
        keywords = _extract_keywords(
            clause.get("scanner_check", ""),
            clause.get("mandatory_clause", ""),
        )
        present = any(kw.lower() in text_lower for kw in keywords) if keywords else False
        required = clause.get("requirement_level", "") in _REQUIREMENT_REQUIRED

        results.append({
            "clause": clause["mandatory_clause"],
            "section": clause.get("section_title", ""),
            "category": clause.get("clause_category", ""),
            "present": present,
            "required": required,
            "requirement_level": clause.get("requirement_level", ""),
        })

    return results
