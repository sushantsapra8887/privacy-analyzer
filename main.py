"""API entry point for the Privacy Policy Compliance Analyzer."""

import traceback

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from privacy_analyzer.analyzer import analyze_privacy_policy
from privacy_analyzer.services.scraper import scrape_policy_text

app = FastAPI(
    title="Privacy Policy Compliance Analyzer",
    version="1.0.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "trace": traceback.format_exc()},
    )


class PolicyRequest(BaseModel):
    policy_text: str

    @field_validator("policy_text")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("policy_text must not be empty")
        return v


class ScrapeRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def must_be_valid_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        return v


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(req: PolicyRequest):
    try:
        result = analyze_privacy_policy(req.policy_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return result


@app.post("/scrape")
def scrape_and_analyze(req: ScrapeRequest):
    """Fetch a privacy policy page by URL, extract text, and analyze it."""
    try:
        policy_text = scrape_policy_text(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    try:
        result = analyze_privacy_policy(policy_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result["source_url"] = req.url
    result["extracted_text_length"] = len(policy_text)
    return result
