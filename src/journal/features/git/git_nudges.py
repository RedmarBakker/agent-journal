from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class GitNudges:
    WORKER_TASK_REFUSAL = Nudge("git", "worker_task_refusal", "task {{task}} is worker {{worker}}'s and stays open", "check its proofs, then `journal worker merge {{worker}}`", repeat=Timeout.seconds(0))
    BRANCH_CONFLICT = Nudge("git", "branch_in_use", "branch {{branch}} is in use by environment {{environment}}", "work on another branch or in a worktree of its own", repeat=Timeout.seconds(0))
