import os
import re
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path

from journal.features.shell.support.progress import Progress
from journal.features.shell.support.step_tally import StepTally
from journal.features.shell.support.reader_commands import COMMANDS_PREFIX, ReaderCommands
from journal.models.command_output import ACTIVE, FAILED, FINISHED
from journal.support.rejection import Rejection

PROGRESS_PREFIX = "progress: "
LABEL_PREFIX = "label: "
STEP_PREFIX = "step: "
TOPIC_PREFIX = "topic: "
FINISHED_PREFIX = "finished: "
FAILED_PREFIX = "failed: "
PREFIXES = (PROGRESS_PREFIX, LABEL_PREFIX, COMMANDS_PREFIX, STEP_PREFIX, TOPIC_PREFIX, FINISHED_PREFIX, FAILED_PREFIX)
SCRIPT_SECONDS = 30
STAGE_VARIABLE = "JOURNAL_OUTPUT_STAGE"


@dataclass(frozen=True)
class Reader:
    """A named way to read outputs of one shape: the lines it picks, by a pattern, with their numbers, or by a script of the project's handed the output on its input and in JOURNAL_OUTPUT_STAGE whether the command runs, finished or failed; the lines its finished and failed patterns pick once the command ended so; how far the command has come by the last match of a progress pattern, read on the output or on what its script prints; the commands whose output it reads; and what a run is about, picked from its command line by a topic pattern."""

    name: str
    subject: str
    pattern: str
    progress_pattern: str = ""
    label: str = ""
    commands: ReaderCommands = ReaderCommands()
    step_pattern: str = ""
    topic_pattern: str = ""
    finished_pattern: str = ""
    failed_pattern: str = ""
    script: str = ""
    stage: str = ACTIVE

    def revised(self, **changes: object) -> "Reader":
        return replace(self, **{name: value for name, value in changes.items() if value is not None})

    @classmethod
    def loaded(cls, path: Path) -> "Reader":
        return cls.scripted(path) if path.suffix == ".sh" else cls.patterned(path)

    @classmethod
    def scripted(cls, path: Path) -> "Reader":
        notes = [line.removeprefix("#").strip() for line in path.read_text().splitlines() if line.startswith("#") and not line.startswith("#!")]
        settings = {prefix: note.removeprefix(prefix) for note in notes for prefix in PREFIXES if note.startswith(prefix)}
        subject = next((note for note in notes if not note.startswith(PREFIXES)), "")
        return cls(path.stem, subject, "", settings.get(PROGRESS_PREFIX, ""), settings.get(LABEL_PREFIX, ""), ReaderCommands.parsed(settings.get(COMMANDS_PREFIX, "")), settings.get(STEP_PREFIX, ""), settings.get(TOPIC_PREFIX, ""), settings.get(FINISHED_PREFIX, ""), settings.get(FAILED_PREFIX, ""), str(path))

    @classmethod
    def patterned(cls, path: Path) -> "Reader":
        lines = path.read_text().splitlines()
        if len(lines) < 2:
            raise Rejection(f"reader {path.stem} needs two lines: '# what it picks', then its pattern")
        settings = {prefix: line.removeprefix(prefix) for line in lines[2:] for prefix in PREFIXES if line.startswith(prefix)}
        return cls(path.stem, lines[0].removeprefix("#").strip(), lines[1], settings.get(PROGRESS_PREFIX, ""), settings.get(LABEL_PREFIX, ""), ReaderCommands.parsed(settings.get(COMMANDS_PREFIX, "")), settings.get(STEP_PREFIX, ""), settings.get(TOPIC_PREFIX, ""), settings.get(FINISHED_PREFIX, ""), settings.get(FAILED_PREFIX, ""))

    def settings(self) -> list[str]:
        values = (self.progress_pattern, self.label, self.commands.text(), self.step_pattern, self.topic_pattern, self.finished_pattern, self.failed_pattern)
        return [f"{prefix}{value}" for prefix, value in zip(PREFIXES, values) if value]

    def text(self) -> str:
        return "\n".join([f"# {self.subject}", self.pattern, *self.settings()]) + "\n"

    def script_text(self, body: str) -> str:
        return "".join(f"# {line}\n" for line in [self.subject, *self.settings()]) + body

    def topic(self, line: str) -> str:
        if not self.topic_pattern:
            return ""
        topics = [next((group for group in match.groups() if group), match.group(0)) if match.groups() else match.group(0) for match in re.finditer(self.topic_pattern, line)]
        return ", ".join(dict.fromkeys(Path(item.strip("'\"")).name if "/" in item else item.strip("'\"") for item in topics))

    def variant(self, stage: str) -> "Reader":
        pattern = {FINISHED: self.finished_pattern, FAILED: self.failed_pattern}.get(stage, "")
        return replace(self, stage=stage, pattern=pattern or self.pattern)

    def is_counting(self) -> bool:
        return bool(self.progress_pattern)

    def matches(self, command: str) -> bool:
        return bool(self.pattern) and self.pattern in command

    # the lines picked with their numbers in the output; a script's lines are its own, so they carry none
    def read(self, lines: list[str]) -> list[str]:
        return self.script_lines(lines) if self.script else [f"{i}: {line}" for i, line in self.picked_lines(lines)]

    def card_lines(self, lines: list[str]) -> list[str]:
        return [line for _, line in self.picked_lines(lines)]

    def picked_lines(self, lines: list[str]) -> list[tuple[int, str]]:
        if self.script:
            return list(enumerate(self.script_lines(lines), 1))
        rows = re.compile(self.pattern)
        return [(i, line) for i, line in enumerate(lines, 1) if rows.search(line)]

    def script_lines(self, lines: list[str]) -> list[str]:
        try:
            completed = subprocess.run(["sh", self.script], input="\n".join(lines) + "\n", env={**os.environ, STAGE_VARIABLE: self.stage}, capture_output=True, text=True, timeout=SCRIPT_SECONDS)
        except subprocess.TimeoutExpired as late:
            raise Rejection(f"reader {self.name} took more than {SCRIPT_SECONDS} seconds") from late
        if completed.returncode != 0:
            raise Rejection(f"reader {self.name} failed with code {completed.returncode}: {completed.stderr.strip()[-300:]}")
        return completed.stdout.splitlines()

    # the lines its progress and steps are read on: the output itself, or what its script prints of it
    def measured(self, lines: list[str]) -> list[str]:
        return self.script_lines(lines) if self.script else lines

    def progress(self, lines: list[str]) -> Progress:
        return Progress.found(self.progress_pattern, self.label, self.measured(lines), self.step_pattern) if self.progress_pattern else Progress.empty()

    def tally(self, lines: list[str]) -> StepTally:
        return StepTally.counted(self.step_pattern, self.progress_pattern, self.measured(lines)) if self.step_pattern else StepTally(0, 0)
