import json
from pathlib import Path

_thresholds_path = Path(__file__).parent.parent / "config" / "thresholds.json"


def _load_config():
    with open(_thresholds_path) as f:
        return json.load(f)


def _score_metric(value: float, metric: str, thresholds: dict, higher_is_better: bool) -> float:
    """Returns 0-100 score for a single metric."""
    good = thresholds[metric]["good"]
    avg  = thresholds[metric]["average"]

    if higher_is_better:
        if value >= good:
            return 100.0
        elif value >= avg:
            return 50.0 + 50.0 * (value - avg) / (good - avg)
        else:
            return max(0.0, 50.0 * (value / avg)) if avg > 0 else 0.0
    else:
        if value <= good:
            return 100.0
        elif value <= avg:
            return 50.0 + 50.0 * (avg - value) / (avg - good)
        else:
            return max(0.0, 50.0 * (avg / value)) if value > 0 else 100.0


class ClassifierAgent:

    def classify(self, metrics: dict, custom_thresholds: dict = None) -> dict:
        config = _load_config()
        thresholds = custom_thresholds if custom_thresholds else config["thresholds"]
        weights    = config["weights"]
        cls_config = config["classification"]

        metric_map = {
            "open_rate":         (metrics.get("open_rate", 0),         True),
            "genuine_open_rate": (metrics.get("genuine_open_rate", 0), True),
            "click_rate":        (metrics.get("click_rate", 0),        True),
            "delivery_rate":     (metrics.get("delivery_rate", 0),     True),
            "abuse_rate":        (metrics.get("abuse_rate", 0),        False),
            "hard_error_rate":   (metrics.get("hard_error_rate", 0),   False),
            "unsub_rate":        (metrics.get("unsub_rate", 0),        False),
        }

        scores     = {}
        weighted   = 0.0
        total_w    = 0.0

        for metric, (value, higher_is_better) in metric_map.items():
            s = _score_metric(value, metric, thresholds, higher_is_better)
            scores[metric] = round(s, 1)
            weighted  += s * weights[metric]
            total_w   += weights[metric]

        overall_score = round(weighted / total_w, 1) if total_w > 0 else 0.0

        if overall_score >= cls_config["good_min_score"]:
            label  = "GOOD"
            color  = "green"
            emoji  = "✅"
        elif overall_score >= cls_config["average_min_score"]:
            label  = "AVERAGE"
            color  = "orange"
            emoji  = "⚠️"
        else:
            label  = "BAD"
            color  = "red"
            emoji  = "❌"

        return {
            "label":         label,
            "color":         color,
            "emoji":         emoji,
            "overall_score": overall_score,
            "metric_scores": scores,
        }
