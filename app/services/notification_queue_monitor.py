"""Read-only monitoring and operational summaries for notification queues."""
class NotificationQueueMonitor:
    def __init__(self, reliability_service):
        self.reliability = reliability_service

    def summary(self, organization_id=None):
        metrics = self.reliability.metrics(organization_id)
        total = metrics["total"]
        metrics["failure_rate"] = round((metrics["failed"] + metrics["dead_letter"]) / total, 4) if total else 0.0
        metrics["attention_required"] = metrics["dead_letter"] > 0 or metrics["failed"] > 0
        return metrics
