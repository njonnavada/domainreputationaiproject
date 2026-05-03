import sys
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.orchestrator import DomainReputationOrchestrator

app = FastAPI(
    title="Domain Reputation AI API",
    description="Multi-agent domain reputation analysis — Zeta Global Buildathon 2026",
    version="1.0.0",
    servers=[
        {
            "url": "https://domainreputationaiproject.onrender.com",
            "description": "Production server"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = DomainReputationOrchestrator()


class AnalyzeRequest(BaseModel):
    domain:     str
    start_date: str | None = None
    end_date:   str | None = None


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    end   = req.end_date   or datetime.today().strftime("%Y-%m-%d")
    start = req.start_date or (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    return orchestrator.analyze(req.domain, start, end)


@app.post("/analyze-copilot")
def analyze_copilot(req: AnalyzeRequest):
    """
    Flat, Copilot Studio-friendly response.
    All values are strings — no nested objects.
    """
    end   = req.end_date   or datetime.today().strftime("%Y-%m-%d")
    start = req.start_date or (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    r = orchestrator.analyze(req.domain, start, end)

    if r["metrics"].get("source") == "unknown":
        return {
            "domain":          req.domain,
            "status":          "UNKNOWN",
            "emoji":           "❓",
            "score":           "N/A",
            "summary":         (
                f"I'm sorry, I don't have reputation data for '{req.domain}' at this time. "
                f"Please enter a valid Zeta sending domain. "
                f"For demo purposes, try: great-sender.com, mid-tier-mail.com, or bad-reputation.com."
            ),
            "issues":          "",
            "recommendations": "",
        }

    cls  = r["classification"]
    m    = r["metrics"]
    diag = r["diagnosis"]
    recs = r["recommendations"]["recommendations"]

    # Top 5 issues as plain text
    issues_text = "\n".join(
        f"{'🔴' if i['severity']=='critical' else '🟠'} {i['reason']}"
        for i in diag["issues"][:5]
    ) or "✅ No significant issues found."

    # Top 5 recommendations as plain text
    recs_text = "\n".join(
        f"{rec['rank']}. {rec['action']} (Impact: {rec['impact']}, Effort: {rec['effort']})"
        for rec in recs[:5]
    ) or "No specific actions needed."

    return {
        "domain":           req.domain,
        "status":           cls["label"],
        "emoji":            cls["emoji"],
        "score":            str(cls["overall_score"]),
        "period":           f"{start} to {end}",
        "open_rate":        f"{m['open_rate']}%",
        "delivery_rate":    f"{m['delivery_rate']}%",
        "abuse_rate":       f"{m['abuse_rate']}%",
        "click_rate":       f"{m['click_rate']}%",
        "hard_bounce_rate": f"{m['hard_error_rate']}%",
        "unsub_rate":       f"{m['unsub_rate']}%",
        "total_sent":       f"{m['total_sent']:,}",
        "issue_count":      str(diag["issue_count"]),
        "critical_count":   str(diag["critical_count"]),
        "issues":           issues_text,
        "recommendations":  recs_text,
        "summary":          (
            f"Domain '{req.domain}' has a reputation score of {cls['overall_score']}/100 "
            f"and is classified as {cls['label']}. "
            f"Found {diag['issue_count']} issues ({diag['critical_count']} critical). "
            f"Top action: {recs[0]['action'] if recs else 'None required'}."
        ),
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "Domain Reputation AI"}


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
def ai_plugin():
    return JSONResponse(content={
        "schema_version": "v1",
        "name_for_model": "domain_reputation_ai",
        "name_for_human": "Domain Reputation AI",
        "description_for_model": (
            "Analyzes email domain reputation using a multi-agent AI system. "
            "Given a domain name, it fetches email metrics and runs three agents: "
            "Classifier (scores 0-100), Diagnosis (root causes), and Recommendation (action plan). "
            "Use analyze-copilot endpoint for flat, readable responses."
        ),
        "description_for_human": (
            "Multi-agent AI that classifies, diagnoses, and recommends fixes "
            "for email domain reputation — Zeta Global Buildathon 2026."
        ),
        "auth": {
            "type": "none",
            "is_user_authenticated": False
        },
        "api": {
            "type": "openapi",
            "url": "https://domainreputationaiproject.onrender.com/openapi.json"
        },
        "logo_url": "https://domainreputationaiproject.onrender.com/health",
        "contact_email": "njonnavada@zetaglobal.com",
        "legal_info_url": "https://domainreputationaiproject.onrender.com/health"
    })
