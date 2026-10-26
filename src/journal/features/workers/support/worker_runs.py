import shlex

from journal.features.shell.support.activity_label import ActivityLabel
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.command_outputs import CommandOutputs

MERGE_LINE = "journal worker merge"


class WorkerRuns:
    """What a worker's commands are doing now, for the viewer: the labels of the runs going on in its session, such as testing or building, and the workers whose work a merge going on now takes in, by number or as one of the checked workers a merge of all takes."""

    def __init__(self, outputs: CommandOutputs) -> None:
        self.outputs = outputs

    def labels(self, workers: list[Worker]) -> dict[str | None, list[str]]:
        labels: dict[str | None, list[str]] = {}
        for output in self.outputs.session_runs([worker.session for worker in workers if worker.session is not None]):
            labels.setdefault(output.session, []).append(ActivityLabel.build(output.command))
        return labels

    def merging(self, workers: list[Worker]) -> set[int]:
        merge_arguments = {argument for output in self.outputs.prefix_runs(MERGE_LINE) for argument in shlex.split(output.command)[len(MERGE_LINE.split()):]}
        return {worker.row_id for worker in workers if str(worker.row_id) in merge_arguments or ("--all" in merge_arguments and worker.state == WorkerState.DELIVERED)}
