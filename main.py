"""API entry point for the Privacy Policy Compliance Analyzer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from privacy_analyzer.analyzer import analyze_privacy_policy

app = FastAPI(
    title="Privacy Policy Compliance Analyzer",
    version="1.0.0",
)


class PolicyRequest(BaseModel):
    policy_text: str

    @field_validator("policy_text")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("policy_text must not be empty")
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
