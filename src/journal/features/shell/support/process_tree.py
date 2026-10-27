import re
import subprocess

from journal.features.shell.support.process_row import ProcessRow
from journal.support.command_classifier import CommandClassifier

LIST_COMMAND = ["ps", "-Ao", "pid=,ppid=,args="]
LIST_SECONDS = 5
# a test binary go test builds, a test runner of another tool, and the process of a worker a test runner starts
TEST_PROCESS = re.compile(r"^\S*\.test(?:\s|$)|(?:^|[\s/])(?:pytest|py\.test|jest|vitest|phpunit|rspec|mocha)(?:\s|$)|execnet|exec\(eval\(sys\.stdin")


class ProcessTree:
    """The processes of the machine as a tree by parent id: those beneath one process, the test processes among them, and the command that really runs beneath a wrapper such as a shell, a make target or a docker exec, read through the command table."""

    def __init__(self, rows: list[ProcessRow]) -> None:
        self.rows = rows

    @classmethod
    def read(cls) -> "ProcessTree":
        listed = subprocess.run(LIST_COMMAND, capture_output=True, text=True, timeout=LIST_SECONDS)
        return cls.parsed(listed.stdout)

    @classmethod
    def parsed(cls, text: str) -> "ProcessTree":
        rows = [ProcessRow(int(fields[0]), int(fields[1]), fields[2]) for line in text.splitlines() if len(fields := line.strip().split(None, 2)) == 3 and fields[0].isdigit() and fields[1].isdigit()]
        return cls(rows)

    def descendants(self, pid: int) -> "ProcessTree":
        children: dict[int, list[ProcessRow]] = {}
        for row in self.rows:
            children.setdefault(row.parent, []).append(row)
        members, level = [], children.get(pid, [])
        while level:
            members.extend(level)
            level = [child for row in level for child in children.get(row.pid, [])]
        return ProcessTree(members)

    def tests(self) -> list[ProcessRow]:
        return [row for row in self.rows if TEST_PROCESS.search(row.command)]

    def inner_command(self, classifier: CommandClassifier) -> str:
        return next((command for row in self.rows if (command := classifier.process_command(row.command))), "")
