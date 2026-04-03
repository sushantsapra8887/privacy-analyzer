"""Mock LLM service for privacy policy risk analysis."""

from pathlib import Path

from ..config import (
    BASE_RISK_SCORE,
    MAX_RISK_SCORE,
    MIN_RISK_SCORE,
    MISSING_OPTIONAL_CLAUSE_PENALTY,
    MISSING_REQUIRED_CLAUSE_PENALTY,
)


def _load_prompt_template() -> str:
    """Load the prompt template from disk."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "privacy_prompt.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _compute_risk_score(clause_results: list[dict]) -> int:
    """Compute a numeric risk score based on missing clauses."""
    score = BASE_RISK_SCORE

    for clause in clause_results:
        if not clause["present"]:
            if clause["required"]:
                score += MISSING_REQUIRED_CLAUSE_PENALTY
            else:
                score += MISSING_OPTIONAL_CLAUSE_PENALTY

    return max(MIN_RISK_SCORE, min(MAX_RISK_SCORE, round(score)))


def _identify_issues(clause_results: list[dict]) -> list[str]:
    """Build a list of compliance issues from clause results."""
    issues = []

    for clause in clause_results:
        if not clause["present"] and clause["required"]:
            issues.append(f"Missing required clause: {clause['clause']}")

    for clause in clause_results:
        if not clause["present"] and not clause["required"]:
            issues.append(f"Missing optional clause: {clause['clause']}")

    return issues


def _generate_summary(clause_results: list[dict], risk_score: int) -> str:
    """Generate a human-readable summary."""
    total = len(clause_results)
    present = sum(1 for c in clause_results if c["present"])
    missing_required = sum(
        1 for c in clause_results if not c["present"] and c["required"]
    )

    if risk_score <= 3:
        level = "good"
    elif risk_score <= 6:
        level = "moderate"
    else:
        level = "poor"

    return (
        f"Privacy policy covers {present}/{total} analyzed clauses. "
        f"{missing_required} required clause(s) missing. "
        f"Overall compliance posture: {level} (risk score: {risk_score}/10)."
    )


def analyze_with_llm(policy_text: str, clause_results: list[dict]) -> dict:
    """Mock LLM analysis of privacy policy compliance.

    In production, this would format the prompt template with the inputs
    and call an actual LLM API. For now it uses rule-based logic.

    Args:
        policy_text: The full privacy policy text.
        clause_results: Output from compliance.check_compliance().

    Returns:
        Dict with risk_score, issues list, and summary string.
    """
    # Load template to validate it exists (used in production path)
    _load_prompt_template()

    risk_score = _compute_risk_score(clause_results)
    issues = _identify_issues(clause_results)
    summary = _generate_summary(clause_results, risk_score)

    return {
        "risk_score": risk_score,
        "issues": issues,
        "summary": summary,
    }
