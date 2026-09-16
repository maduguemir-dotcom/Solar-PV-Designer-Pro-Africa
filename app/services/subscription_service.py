"""Stage 5B subscription plans, feature flags and usage enforcement.

This module intentionally contains no payment provider integration. It defines
commercial entitlements and a replaceable subscription boundary for the later
payment stage.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository


@dataclass(frozen=True)
class Plan:
    code: str
    name: str
    description: str
    limits: dict[str, Optional[int]]
    features: frozenset[str]

    def limit_for(self, metric: str) -> Optional[int]:
        return self.limits.get(metric)


PLANS = {
    "free": Plan(
        "free", "FREE", "For learning, small projects and evaluation.",
        {
            "customers": 10,
            "sites": 10,
            "projects": 3,
            "design_runs": 10,
            "professional_designs_saved": 3,
            "professional_reports_generated": 3,
            "design_versions_created": 5,
            "team_members": 1,
        },
        frozenset({"basic_design", "basic_reports", "basic_equipment"}),
    ),
    "professional": Plan(
        "professional", "PROFESSIONAL", "For solar installers and energy professionals.",
        {
            "customers": 250,
            "sites": 250,
            "projects": 100,
            "design_runs": 250,
            "professional_designs_saved": 100,
            "professional_reports_generated": 100,
            "design_versions_created": 250,
            "team_members": 5,
        },
        frozenset({"basic_design", "advanced_design", "professional_reports", "equipment_library", "design_history", "ai_assistance"}),
    ),
    "business": Plan(
        "business", "BUSINESS", "For solar companies and multi-staff engineering teams.",
        {
            "customers": None,
            "sites": None,
            "projects": None,
            "design_runs": None,
            "professional_designs_saved": None,
            "professional_reports_generated": None,
            "design_versions_created": None,
            "team_members": 25,
        },
        frozenset({"basic_design", "advanced_design", "professional_reports", "equipment_library", "design_history", "ai_assistance", "team_management", "branded_reports", "business_analytics"}),
    ),
}

METRIC_LABELS = {
    "customers": "Customers",
    "sites": "Installation sites",
    "projects": "Projects",
    "design_runs": "Design runs",
    "professional_designs_saved": "Professional designs saved",
    "professional_reports_generated": "Professional reports",
    "design_versions_created": "Design versions",
    "team_members": "Team members",
}

class UsageLimitError(ValueError):
    """Raised when an organization has exhausted a plan entitlement."""


class SubscriptionService:
    def __init__(self, database: Optional[PlatformDatabase] = None):
        self.database = database or PlatformDatabase()
        self.repository = PlatformRepository(self.database)

    @staticmethod
    def plans() -> dict[str, Plan]:
        return PLANS.copy()

    def ensure_subscription(self, organization_id: str) -> dict:
        subscription = self.repository.get_subscription(organization_id)
        if subscription:
            return subscription
        subscription_id = self.repository.create_subscription(organization_id, "free", "active")
        return self.repository.get_one("subscriptions", subscription_id) or {
            "id": subscription_id, "organization_id": organization_id,
            "plan_code": "free", "status": "active"
        }

    def current_plan(self, organization_id: str) -> Plan:
        sub = self.ensure_subscription(organization_id)
        code = sub.get("plan_code", "free")
        return PLANS.get(code, PLANS["free"])

    def subscription(self, organization_id: str) -> dict:
        return self.ensure_subscription(organization_id)

    @staticmethod
    def _month_start() -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-01 00:00:00")

    def usage_this_month(self, organization_id: str, metric: str) -> int:
        return self.repository.usage_since(organization_id, metric, self._month_start())

    def remaining(self, organization_id: str, metric: str) -> Optional[int]:
        limit = self.current_plan(organization_id).limit_for(metric)
        if limit is None:
            return None
        return max(0, limit - self.usage_this_month(organization_id, metric))

    def check_limit(self, organization_id: str, metric: str, quantity: int = 1) -> bool:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        limit = self.current_plan(organization_id).limit_for(metric)
        if limit is None:
            return True
        return self.usage_this_month(organization_id, metric) + quantity <= limit

    def require_limit(self, organization_id: str, metric: str, quantity: int = 1) -> None:
        if self.check_limit(organization_id, metric, quantity):
            return
        plan = self.current_plan(organization_id)
        label = METRIC_LABELS.get(metric, metric.replace("_", " ").title())
        limit = plan.limit_for(metric)
        raise UsageLimitError(
            f"{label} limit reached for the {plan.name} plan ({limit} per month). "
            "Upgrade your plan to continue."
        )

    def record_if_allowed(self, organization_id: str, metric: str, quantity: int = 1) -> str:
        self.require_limit(organization_id, metric, quantity)
        return self.repository.record_usage(organization_id, metric, quantity)

    def feature_enabled(self, organization_id: str, feature: str) -> bool:
        return feature in self.current_plan(organization_id).features

    def set_plan(self, organization_id: str, plan_code: str, status: str = "active") -> dict:
        if plan_code not in PLANS:
            raise ValueError(f"Unknown plan: {plan_code}")
        self.ensure_subscription(organization_id)
        self.repository.update_subscription_for_org(organization_id, plan_code, status)
        return self.subscription(organization_id)

    def usage_summary(self, organization_id: str) -> list[dict]:
        plan = self.current_plan(organization_id)
        rows = []
        for metric, limit in plan.limits.items():
            used = self.usage_this_month(organization_id, metric)
            rows.append({
                "metric": metric,
                "label": METRIC_LABELS.get(metric, metric.replace("_", " ").title()),
                "used": used,
                "limit": limit,
                "remaining": None if limit is None else max(0, limit - used),
            })
        return rows
