from journal.events.listener import Listener
from journal.events.rows.row_resolved import RowResolved
from journal.features.tasks.support.task_test_runs import TaskTestRuns
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.support.actor import Actor


class TestingRunEnd(Listener[RowResolved]):
    """A run that ended settles the tasks waiting in testing on it."""

    def __init__(self, outputs: CommandOutputs, runs: TaskTestRuns) -> None:
        self.outputs, self.runs = outputs, runs

    def handle(self, event: RowResolved) -> None:
        table, _, number = event.ref.partition(":")
        if table == CommandOutput.table():
            self.runs.finish_tests(self.outputs.find(int(number)), Actor.system())
