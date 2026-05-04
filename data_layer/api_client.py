import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

_config_path = Path(__file__).parent.parent / "config" / "api_config.json"


def _load_config():
    with open(_config_path) as f:
        return json.load(f)

def fetch_domain_metrics(domain: str, start_date: str, end_date: str) -> dict:
    """
    Calls POST /getAdvancedReport and returns parsed TotalCounts metrics.
    Falls back to mock data for known demo domains.
    Returns 'unknown' source if domain is not found in API or demo list.
    """
    config = _load_config()

    payload = {
        "domain": domain,
        "startDate": start_date,
        "endDate": end_date,
        "selectedDateType": "custom",
        "withoutPagination": True,
        "reportType": "domain"
    }

    try:
        url = config["base_url"] + config["endpoint"]
        resp = requests.post(
            url,
            json=payload,
            headers=config["headers"],
            timeout=config["timeout_seconds"]
        )
        resp.raise_for_status()

        outer = resp.json()
        inner = json.loads(outer.get("response", "{}"))
        total = inner.get("TotalCounts", {})
        return _parse_metrics(total, domain, start_date, end_date, source="api")

    except Exception:
        return _mock_metrics(domain, start_date, end_date)


def _parse_metrics(total: dict, domain: str, start_date: str, end_date: str, source: str) -> dict:
    def pct(val):
        try:
            return round(float(str(val).replace("%", "").strip()), 2)
        except (TypeError, ValueError):
            return 0.0

    def num(val):
        try:
            return int(str(val).replace(",", "").strip())
        except (TypeError, ValueError):
            return 0

    sent = num(total.get("totalSent", 0))
    hard_errors = num(total.get("totalHarderror", 0))
    hard_error_rate = round((hard_errors / sent * 100), 2) if sent > 0 else 0.0

    return {
        "domain":            domain,
        "start_date":        start_date,
        "end_date":          end_date,
        "source":            source,
        "total_sent":        sent,
        "total_delivered":   num(total.get("totalDelivered", 0)),
        "delivery_rate":     pct(total.get("totalDeliveredRate", 0)),
        "open_rate":         pct(total.get("totalOpenRate", 0)),
        "genuine_open_rate": pct(total.get("totalgenuineOpenRate", 0)),
        "click_rate":        pct(total.get("totalClickRate", 0)),
        "abuse_rate":        pct(total.get("totalAbuseRate", 0)),
        "unsub_rate":        pct(total.get("totalUnsubRate", 0)),
        "hard_error_rate":   hard_error_rate,
        "soft_error_rate":   pct(total.get("totalSofterror", 0)),
        "block_error":       num(total.get("totalBlockError", 0)),
        "total_abuses":      num(total.get("totalAbuses", 0)),
        "total_unsubs":      num(total.get("totalUnsubs", 0)),
        "total_revenue":     total.get("totalRevenue", "0"),
        "total_ecpm":        total.get("totaleCPM", "0"),
    }


