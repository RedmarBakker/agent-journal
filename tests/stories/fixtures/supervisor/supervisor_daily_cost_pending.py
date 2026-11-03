from tests.stories.fixtures.supervisor.supervisor_daily_cost import SupervisorDailyCost


class SupervisorDailyCostPending(SupervisorDailyCost):
    """A supervisor grant has an admitted run whose usage is still unsettled."""

    daily_cost_limit_microusd = SupervisorDailyCost.daily_cost_limit_microusd * 2
    owner_route = "/journal/plans/{plan_id}/supervisor/wakeups"
