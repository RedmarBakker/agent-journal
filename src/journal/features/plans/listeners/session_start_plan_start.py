from journal.events.agent_listener import AgentListener
from journal.events.agent.session_started import SessionStarted
from journal.features.plans.support.approved_plan_start import ApprovedPlanStart


class SessionStartPlanStart(AgentListener[SessionStarted]):
    """At a session start with no plan started, the oldest approved plan starts by itself."""

    def __init__(self, start: ApprovedPlanStart) -> None:
        self.start = start

    def handle(self, event: SessionStarted) -> None:
        self.start.run()
