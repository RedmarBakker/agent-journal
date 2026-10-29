"""Cap decisions for plan estimates and account-wide running seats."""

from dataclasses import dataclass

from journal.features.organization.support.usage_ledger import UsageEstimate
from journal.features.workers.organization_options import OrganizationOptions
from journal.repositories.setting_rows import SettingRows


@dataclass(frozen=True)
class CapDecision:
    status: str
    limit: float
    observed: float | None
    reason: str

    @property
    def allowed(self) -> bool:
        return self.status == "within"


class Caps:
    """Keep plan Estimated API cost budgets and shared-rig seats separate from subscription limits."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def seats(self, active_seats: int) -> CapDecision:
        limit = self.settings.integer(OrganizationOptions.SEAT_CAP)
        if not limit or active_seats < limit:
            return CapDecision("within", float(limit), float(active_seats), "")
        return CapDecision("full", float(limit), float(active_seats), f"the shared OpenRig seat cap is {limit}")

    def plan_cost(self, estimate: UsageEstimate) -> CapDecision:
        limit = self.settings.decimal(OrganizationOptions.COST_CAP)
        if limit <= 0:
            return CapDecision("within", limit, estimate.amount_usd, "")
        if estimate.amount_usd is not None and estimate.amount_usd >= limit:
            return CapDecision("exceeded", limit, estimate.amount_usd,
                               f"the plan's Estimated API cost reached ${limit:.2f}; this is an estimate, not money billed or a share of a subscription")
        if estimate.status in ("missing", "stale", "unavailable") or estimate.amount_usd is None:
            return CapDecision("unknown", limit, estimate.amount_usd, f"the plan's Estimated API cost is {estimate.status}")
        if (estimate.status == "partial" or estimate.expected_seats is not None
                and estimate.observed_seats < estimate.expected_seats):
            return CapDecision("unknown", limit, estimate.amount_usd,
                               f"the plan's Estimated API cost has incomplete seat coverage ({estimate.coverage})")
        return CapDecision("within", limit, estimate.amount_usd, "")