def _mock_metrics(domain: str, start_date: str, end_date: str) -> dict:
    """
    Demo data for judges when API is not accessible.
    Each domain has its own distinct profile within its reputation band.

    Demo domains to use:
      BAD     → bad-reputation.com   |  bounce-heavy.net  |  spammy-sender.org
      AVERAGE → mid-tier-mail.com    |  average-domain.net
      GOOD    → great-sender.com     |  healthy-domain.net |  top-performer.org
    """
    PROFILES = {
        # ── BAD ──────────────────────────────────────────────────────────────
        # High abuse rate + low delivery — classic reputation problem
        "bad-reputation.com": {
            "delivery_rate": 78.5, "open_rate": 6.2,  "genuine_open_rate": 4.1,
            "click_rate": 0.4,     "abuse_rate": 0.45, "unsub_rate": 1.8,
            "hard_error_rate": 8.2,"soft_error_rate": 5.1,
            "total_sent": 120000,  "total_delivered": 94200,
            "total_abuses": 540,   "total_unsubs": 2160,
            "total_revenue": "1250.00", "total_ecpm": "10.42",
        },
        # Very high hard bounce rate — list quality issue
        "bounce-heavy.net": {
            "delivery_rate": 74.0, "open_rate": 8.5,  "genuine_open_rate": 5.8,
            "click_rate": 0.6,     "abuse_rate": 0.28, "unsub_rate": 2.1,
            "hard_error_rate": 12.5,"soft_error_rate": 7.3,
            "total_sent": 95000,   "total_delivered": 70300,
            "total_abuses": 266,   "total_unsubs": 1995,
            "total_revenue": "980.00", "total_ecpm": "10.32",
        },
        # Extremely high abuse/spam complaints — content or consent issue
        "spammy-sender.org": {
            "delivery_rate": 82.0, "open_rate": 4.8,  "genuine_open_rate": 2.9,
            "click_rate": 0.3,     "abuse_rate": 0.52, "unsub_rate": 2.4,
            "hard_error_rate": 6.8,"soft_error_rate": 4.2,
            "total_sent": 140000,  "total_delivered": 114800,
            "total_abuses": 728,   "total_unsubs": 3360,
            "total_revenue": "1100.00", "total_ecpm": "7.86",
        },

        # ── AVERAGE ──────────────────────────────────────────────────────────
        # Moderate issues — delivery ok but engagement low
        "mid-tier-mail.com": {
            "delivery_rate": 91.0, "open_rate": 11.0, "genuine_open_rate": 8.5,
            "click_rate": 1.1,     "abuse_rate": 0.22, "unsub_rate": 0.85,
            "hard_error_rate": 4.2,"soft_error_rate": 2.8,
            "total_sent": 85000,   "total_delivered": 77350,
            "total_abuses": 187,   "total_unsubs": 723,
            "total_revenue": "2800.00", "total_ecpm": "32.94",
        },
        # Slightly better average — delivery good but open rate still weak
        "average-domain.net": {
            "delivery_rate": 93.5, "open_rate": 14.5, "genuine_open_rate": 11.2,
            "click_rate": 1.4,     "abuse_rate": 0.18, "unsub_rate": 0.72,
            "hard_error_rate": 3.1,"soft_error_rate": 2.1,
            "total_sent": 72000,   "total_delivered": 67320,
            "total_abuses": 130,   "total_unsubs": 518,
            "total_revenue": "3400.00", "total_ecpm": "47.22",
        },

        # ── GOOD ─────────────────────────────────────────────────────────────
        # Excellent across all metrics — benchmark domain
        "great-sender.com": {
            "delivery_rate": 97.8, "open_rate": 26.5, "genuine_open_rate": 22.3,
            "click_rate": 3.1,     "abuse_rate": 0.05, "unsub_rate": 0.3,
            "hard_error_rate": 0.9,"soft_error_rate": 0.8,
            "total_sent": 200000,  "total_delivered": 195600,
            "total_abuses": 100,   "total_unsubs": 600,
            "total_revenue": "18500.00", "total_ecpm": "92.50",
        },
        # Good but slightly lower open rate than top performer
        "healthy-domain.net": {
            "delivery_rate": 96.2, "open_rate": 21.3, "genuine_open_rate": 18.1,
            "click_rate": 2.6,     "abuse_rate": 0.08, "unsub_rate": 0.4,
            "hard_error_rate": 1.4,"soft_error_rate": 1.1,
            "total_sent": 155000,  "total_delivered": 149110,
            "total_abuses": 124,   "total_unsubs": 620,
            "total_revenue": "13200.00", "total_ecpm": "85.16",
        },
        # Top of the range — near-perfect metrics
        "top-performer.org": {
            "delivery_rate": 98.5, "open_rate": 31.2, "genuine_open_rate": 27.4,
            "click_rate": 4.2,     "abuse_rate": 0.03, "unsub_rate": 0.22,
            "hard_error_rate": 0.6,"soft_error_rate": 0.5,
            "total_sent": 250000,  "total_delivered": 246250,
            "total_abuses": 75,    "total_unsubs": 550,
            "total_revenue": "26000.00", "total_ecpm": "104.00",
        },
    }

    if domain.lower() not in PROFILES:
        return {
            "domain":     domain,
            "start_date": start_date,
            "end_date":   end_date,
            "source":     "unknown",
        }

    profile = PROFILES[domain.lower()]
    return {
        "domain":      domain,
        "start_date":  start_date,
        "end_date":    end_date,
        "source":      "mock",
        "block_error": 0,
        **profile,
    }
