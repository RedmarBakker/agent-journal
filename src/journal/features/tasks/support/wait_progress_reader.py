import re
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.tasks.support.wait_progress import WaitProgress
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs

PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
COUNT = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")


class WaitProgressReader:
    """The progress of the runs of a session still going, by the row of each: its last percentage, or its last count or step such as 2/5, and how long the run before it, of the same line, took."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def running(self, session: str) -> dict[str, WaitProgress]:
        return {f"{run.table()}:{run.id}": self.progress(run) for run in self.outputs.matching(session=session, ended=False)}

    def progress(self, run: CommandOutput) -> WaitProgress:
        files = OutputFiles(Path(run.folder))
        previous = self.outputs.previous_run(run)
        return WaitProgress(run.creation_time.timestamp(), self.finished_share(files.lines() if files.is_stored() else []), previous.run_seconds() if previous else 0.0)

    @staticmethod
    def finished_share(lines: list[str]) -> float:
        for line in reversed(lines):
            percent, count = PERCENT.findall(line), COUNT.findall(line)
            if percent:
                return min(float(percent[-1]) / 100, 1.0)
            if count and int(count[-1][1]):
                return min(int(count[-1][0]) / int(count[-1][1]), 1.0)
        return 0.0
