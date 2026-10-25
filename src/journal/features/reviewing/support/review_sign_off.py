from journal.features.reviewing.support.point_verdict import PointVerdict
from journal.features.workers.support.merge_steps import MergeSteps
from journal.features.reviewing.support.review_report import ReviewReport
from journal.features.workers.support.worker_actions import WorkerActions
from journal.support.actor import Actor


class ReviewSignOff:
    """What a reviewer's decided report does to the work it judged, as the agent's checks would: each point passed is checked, the short ones are checked short together, which sends the worker back with the reasons, and with every point passed the work is signed off, merged as journal worker merge does, and the worker goes on to its next queued task."""

    def __init__(self, actions: WorkerActions) -> None:
        self.actions = actions

    def applied(self, worker: int, report: ReviewReport, actor: Actor) -> str:
        for point in report.judged(PointVerdict.PASSED):
            self.actions.check(worker, point.number, actor)
        shorts = report.judged(PointVerdict.SHORT)
        if shorts:
            self.actions.short_checks(worker, [(point.number, point.reason) for point in shorts], actor)
            return f"points {', '.join(str(point.number) for point in shorts)} went back to worker {worker} with your reasons"
        return self.merged(worker, actor)

    def merged(self, worker: int, actor: Actor) -> str:
        outcome = self.actions.merge(worker, actor, MergeSteps.silent())
        return "; ".join(part for part in (f"signed off: task {outcome.task.id} closed", outcome.worktree, outcome.next_task) if part)
