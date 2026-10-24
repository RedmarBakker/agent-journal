from journal.engine.nudge import Nudge


class PlansNudges:
    """The nudges of the plans feature."""

    ALL_BLOCKED = "all its tasks left are blocked"
    PLAN_TESTING = Nudge("plans", "how_the_plan_tests", "plan {{n}} tests this way: {{testing}}", repeat_interval=0)
    BUILDER_MODE = Nudge("plans", "now_building", "you now work as the builder", repeat_interval=0)
    NEXT_PLAN_TASK = Nudge("plans", "next_task_of_the_plan", "plan {{n}}: task {{task}}, {{title}} is next. {{briefing}}", repeat_interval=0)
    PLAN_FINISHED = Nudge("plans", "plan_done", "plan {{n}} is done: its last task closed", repeat_interval=0)
    PLAN_STALLED = Nudge("plans", "plan_waits_on_its_tasks", "plan {{n}}: no task can start; {{left}} paused, blocked or waiting", "`journal plan start {{n}}` once one can go on", repeat_interval=0)
    PLAN_POSTPONED = Nudge("plans", "the_user_postponed_the_plan", "the user postponed plan {{n}}")
    PLAN_ABANDONED = Nudge("plans", "the_user_abandoned_the_plan", "the user abandoned plan {{n}}")
    PLAN_APPROVED = Nudge("plans", "the_user_approved_the_plan", "the user approved plan {{n}}", "`journal plan start {{n}}` begins its first task", repeat_interval=0)
    CHECKPOINT_PHASE_END = Nudge("plans", "phase_complete_at_a_checkpoint", "plan {{n}}: phase {{phase}} is complete, a checkpoint", "wait for the user, then `journal plan start {{n}}`", repeat_interval=0)
    PHASE_END = Nudge("plans", "phase_complete_go_on", "plan {{n}}: phase {{phase}} is complete", "`journal plan start {{n}}` begins the next phase", repeat_interval=0)
    PLAN_BLOCKED = Nudge("plans", "plan_blocked", "plan {{n}} is blocked: {{why}}", "`journal plan unblock {{n}}` opens it by hand", repeat_interval=0)
    PLAN_REOPENED = Nudge("plans", "plan_reopened", "plan {{n}} is open again: {{why}}", "`journal plan start {{n}}` goes on with it", repeat_interval=0)
    UNAPPROVED_PLAN = Nudge("plans", "plan_not_approved", "plan {{n}} is not approved", "only the user approves it", repeat_interval=0)
    APPROVED_UNSTARTED = Nudge("plans", "approved_unstarted", "plan {{n}} is approved and not started", "`journal plan start {{n}}` begins its first task", repeat_interval=0)
    REVIEW_ENTRY_REQUEST = Nudge("plans", "put_the_review_into_the_plan", "plan {{n}}'s reviewers are all back", "put their findings in as tasks, then `journal plan ready {{n}} --changed \"<what changed>\"`", repeat_interval=0)
    REVIEW_ENTRY_BLOCK = Nudge("plans", "review_write_up_waits", "your writes wait until plan {{n}} is readied", "put the reviewers' findings into it and `journal plan ready {{n}} --changed \"<what changed>\"`", repeat_interval=0)
