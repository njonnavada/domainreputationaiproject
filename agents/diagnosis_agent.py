import json
from pathlib import Path

_thresholds_path = Path(__file__).parent.parent / "config" / "thresholds.json"

_DIAGNOSIS_RULES = [
    {
        "metric":          "delivery_rate",
        "higher_is_better": True,
        "severity_bad":    "critical",
        "severity_avg":    "warning",
        "reason_bad":      "Critically low delivery rate — most emails not reaching inboxes",
        "reason_avg":      "Below-average delivery rate — inbox placement needs attention",
        "detail_bad":      "Less than 90% of sent emails are being delivered. This signals ISP blocks, IP blacklisting, or domain reputation damage.",
        "detail_avg":      "Delivery rate is between 90–95%. Minor ISP filtering or list quality issues may be present.",
    },
    {
        "metric":          "open_rate",
        "higher_is_better": True,
        "severity_bad":    "critical",
        "severity_avg":    "warning",
        "reason_bad":      "Very low open rate — recipients not engaging with emails",
        "reason_avg":      "Below-average open rate — subject lines or sender reputation may be weak",
        "detail_bad":      "Under 10% open rate indicates poor sender reputation, spam folder placement, or unengaged list.",
        "detail_avg":      "Open rate between 10–20%. Room to improve via better subject lines and send-time optimization.",
    },
    {
        "metric":          "genuine_open_rate",
        "higher_is_better": True,
        "severity_bad":    "critical",
        "severity_avg":    "warning",
        "reason_bad":      "Very low genuine (human) open rate — bot opens masking real engagement",
        "reason_avg":      "Genuine open rate is below target — actual human engagement is limited",
        "detail_bad":      "Genuine opens under 8% suggest the list has poor human engagement. Bot-inflated opens may hide deeper reputation issues.",
        "detail_avg":      "Genuine opens between 8–15%. Consider list hygiene and re-engagement campaigns.",
    },
    {
        "metric":          "abuse_rate",
        "higher_is_better": False,
        "severity_bad":    "critical",
        "severity_avg":    "warning",
        "reason_bad":      "High spam complaint (abuse) rate — serious reputation risk",
        "reason_avg":      "Elevated spam complaint rate — approaching ISP threshold",
        "detail_bad":      "Abuse rate above 0.3% triggers ISP reputation penalties and can lead to domain blacklisting.",
        "detail_avg":      "Abuse rate between 0.1–0.3%. Monitor closely — exceeding 0.3% causes ISP throttling.",
    },
    {
        "metric":          "hard_error_rate",
        "higher_is_better": False,
        "severity_bad":    "critical",
        "severity_avg":    "warning",
        "reason_bad":      "High hard bounce rate — large volume of invalid addresses",
        "reason_avg":      "Elevated hard bounce rate — list contains stale or invalid addresses",
        "detail_bad":      "Hard bounce rate above 5% indicates a severely outdated or low-quality list. ISPs penalize domains for repeated delivery attempts to invalid addresses.",
        "detail_avg":      "Hard bounce rate between 2–5%. Regular list cleaning and suppression updates are needed.",
    },
    {
        "metric":          "click_rate",
        "higher_is_better": True,
        "severity_bad":    "warning",
        "severity_avg":    "info",
        "reason_bad":      "Very low click-through rate — email content not driving action",
        "reason_avg":      "Below-average click rate — call-to-action effectiveness can be improved",
        "detail_bad":      "Click rate under 1% suggests content relevance issues or poor placement of CTAs.",
        "detail_avg":      "Click rate between 1–2%. A/B testing subject lines and CTAs could improve this.",
    },
    {
        "metric":          "unsub_rate",
        "higher_is_better": False,
        "severity_bad":    "warning",
        "severity_avg":    "info",
        "reason_bad":      "High unsubscribe rate — recipients opting out at an elevated pace",
        "reason_avg":      "Slightly elevated unsubscribe rate — sending frequency or content relevance may need review",
        "detail_bad":      "Unsub rate above 1% indicates content-audience mismatch or over-mailing.",
        "detail_avg":      "Unsub rate between 0.5–1%. Review content personalization and mailing cadence.",
    },
]


def _load_config():
    with open(_thresholds_path) as f:
        return json.load(f)


class DiagnosisAgent:

    def diagnose(self, metrics: dict, custom_thresholds: dict = None) -> dict:
        config     = _load_config()
        thresholds = custom_thresholds if custom_thresholds else config["thresholds"]

        issues    = []
        positives = []

        for rule in _DIAGNOSIS_RULES:
            metric = rule["metric"]
            value  = metrics.get(metric, 0)
            good   = thresholds[metric]["good"]
            avg    = thresholds[metric]["average"]

            if rule["higher_is_better"]:
                is_bad = value < avg
                is_avg = avg <= value < good
                is_good= value >= good
            else:
                is_bad = value > avg
                is_avg = good < value <= avg
                is_good= value <= good

            if is_bad:
                issues.append({
                    "metric":    metric,
                    "value":     value,
                    "severity":  rule["severity_bad"],
                    "reason":    rule["reason_bad"],
                    "detail":    rule["detail_bad"],
                })
            elif is_avg:
                issues.append({
                    "metric":    metric,
                    "value":     value,
                    "severity":  rule["severity_avg"],
                    "reason":    rule["reason_avg"],
                    "detail":    rule["detail_avg"],
                })
            elif is_good:
                positives.append({
                    "metric":  metric,
                    "value":   value,
                    "message": f"{metric.replace('_', ' ').title()} is performing well ({value}%)",
                })

        severity_order = {"critical": 0, "warning": 1, "info": 2}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return {
            "issues":    issues,
            "positives": positives,
            "issue_count":    len(issues),
            "critical_count": sum(1 for i in issues if i["severity"] == "critical"),
            "warning_count":  sum(1 for i in issues if i["severity"] == "warning"),
        }
