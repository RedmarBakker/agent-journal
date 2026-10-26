from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.features.tasks.support.passed_wait_checks import PassedWaitChecks
from journal.features.tasks.support.wait_targets import WaitTargets
from journal.models.agent import Agent
from journal.support.actor import Actor


class DeleteEndedWaitChecks(Listener[Updated]):
    """A wait the agent declared that leaves its stack because what it waited on happened takes the checks it made for itself with it; a wait lifted or cleared leaves them to run."""

    def __init__(self, passed_checks: PassedWaitChecks) -> None:
        self.passed_checks = passed_checks

    def handle(self, event: Updated) -> None:
        previous = event.previous_row(Agent)
        if previous is None:
            return
        ended = WaitTargets.awaited_checks(previous.stack) - WaitTargets.awaited_checks(event.model.stack)
        if ended:
            self.passed_checks.deleted(ended, Actor.system())
