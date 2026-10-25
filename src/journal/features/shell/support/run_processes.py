from dataclasses import dataclass, field

from journal.features.shell.support.process_tree import ProcessTree


@dataclass
class RunProcesses:
    """For each watched output, the test processes it started beneath its shell while it ran and the command that really ran beneath it, kept in memory while the journal runs."""

    tests: dict[int, set[int]] = field(default_factory=dict)
    commands: dict[int, str] = field(default_factory=dict)

    def sampled(self, output: int, subtree: ProcessTree) -> None:
        self.tests.setdefault(output, set()).update(row.pid for row in subtree.tests())
        if inner := subtree.inner_command():
            self.commands[output] = inner

    def test_count(self, output: int) -> int:
        return len(self.tests.get(output, ()))

    def inner_command(self, output: int) -> str:
        return self.commands.get(output, "")

    def counts_suites(self, output: int, steps: int) -> bool:
        return 0 < self.test_count(output) and 0 < steps <= self.test_count(output)
