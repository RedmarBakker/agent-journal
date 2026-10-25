import re
import subprocess

from journal.features.shell.support.process_row import ProcessRow

LIST_COMMAND = ["ps", "-Ao", "pid=,ppid=,args="]
LIST_SECONDS = 5
# a test binary go test builds, a test runner of another tool, and the process of a worker a test runner starts
TEST_PROCESS = re.compile(r"^\S*\.test(?:\s|$)|(?:^|[\s/])(?:pytest|py\.test|jest|vitest|phpunit|rspec|mocha)(?:\s|$)|execnet|exec\(eval\(sys\.stdin")
# the programs that only start another command
WRAPPERS = frozenset({"sh", "bash", "zsh", "dash", "env", "timeout", "time", "nohup", "sudo", "make", "docker", "journal", "script"})
SHELLS = frozenset({"sh", "bash", "zsh", "dash"})
DOCKER_FLAGS_WITH_VALUE = frozenset({"-e", "--env", "-u", "--user", "-w", "--workdir", "--name", "-v", "--volume", "--network", "-m", "--memory", "--cpus"})


class ProcessTree:
    """The processes of the machine as a tree by parent id: those beneath one process, the test processes among them, and the command that really runs beneath a wrapper such as a shell, a make target or a docker exec."""

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

    def inner_command(self) -> str:
        return next((command for row in self.rows if (command := self.unwrapped(row.command))), "")

    @classmethod
    def unwrapped(cls, command: str) -> str:
        tokens = command.split()
        while tokens and tokens[0].rsplit("/", 1)[-1] in WRAPPERS:
            program, tokens = tokens[0].rsplit("/", 1)[-1], tokens[1:]
            if program in SHELLS:
                return " ".join(tokens[1:]).strip("'\"") if tokens[:1] == ["-c"] else ""
            tokens = cls.wrapped_arguments(program, tokens)
        return " ".join(tokens)

    @staticmethod
    def wrapped_arguments(program: str, tokens: list[str]) -> list[str]:
        if program == "docker":
            return ProcessTree.container_arguments(tokens)
        if program == "timeout":
            return tokens[1:]
        if program == "env":
            return [token for token in tokens if "=" not in token or token.startswith("-")]
        return [] if program in ("make", "journal", "script") else tokens

    @staticmethod
    def container_arguments(tokens: list[str]) -> list[str]:
        if tokens[:1] != ["exec"]:
            return []
        remaining, skipping = tokens[1:], False
        for index, token in enumerate(remaining):
            if skipping:
                skipping = False
            elif token in DOCKER_FLAGS_WITH_VALUE:
                skipping = True
            elif not token.startswith("-"):
                return remaining[index + 1:]
        return []
