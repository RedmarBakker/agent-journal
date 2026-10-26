from datetime import datetime, timezone

from journal.engine.job import Job
from journal.features.shell.support.watched_run_judge import WatchedRunJudge
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class WatchedRunCheck(Job):
    """Every ten seconds each watched run still going is judged on what its reader shows of the output it prints now."""

    interval_seconds = 10.0

    def __init__(self, outputs: CommandOutputs, judge: WatchedRunJudge, scope: Scope) -> None:
        self.outputs, self.judge, self.scope = outputs, judge, scope

    def tick(self, time: float) -> None:
        for output in self.outputs.running_watched():
            with self.scope.environment(output.environment_id):
                self.judge.judged(output, datetime.fromtimestamp(time, timezone.utc))
