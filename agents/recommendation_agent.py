_RECOMMENDATIONS = {
    "delivery_rate": {
        "critical": [
            {"priority": 1, "action": "Check domain and IP blacklist status immediately (MXToolbox, Talos)",   "impact": "High",   "effort": "Low"},
            {"priority": 2, "action": "Review ISP feedback loops and bounce logs for block patterns",          "impact": "High",   "effort": "Medium"},
            {"priority": 3, "action": "Audit authentication records — SPF, DKIM, DMARC alignment",            "impact": "High",   "effort": "Medium"},
            {"priority": 4, "action": "Consider IP warm-up on a dedicated sending IP",                        "impact": "High",   "effort": "High"},
        ],
        "warning": [
            {"priority": 1, "action": "Verify SPF and DKIM records are correctly published",                  "impact": "Medium", "effort": "Low"},
            {"priority": 2, "action": "Reduce sending volume temporarily to recover sender reputation",       "impact": "Medium", "effort": "Low"},
            {"priority": 3, "action": "Review PMTA bounce handling and retry policies",                       "impact": "Medium", "effort": "Medium"},
        ],
    },
    "open_rate": {
        "critical": [
            {"priority": 1, "action": "Run A/B tests on subject lines — personalize with recipient's name",   "impact": "High",   "effort": "Low"},
            {"priority": 2, "action": "Segment list and send only to most engaged users first",               "impact": "High",   "effort": "Medium"},
            {"priority": 3, "action": "Optimize send time — test morning vs evening delivery windows",        "impact": "Medium", "effort": "Low"},
            {"priority": 4, "action": "Remove cold subscribers (no opens in last 90 days)",                   "impact": "High",   "effort": "Medium"},
        ],
        "warning": [
            {"priority": 1, "action": "Test emoji or question-based subject lines to boost open rates",       "impact": "Medium", "effort": "Low"},
            {"priority": 2, "action": "Review preheader text — it displays next to subject in inbox",         "impact": "Medium", "effort": "Low"},
        ],
    },
    "genuine_open_rate": {
        "critical": [
            {"priority": 1, "action": "Suppress bot-detected opens from engagement metrics",                  "impact": "High",   "effort": "Medium"},
            {"priority": 2, "action": "Launch re-engagement campaign targeting inactive subscribers",          "impact": "High",   "effort": "Medium"},
            {"priority": 3, "action": "Audit list sources — low genuine opens often trace to poor opt-ins",   "impact": "High",   "effort": "High"},
        ],
        "warning": [
            {"priority": 1, "action": "Tighten list acquisition — require double opt-in",                     "impact": "Medium", "effort": "Medium"},
        ],
    },
    "abuse_rate": {
        "critical": [
            {"priority": 1, "action": "Immediately suppress all complainers and honor feedback loop data",    "impact": "High",   "effort": "Low"},
            {"priority": 2, "action": "Audit consent — ensure all recipients explicitly opted in",            "impact": "High",   "effort": "Medium"},
            {"priority": 3, "action": "Review sending frequency — reduce to 1–2 times per week max",         "impact": "High",   "effort": "Low"},
            {"priority": 4, "action": "Make unsubscribe link prominent — reduce friction to opt out",         "impact": "High",   "effort": "Low"},
        ],
        "warning": [
            {"priority": 1, "action": "Monitor FBL (Feedback Loop) reports daily and auto-suppress",         "impact": "Medium", "effort": "Medium"},
            {"priority": 2, "action": "Add clear sender identification to reduce 'this is spam' clicks",      "impact": "Medium", "effort": "Low"},
        ],
    },
    "hard_error_rate": {
        "critical": [
            {"priority": 1, "action": "Run full list validation — remove all invalid and non-existent emails","impact": "High",   "effort": "Medium"},
            {"priority": 2, "action": "Enforce real-time email verification at point of data capture",        "impact": "High",   "effort": "High"},
            {"priority": 3, "action": "Suppress all hard bounces immediately — stop retrying invalid emails", "impact": "High",   "effort": "Low"},
        ],
        "warning": [
            {"priority": 1, "action": "Schedule monthly list hygiene — use email validation tools",           "impact": "Medium", "effort": "Low"},
            {"priority": 2, "action": "Audit list age — addresses older than 12 months have higher bounce",   "impact": "Medium", "effort": "Low"},
        ],
    },
    "click_rate": {
        "warning": [
            {"priority": 1, "action": "Redesign CTA buttons — use action-oriented text and prominent placement", "impact": "Medium", "effort": "Low"},
            {"priority": 2, "action": "Improve email content relevance through audience segmentation",           "impact": "Medium", "effort": "Medium"},
            {"priority": 3, "action": "Test single-CTA emails vs multi-link layout",                            "impact": "Low",    "effort": "Low"},
        ],
        "info": [
            {"priority": 1, "action": "A/B test CTA wording for incremental click-rate improvement",            "impact": "Low",    "effort": "Low"},
        ],
    },
    "unsub_rate": {
        "warning": [
            {"priority": 1, "action": "Reduce sending frequency for high-volume campaigns",                   "impact": "Medium", "effort": "Low"},
            {"priority": 2, "action": "Introduce email preference center — let users choose frequency",       "impact": "Medium", "effort": "Medium"},
        ],
        "info": [
            {"priority": 1, "action": "Survey unsubscribers to understand exit reasons",                      "impact": "Low",    "effort": "Low"},
        ],
    },
}


class RecommendationAgent:

    def recommend(self, diagnosis: dict) -> dict:
        all_recs  = []
        seen      = set()

        for issue in diagnosis["issues"]:
            metric   = issue["metric"]
            severity = issue["severity"]

            recs = _RECOMMENDATIONS.get(metric, {}).get(severity, [])
            for rec in recs:
                key = rec["action"]
                if key not in seen:
                    seen.add(key)
                    all_recs.append({
                        **rec,
                        "metric":   metric,
                        "severity": severity,
                    })

        all_recs.sort(key=lambda x: (
            {"critical": 0, "warning": 1, "info": 2}.get(x["severity"], 3),
            x["priority"]
        ))

        for i, rec in enumerate(all_recs, start=1):
            rec["rank"] = i

        return {
            "recommendations": all_recs,
            "total":           len(all_recs),
            "critical_actions": [r for r in all_recs if r["severity"] == "critical"],
            "quick_wins":       [r for r in all_recs if r["effort"] == "Low"],
        }
