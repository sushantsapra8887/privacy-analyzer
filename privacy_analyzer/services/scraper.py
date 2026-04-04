"""Web scraper for extracting privacy policy text from URLs."""

import html
import re
from urllib.request import Request, urlopen


_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_TIMEOUT = 15


def scrape_policy_text(url: str) -> str:
    """Fetch a URL and extract the visible text content.

    Args:
        url: The full URL of the privacy policy page.

    Returns:
        Extracted plain text from the page.

    Raises:
        RuntimeError: If the page cannot be fetched or has no content.
    """
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    with urlopen(req, timeout=_TIMEOUT) as resp:
        raw = resp.read()

    # Try to decode with charset from headers, fall back to utf-8
    charset = "utf-8"
    content_type = resp.headers.get("Content-Type", "")
    if "charset=" in content_type:
        charset = content_type.split("charset=")[-1].strip()

    page_html = raw.decode(charset, errors="replace")

    text = _html_to_text(page_html)

    if len(text.strip()) < 50:
        raise RuntimeError(f"Extracted text too short ({len(text.strip())} chars)")

    return text


def _html_to_text(page_html: str) -> str:
    """Convert HTML to clean plain text."""
    content = page_html

    # Remove non-visible elements
    for tag in ("script", "style", "nav", "header", "footer", "noscript", "svg"):
        content = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}>", " ", content,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # Replace block-level tags with newlines for readability
    content = re.sub(r"<(?:br|p|div|h[1-6]|li|tr)[^>]*>", "\n", content, flags=re.IGNORECASE)

    # Strip all remaining HTML tags
    content = re.sub(r"<[^>]+>", " ", content)

    # Decode HTML entities
    content = html.unescape(content)

    # Normalize whitespace
    content = re.sub(r"[ \t]+", " ", content)
    content = re.sub(r"\n[ \t]+", "\n", content)
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip()
