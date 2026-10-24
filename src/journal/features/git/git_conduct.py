from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.commit_detected import CommitDetected
from journal.events.agent.tool_starting import ToolStarting
from journal.features.git.support.branch_switch import BranchSwitch
from journal.features.git.support.branch_environments import BranchEnvironments
from journal.features.git.git_nudges import GitNudges
from journal.features.tasks.tasks_nudges import TasksNudges


class GitConduct(Conduct):
    """The git feature's conduct in every state: a commit whose message closed tasks is named with them, and the task open next after that close; a git checkout or switch onto a branch another running environment works on is refused, naming that environment."""

    def on_commit_detected(self, event: CommitDetected, settings: Settings) -> Transition:
        refusals = [GitNudges.WORKER_TASK_REFUSAL.create(task=item.task, worker=item.worker) for item in event.worker_tasks]
        return self.none(*refusals, *closure_lines(event))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        branch = BranchSwitch.call_target(event.call)
        environment = event.data.part(BranchEnvironments).get(branch, "") if branch else ""
        return self.refuse(GitNudges.BRANCH_CONFLICT.create(branch=branch, environment=environment)) if environment else self.none()


def closure_lines(event: CommitDetected) -> list[Nudge]:
    if not event.closed:
        return []
    closure = TasksNudges.COMMIT_CLOSURE.create(sha=event.short_sha(), tasks=event.closed_words())
    if event.next_open is None:
        return [closure]
    return [closure, TasksNudges.NEXT_TASK.create(n=event.next_open.id, title=event.next_open.title)]
