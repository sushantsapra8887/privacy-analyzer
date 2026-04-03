"""Compliance checker that validates policy text against required clauses."""

import json
import re
from pathlib import Path


_REQUIREMENT_REQUIRED = {"MANDATORY", "REQUIRED"}

# Explicit keyword overrides for clauses whose scanner_check lacks quoted terms.
# Keyed by s_no from clauses.json.
_KEYWORD_OVERRIDES = {
    1: ["company name", "organization name", "data fiduciary", "registration",
        "registered in"],
    2: ["email address", "phone number", "physical address", "contact us",
        "contact details", "contact information"],
    10: ["we use your", "use your data for", "process your personal data for",
         "data is processed", "purpose"],
    11: ["services we provide", "linked to", "goods and services",
         "enable", "service delivery"],
    16: ["click here", "settings", "email us", "withdraw", "consent withdrawal",
         "opt out", "unsubscribe"],
    12: ["will not use", "not be used for", "limited to", "only for the stated purpose",
         "not use for other purposes", "beyond what was consented"],
    18: ["consent separately", "separate consent", "purpose-specific",
         "individual consent", "consent for each"],
    24: ["submit a request", "exercise your rights", "email", "form",
         "verification", "data request"],
    25: ["third parties", "third party", "processors", "vendors", "partners",
         "service providers", "data processors"],
    26: ["reason for sharing", "purpose of sharing", "shared for", "shared with",
         "share your data", "why we share", "specific function",
         "receives data"],
    28: ["transfer outside india", "cross-border", "international transfer",
         "stored outside", "transferred outside", "outside india"],
    31: ["nature", "consequences", "mitigation", "breach notification",
         "steps we have taken"],
    32: ["transparency", "committed to", "will not suppress", "breach reporting"],
    33: ["retention", "how long", "keep your data", "storage period",
         "delete after", "retain your data", "account plus", "kept for"],
    36: ["processors to delete", "instruct", "processors to erase",
         "instruct all", "delete your data from their"],
    38: ["google analytics", "facebook pixel", "hotjar", "third-party tracker",
         "third party track", "analytics", "pixel"],
    39: ["cookie consent", "cookie settings", "accept or reject", "cookie banner",
         "manage cookies", "non-essential cookies"],
    40: ["plain language", "clear language", "easy to understand", "readability",
         "simple language"],
    41: ["language toggle", "hindi", "regional language", "available in english",
         "multiple languages", "scheduled languages"],
    42: ["standalone", "separate page", "separate from", "independent",
         "not embedded", "not buried", "terms of service", "terms & conditions",
         "terms and conditions"],
}


def _load_clauses() -> list[dict]:
    """Load clause definitions from clauses.json."""
    clauses_path = Path(__file__).resolve().parent.parent / "data" / "clauses.json"
    with open(clauses_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["clauses"]


def _get_keywords(clause: dict) -> list[str]:
    """Get search keywords for a clause.

    Uses quoted terms from scanner_check first, then falls back
    to explicit overrides, then to terms from sample_language.
    """
    s_no = clause.get("s_no")

    # Check explicit overrides first — most reliable
    if s_no in _KEYWORD_OVERRIDES:
        return _KEYWORD_OVERRIDES[s_no]

    scanner_check = clause.get("scanner_check", "")
    quoted = re.findall(r"'([^']+)'", scanner_check)
    if quoted:
        # Strip [placeholder] brackets from keywords like 'we use your [data]'
        cleaned = [re.sub(r"\[.*?\]", "", kw).strip() for kw in quoted]
        return [kw for kw in cleaned if len(kw) >= 3]

    # No s_no override, no quoted keywords — fall back to sample_language
    if s_no in _KEYWORD_OVERRIDES:
        return _KEYWORD_OVERRIDES[s_no]

    # Last resort: extract key phrases from sample_language
    sample = clause.get("sample_language", "")
    if sample:
        # Pull bracketed placeholders and significant phrases
        words = re.findall(r"\b[a-z][a-z ]{2,}\b", sample.lower())
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "shall", "should", "may", "might", "can", "could", "of", "in",
            "to", "for", "with", "on", "at", "from", "by", "about", "as",
            "and", "but", "or", "not", "so", "yet", "if", "that", "this",
            "these", "those", "it", "its", "your", "you", "we", "our", "us",
        }
        return [w.strip() for w in words if w.strip() not in stopwords][:10]

    return []


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
        keywords = _get_keywords(clause)
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
