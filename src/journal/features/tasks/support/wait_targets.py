from journal.events.models.updated import Updated
from journal.features.tasks.support.task_state_names import EXTERNAL_WAIT
from journal.models.check import Check
from journal.models.command_output import CommandOutput
from journal.models.question import Question
from journal.models.task import Task
from journal.repositories.checks import Checks
from journal.repositories.command_outputs import CommandOutputs

WAIT_TARGETS = (CommandOutput, Task, Question, Check)
POLL_INTERVAL_MINUTES = 0.5


class WaitTargets:
    """What an agent's wait ends on, by table:id, the rows it may name, and the one place that checks whether a write resolved a row something waits on, and the checks an agent's waits on its stack end on."""

    def __init__(self, outputs: CommandOutputs, checks: Checks) -> None:
        self.outputs, self.checks = outputs, checks

    def output(self, n: int) -> str:
        return self.ref(self.outputs.find(n))

    def polled_check(self, command: str, purpose: str, actor) -> str:
        check = self.checks.save(Check(title=f"the wait for {purpose} ends when this passes", command=command, interval=POLL_INTERVAL_MINUTES, wait_target=True), actor)
        return self.ref(check)

    @staticmethod
    def ref(row: CommandOutput | Check) -> str:
        return f"{row.table()}:{row.id}"

    @staticmethod
    def wait_check_ids(stack: tuple) -> set[int]:
        return WaitTargets.wait_row_ids(stack, Check.table())

    @staticmethod
    def wait_output_ids(stack: tuple) -> set[int]:
        return WaitTargets.wait_row_ids(stack, CommandOutput.table())

    @staticmethod
    def wait_row_ids(stack: tuple, table: str) -> set[int]:
        prefix = f"{table}:"
        return {int(ref.removeprefix(prefix)) for frame in stack if frame.get("state") == EXTERNAL_WAIT for ref in frame.get("data", {}).get("end_refs", "").split(",") if ref.startswith(prefix)}

    @staticmethod
    def title(name: str) -> str:
        table, _, number = name.partition(":")
        return f"{'output' if table == CommandOutput.table() else 'check'} {number}"

    @staticmethod
    def is_newly_resolved(event: Updated) -> bool:
        model = event.model
        if not isinstance(model, WAIT_TARGETS):
            return False
        prior_row = event.previous_row(type(model))
        return model.is_resolved() and (prior_row is None or not prior_row.is_resolved())
