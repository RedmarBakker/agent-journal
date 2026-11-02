from datetime import datetime, timezone

from tests.stories.fixtures.supervisor.supervisor_scheduled_wake import SupervisorScheduledWake


DAILY_COST_START = datetime(2026, 11, 3, 23, 45, tzinfo=timezone.utc).timestamp()


class SupervisorDailyCost(SupervisorScheduledWake):
    """A supervisor grant starts just before a UTC day ends with one run's cost as its cap."""

    pinned_at = DAILY_COST_START
    limit_overrides = {"max_cost_microusd_per_day": 14_000}
