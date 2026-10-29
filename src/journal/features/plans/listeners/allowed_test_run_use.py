from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.repositories.plans import Plans
from journal.support.actor import Actor


class AllowedTestRunUse(AgentListener[ToolStarting]):
    """A test run the agent starts uses one test run its started plan allowed mid-phase, so the next waits for the phase end again."""

    def __init__(self, plans: Plans) -> None:
        self.plans = plans

    def handle(self, event: ToolStarting) -> None:
        if not event.call.test_runs():
            return
        for plan in self.plans.allowing_test_runs():
            self.plans.save(plan.with_allowed_test_run_used(), Actor.agent(event.session))
