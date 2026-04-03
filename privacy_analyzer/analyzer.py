"""Main entry point for privacy policy compliance analysis."""

from .config import MIN_POLICY_LENGTH
from .services.compliance import check_compliance
from .services.llm import analyze_with_llm


def analyze_privacy_policy(policy_text: str) -> dict:
    """Analyze a privacy policy for compliance and risk.

    Args:
        policy_text: The full text of a website's privacy policy.

    Returns:
        Dict with clauses, risk_score, issues, and summary.

    Raises:
        ValueError: If policy_text is empty or too short.
    """
    if not policy_text or not isinstance(policy_text, str):
        raise ValueError("policy_text must be a non-empty string")

    text = policy_text.strip()
    if len(text) < MIN_POLICY_LENGTH:
        raise ValueError(
            f"Policy text too short ({len(text)} chars). "
            f"Minimum {MIN_POLICY_LENGTH} characters required."
        )

    clause_results = check_compliance(text)
    llm_analysis = analyze_with_llm(text, clause_results)

    return {
        "clauses": clause_results,
        "risk_score": llm_analysis["risk_score"],
        "issues": llm_analysis["issues"],
        "summary": llm_analysis["summary"],
    }
