from tests.stories.fixtures.supervisor.supervisor_daily_cost import SupervisorDailyCost


class SupervisorDailyCostBelowCap(SupervisorDailyCost):
    """A supervisor grant can afford one settled run and reserve another on the same UTC day."""

    daily_cost_limit_microusd = SupervisorDailyCost.daily_cost_limit_microusd * 2
