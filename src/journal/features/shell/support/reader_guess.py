import re
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.reader_judge import COUNT_PATTERN, PERCENT_PATTERN, SUMMARY_PATTERN, ReaderJudge
from journal.features.shell.support.readers import Readers
from journal.models.command_output import CommandOutput
from journal.support.command_shape import CommandShape

PERCENT_PROGRESS = r"(\d+)%"
COUNT_PROGRESS = r"(\d+)\s*/\s*(\d+)"
FAILURE_PATTERN = re.compile(r"\b(?:FAILED|FAIL|ERROR|Traceback)\b|\bfailed\b|\berror:", re.IGNORECASE)


class ReaderGuess:
    """The reader a command moved to the background gets when no reader reads it: a reader of the same program that picks lines from the run's output so far, else one written by code from that output, its progress line, its summary line and its failure lines; kept as a reader of the project, tried on the output before it is offered."""

    def __init__(self, readers: Readers, judge: ReaderJudge) -> None:
        self.readers, self.judge = readers, judge

    def reader_for(self, output: CommandOutput, part: str) -> Reader | None:
        files = OutputFiles(Path(output.folder))
        lines = files.lines() if files.is_stored() else []
        name = CommandShape.command_name(part)
        if not lines or not name:
            return None
        reader = self.similar(name, lines) or self.written(name, lines)
        if reader is None or self.judge.tried(reader, lines):
            return None
        if self.readers.named(reader.name) is None:
            self.readers.add(reader)
        return self.readers.named(reader.name)

    def similar(self, name: str, lines: list[str]) -> Reader | None:
        program = name.split()[0]
        return next((reader for reader in self.readers.all() if any(own.split()[0] == program for own in reader.commands.programs) and not self.judge.tried(reader, lines)), None)

    def written(self, name: str, lines: list[str]) -> Reader | None:
        progress = PERCENT_PROGRESS if any(PERCENT_PATTERN.search(line) for line in lines) else COUNT_PROGRESS if any(COUNT_PATTERN.search(line) for line in lines) else ""
        summary = f"(?i:{SUMMARY_PATTERN.pattern})" if any(SUMMARY_PATTERN.search(line) for line in lines) else ""
        failures = f"(?i:{FAILURE_PATTERN.pattern})" if any(FAILURE_PATTERN.search(line) for line in lines) else ""
        patterns = [pattern for pattern in (failures, summary) if pattern]
        if not patterns:
            return None
        subject = " and ".join(word for word, found in (("progress", progress), ("failure lines", failures), ("summary", summary)) if found)
        return Reader(re.sub(r"[^a-z0-9]+", "-", f"{name} output".lower()).strip("-"), f"the {subject} of {name} runs, written from a run's own output", "|".join(f"(?:{pattern})" for pattern in patterns),
                      progress_pattern=progress, commands=ReaderCommands((name,)), finished_pattern=summary, failed_pattern=failures)
