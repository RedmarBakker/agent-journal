from journal.features.workers.support.merged_work import MergedWork
from journal.features.workers.support.worker_reports import WorkerReports
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks

# the most of the diff a verifier of a model's fit is handed, so its brief stays one read
DIFF_CHARS = 8000
EDIT_CHARS = 1200
MODEL_VERDICTS = ("too-strong", "right", "too-weak")


class ModelFitEvidence:
    """The brief a verifier of a worker's model is handed: the task's brief, the diff the worker's edits make as its records keep them, its report, the model it ran on and how complex the journal measured the work, with the one answer it gives."""

    def __init__(self, work: MergedWork, tasks: Tasks, reports: WorkerReports) -> None:
        self.work, self.tasks, self.reports = work, tasks, reports

    def brief(self, worker: Worker) -> str:
        complexity = self.work.complexity(worker)
        return "\n\n".join((
            "You are a verifier the journal sent. A worker's work below was merged. Judge, on this evidence alone, whether the model it ran on fit the work: "
            "too-strong when a cheaper model would have done it as well, right when it fit, too-weak when it needed a stronger one. Answer with one command and nothing else: "
            "journal verdict model too-strong|right|too-weak \"<one line of reason>\". Every other tool is refused, and your verdict ends your session.",
            f"## The model\n\n{worker.model or 'not named'}, on {worker.provider}",
            f"## How complex the journal measured it\n\n{complexity.lines} lines in {complexity.files} files, {complexity.tests_added} test files, sent back {complexity.send_backs} times, "
            f"{complexity.tool_uses} tool uses over {complexity.minutes:g} minutes; {complexity.points()} points, which call for the {complexity.called_for().value} model",
            f"## The task's brief\n\n{self.task_brief(worker)}",
            f"## The diff\n\n{self.diff(worker)}",
            f"## The worker's report\n\n{self.reports.last(worker) or '(no report)'}",
        ))

    def task_brief(self, worker: Worker) -> str:
        return self.tasks.find(worker.merged_task).brief if worker.merged_task else worker.brief

    def diff(self, worker: Worker) -> str:
        edits = self.work.job_edits(worker)
        parts = [f"### {edit.path} (+{edit.added} -{edit.removed})\n" + "\n".join(f"- {line}" for line in edit.old_text[:EDIT_CHARS].splitlines()) + "\n" + "\n".join(f"+ {line}" for line in edit.new_text[:EDIT_CHARS].splitlines()) for edit in edits]
        text = "\n\n".join(parts)
        return text[:DIFF_CHARS] + ("\n\n(the diff goes on)" if len(text) > DIFF_CHARS else "") if text else "(no edits are kept for this work)"
