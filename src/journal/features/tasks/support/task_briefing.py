from journal.models.task import Task
from journal.repositories.proofs import Proofs
from journal.repositories.task_logs import TaskLogs

RECENT_LOG_LINES = 3


class TaskBriefing:
    """What the agent is informed about a task: its brief and its latest log lines when it starts the task, so it never works from the title alone, and the brief, every log line in order and each proof of a worker's points when it reads the task in full."""

    def __init__(self, logs: TaskLogs, proofs: Proofs) -> None:
        self.logs, self.proofs = logs, proofs

    def lines(self, task: Task) -> list[str]:
        logged = [log.line for log in self.logs.logs(task)][-RECENT_LOG_LINES:]
        return ([f"brief: {task.brief}"] if task.brief else []) + [f"logged: {line}" for line in logged]

    def whole(self, task: Task) -> str:
        logged = sorted(self.logs.logs(task), key=lambda log: log.row_id)
        entries = "\n".join(f"  {log.created_at:%Y-%m-%d %H:%M}  {log.line}" for log in logged)
        return f"brief: {task.brief or 'none'}\n" + (f"log ({len(logged)} lines):\n{entries}" if logged else "log: none") + self.proof_lines(task)

    def proof_lines(self, task: Task) -> str:
        proofs = sorted(self.proofs.task_proofs(task), key=lambda proof: (proof.point, proof.row_id))
        return "".join(f"\nproof of point {proof.point} ({proof.state}): {proof.text}" + (f"\n  short: {proof.shortfall}" if proof.shortfall else "") for proof in proofs)

    def text(self, task: Task) -> str:
        return "; ".join(self.lines(task))
