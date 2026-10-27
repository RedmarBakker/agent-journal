import re
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.tasks.support.wait_progress import WaitProgress
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs

PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
COUNT = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")
STEP = re.compile(r"\bstep (\d+)\s*/\s*(\d+)\b")


class WaitProgressReader:
    """The progress of the runs of a session still going, by the row of each: its last percentage, its last count such as 12/40 finished, or its last step such as step 2/5, which counts the steps before it as done, how long the run before it, of the same line, took, and when it last printed."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def running(self, session: str) -> dict[str, WaitProgress]:
        return {f"{run.table()}:{run.id}": self.progress(run) for run in self.outputs.matching(session=session, ended=False)}

    def progress(self, run: CommandOutput) -> WaitProgress:
        files = OutputFiles(Path(run.folder))
        previous = self.outputs.previous_passing_run(run)
        stored = files.is_stored()
        return WaitProgress(run.creation_time.timestamp(), self.finished_share(files.lines() if stored else []), previous.run_seconds() if previous else 0.0, files.output_time() if stored else 0.0)

    @staticmethod
    def finished_share(lines: list[str]) -> float:
        for line in reversed(lines):
            step, percent, count = STEP.findall(line), PERCENT.findall(line), COUNT.findall(line)
            if step and int(step[-1][1]):
                return min((int(step[-1][0]) - 1) / int(step[-1][1]), 1.0)
            if percent:
                return min(float(percent[-1]) / 100, 1.0)
            if count and int(count[-1][1]):
                return min(int(count[-1][0]) / int(count[-1][1]), 1.0)
        return 0.0
