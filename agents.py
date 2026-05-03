# agents.py

def diagnose(domain):
    reasons = []

    if domain["bounceRate"] > 10:
        reasons.append("High bounce rate")

    if domain["openRate"] < 10:
        reasons.append("Low open rate")

    if domain["complaintRate"] > 1:
        reasons.append("High spam complaints")

    return reasons


def recommend(reasons):
    actions = []

    for r in reasons:
        if "bounce" in r:
            actions.append("Clean email list")

        if "open" in r:
            actions.append("Improve subject lines")

        if "complaints" in r:
            actions.append("Reduce sending frequency")

    return actions