from tests.stories.fixtures.supervisor.supervisor_daily_cost import SupervisorDailyCost


class SupervisorDailyCostPending(SupervisorDailyCost):
    """A supervisor grant has an admitted run whose usage is still unsettled."""

    limit_overrides = {"max_cost_microusd_per_day": 28_000}
