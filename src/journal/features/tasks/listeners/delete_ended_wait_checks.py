from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.features.tasks.support.wait_checks import WaitChecks
from journal.features.tasks.support.wait_targets import WaitTargets
from journal.models.agent import Agent
from journal.support.actor import Actor


class DeleteEndedWaitChecks(Listener[Updated]):
    """A wait the agent declared that leaves its stack, ended or lifted, takes the checks it made for itself with it."""

    def __init__(self, wait_checks: WaitChecks) -> None:
        self.wait_checks = wait_checks

    def handle(self, event: Updated) -> None:
        previous = event.previous_row(Agent)
        if previous is None:
            return
        ended = WaitTargets.awaited_checks(previous.stack) - WaitTargets.awaited_checks(event.model.stack)
        if ended:
            self.wait_checks.deleted(ended, Actor.system())
