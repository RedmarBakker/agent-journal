
from journal.events.clock_ticked import ClockTicked
from journal.features.checks.support.check_runner import CheckRunner
from journal.events.listener import Listener
from journal.support.actor import Actor
from journal.repositories.checks import Checks
from journal.support.time_source import TimeSource


class RunDueChecks(Listener[ClockTicked]):
    """Every tick, the checks whose interval has passed start, each on a thread of its own, so a slow check never holds the clock and the other jobs; one still running is not started again."""

    def __init__(self, checks: Checks, runner: CheckRunner, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.checks, self.runner = checks, runner

    def handle(self, event: ClockTicked) -> None:
        for check in self.checks.due(self.time_source.moment()):
            self.runner.start(check, Actor.system())
