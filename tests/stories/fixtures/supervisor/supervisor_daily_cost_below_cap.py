from tests.stories.fixtures.supervisor.supervisor_daily_cost import SupervisorDailyCost


class SupervisorDailyCostBelowCap(SupervisorDailyCost):
    """A supervisor grant can afford one settled run and reserve another on the same UTC day."""

    limit_overrides = {"max_cost_microusd_per_day": 28_000}
