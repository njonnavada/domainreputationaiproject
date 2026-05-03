from data_layer.api_client import fetch_domain_metrics
from agents.classifier_agent import ClassifierAgent
from agents.diagnosis_agent import DiagnosisAgent
from agents.recommendation_agent import RecommendationAgent


class DomainReputationOrchestrator:

    def __init__(self):
        self.classifier     = ClassifierAgent()
        self.diagnosis      = DiagnosisAgent()
        self.recommendation = RecommendationAgent()

    def analyze(self, domain: str, start_date: str, end_date: str,
                custom_thresholds: dict = None) -> dict:

        # Step 1 — Fetch real metrics from API
        metrics = fetch_domain_metrics(domain, start_date, end_date)

        # Step 2 — Classify reputation
        classification = self.classifier.classify(metrics, custom_thresholds)

        # Step 3 — Diagnose root causes
        diagnosis = self.diagnosis.diagnose(metrics, custom_thresholds)

        # Step 4 — Generate recommendations
        recommendations = self.recommendation.recommend(diagnosis)

        return {
            "domain":          domain,
            "start_date":      start_date,
            "end_date":        end_date,
            "data_source":     metrics.get("source", "unknown"),
            "metrics":         metrics,
            "classification":  classification,
            "diagnosis":       diagnosis,
            "recommendations": recommendations,
        }
