"""Compliance checker that validates policy text against required clauses."""

import json
from pathlib import Path


def _load_clauses() -> list[dict]:
    """Load clause definitions from clauses.json."""
    clauses_path = Path(__file__).resolve().parent.parent / "data" / "clauses.json"
    with open(clauses_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
        present = any(kw.lower() in text_lower for kw in clause["keywords"])
        results.append({
            "clause": clause["name"],
            "present": present,
            "required": clause["required"],
        })

    return results
