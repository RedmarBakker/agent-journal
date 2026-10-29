import argparse

from journal.console.console import Console
from journal.console.support.outcome import Outcome
from journal.support.caller import Caller
from journal.support.listener_queue import ListenerQueue
from journal.support.agent_role import AgentRole


class SuiteConsole:
    """The console as a test runs it: a command's listeners that run after the answer have run before the test's next step, as the server's queue runs them before the agent's next hook."""

    def __init__(self, console: Console, deferred: ListenerQueue) -> None:
        self.console, self.deferred = console, deferred

    def run(self, argv: list[str], caller: Caller) -> Outcome:
        outcome = self.console.run(argv, caller)
        self.deferred.drain()
        return outcome

    def parser(self, role: AgentRole) -> argparse.ArgumentParser:
        return self.console.parser(role)
