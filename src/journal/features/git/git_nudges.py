from journal.engine.nudge import Nudge


class GitNudges:
    WORKER_TASK_REFUSAL = Nudge("git", "worker_task_refusal", "task {{task}} is worker {{worker}}'s, so the commit leaves it open", "journal worker merge {{worker}} once its proofs are checked", repeat_interval=0)
    BRANCH_CONFLICT = Nudge("git", "branch_in_use", "the branch {{branch}} is in use by the environment {{environment}}, whose agent runs on it", "work on another branch or in a worktree of its own", repeat_interval=0)
