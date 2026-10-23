from datetime import datetime, timezone

from journal.events.clock_ticked import ClockTicked
from journal.features.checks.support.check_runner import CheckRunner
from journal.events.listener import Listener
from journal.support.actor import Actor
from journal.repositories.checks import Checks
from journal.sync.hosting import Hosting


class RunDueChecks(Listener[ClockTicked]):
    """Every tick, the checks whose interval has passed start, each on a thread of its own, so a slow check never holds the clock and the other jobs; one still running is not started again; a hosted journal runs none, having no checkout to run them in."""

    def __init__(self, checks: Checks, runner: CheckRunner, hosting: Hosting) -> None:
        self.checks, self.runner, self.hosting = checks, runner, hosting

    def handle(self, event: ClockTicked) -> None:
        if self.hosting.is_hosted():
            return
        for check in self.checks.due(datetime.now(timezone.utc)):
            self.runner.start(check, Actor.system())
