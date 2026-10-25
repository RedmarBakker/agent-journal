from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.repositories.checks import Checks
from journal.support.actor import Actor
from journal.features.checks.checks_nudges import ChecksNudges


class CheckFailureRecord(AgentListener[LineDelivered]):
    """A failing check reported to the agent is marked on its row with the time it was reported, so it is reported again only once the set minutes have passed."""

    def __init__(self, checks: Checks) -> None:
        self.checks = checks

    def handle(self, event: LineDelivered) -> None:
        if event.nudge not in (ChecksNudges.CHECK_FAILED.key, ChecksNudges.CHECK_FAILURE_REPEAT.key):
            return
        self.checks.rewritten(self.checks.find(int(event.values["n"])), Actor.system(), lambda check: check.failure_reported(event.time))
