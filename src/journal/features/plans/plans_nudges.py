from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PlansNudges:
    """The nudges of the plans feature."""

    ALL_BLOCKED = "all its tasks left are blocked"
    PLAN_TESTING = Nudge("plans", "how_the_plan_tests", "plan {{n}} tests this way: {{testing}}", repeat=Timeout.seconds(0))
    BUILDER_MODE = Nudge("plans", "now_building", "you now work as the builder", repeat=Timeout.seconds(0))
    NEXT_PLAN_TASK = Nudge("plans", "next_task_of_the_plan", "plan {{n}}: task {{task}} is next. {{briefing}}", repeat=Timeout.seconds(0))
    PLAN_FINISHED = Nudge("plans", "plan_done", "plan {{n}} done", "run the final suite; merging to main and releasing wait for the user's word", repeat=Timeout.seconds(0))
    PLAN_STALLED = Nudge("plans", "plan_waits_on_its_tasks", "plan {{n}}: no task can start; {{left}} paused, blocked or waiting", "`journal plan start {{n}}` once one can go on", repeat=Timeout.seconds(0))
    PLAN_POSTPONED = Nudge("plans", "the_user_postponed_the_plan", "the user postponed plan {{n}}")
    PLAN_ABANDONED = Nudge("plans", "the_user_abandoned_the_plan", "the user abandoned plan {{n}}")
    PLAN_APPROVED = Nudge("plans", "the_user_approved_the_plan", "plan {{n}} approved", repeat=Timeout.seconds(0))
    CHECKPOINT_PHASE_END = Nudge("plans", "phase_complete_at_a_checkpoint", "plan {{n}}: phase {{phase}} is complete, a checkpoint", "wait for the user, then `journal plan start {{n}}`", repeat=Timeout.seconds(0))
    PHASE_END_TESTS = Nudge("plans", "phase_complete_run_its_tests", "plan {{n}}: phase {{phase}} is complete, and its testing template runs {{commands}}", "run each and see it pass, then `journal plan start {{n}}` begins the next phase", repeat=Timeout.seconds(0))
    PHASE_END = Nudge("plans", "phase_complete_go_on", "plan {{n}}: phase {{phase}} is complete", "`journal plan start {{n}}` begins the next phase", repeat=Timeout.seconds(0))
    PLAN_BLOCKED = Nudge("plans", "plan_blocked", "plan {{n}} is blocked: {{why}}", "`journal plan unblock {{n}}` opens it by hand", repeat=Timeout.seconds(0))
    PLAN_REOPENED = Nudge("plans", "plan_reopened", "plan {{n}} is open again: {{why}}", "`journal plan start {{n}}` goes on with it", repeat=Timeout.seconds(0))
    UNAPPROVED_PLAN = Nudge("plans", "plan_not_approved", "plan {{n}} is not approved", "only the user approves it", repeat=Timeout.seconds(0))
    APPROVED_UNSTARTED = Nudge("plans", "approved_unstarted", "plan {{n}} is approved and not started", "`journal plan start {{n}}` begins its first task", repeat=Timeout.seconds(0))
    REVIEW_ENTRY_REQUEST = Nudge("plans", "put_the_review_into_the_plan", "plan {{n}}'s reviewers are all back{{reports}}", "put their findings in as tasks, then `journal plan ready {{n}} --changed \"<what changed>\"`", repeat=Timeout.seconds(0))
    REVIEW_COUNTDOWN = Nudge("plans", "writes_held_soon_until_the_review_is_in", "plan {{n}} readied due: {{count}}{{reports}}", repeat=Timeout.seconds(0))
    REVIEW_LAST_USE = Nudge("plans", "next_write_held_until_the_review_is_in", "plan {{n}} readied due: 0{{reports}}", "your next write waits until it is readied", repeat=Timeout.seconds(0))
    REVIEW_ENTRY_BLOCK = Nudge("plans", "review_write_up_waits", "your writes wait until plan {{n}} is readied", "put the reviewers' findings into it and `journal plan ready {{n}} --changed \"<what changed>\"`", repeat=Timeout.seconds(0))

    @staticmethod
    def unread(reports: tuple[int, ...]) -> str:
        return f"; unread: reports {', '.join(map(str, reports))}" if reports else ""

    @classmethod
    def review_countdown(cls, plan: int, remaining_uses: int, reports: tuple[int, ...] = ()) -> Nudge:
        named = cls.unread(reports)
        return cls.REVIEW_COUNTDOWN.create(n=plan, count=remaining_uses, reports=named) if remaining_uses else cls.REVIEW_LAST_USE.create(n=plan, reports=named)
