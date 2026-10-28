from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PlansNudges:
    """The nudges of the plans feature."""

    ALL_BLOCKED = "all its tasks left are blocked"
    PLAN_TESTING_CHANGED = Nudge("plans", "the_plan_tests_another_way", "plan {{n}} now tests this way ({{template}}): {{testing|cap=600}}", repeat=Timeout.seconds(0), longest_characters=660, longest_reason="it contains the testing instructions the user wrote")
    TEST_COMMANDS_NEEDED = Nudge("plans", "name_the_test_commands", "the plan waits for test commands: `journal settings set plans.test_commands \"<line>, <line>\"`; reads go through", "", repeat=Timeout.seconds(0))
    MID_PHASE_TESTS = Nudge("plans", "tests_wait_for_the_phase_end", "plan {{n}} tests at phase ends and phase {{phase}} is open: write the tests now, run them at its end", "to run one now for a reason: `journal plan allow-tests {{n}} --why \"<reason>\"`", repeat=Timeout.seconds(0), longest_characters=170, longest_reason="it names the plan, its phase and the command that lets one test run through")
    PLAN_TESTING = Nudge("plans", "how_the_plan_tests", "plan {{n}} tests this way: {{testing}}", repeat=Timeout.seconds(0))
    BUILDER_MODE = Nudge("plans", "now_building", "you are now the builder", repeat=Timeout.seconds(0))
    NEXT_PLAN_TASK = Nudge("plans", "next_task_of_the_plan", "plan {{n}}: task {{task}} is next. {{briefing|cap=1500}}", repeat=Timeout.seconds(0), longest_characters=1540, longest_reason="it contains the brief of the next task")
    PLAN_FINISHED = Nudge("plans", "plan_done", "plan {{n}} done", "run the final suite; merging to main and releasing wait for the user's word", repeat=Timeout.seconds(0))
    PLAN_STALLED = Nudge("plans", "plan_waits_on_its_tasks", "plan {{n}}: no task can start; {{left}} paused, blocked or waiting", "`journal plan start {{n}}` once one can go on", repeat=Timeout.seconds(0))
    PLAN_POSTPONED = Nudge("plans", "the_user_postponed_the_plan", "the user postponed plan {{n}}")
    PLAN_ABANDONED = Nudge("plans", "the_user_abandoned_the_plan", "the user abandoned plan {{n}}")
    PLAN_APPROVED = Nudge("plans", "the_user_approved_the_plan", "plan {{n}} approved", repeat=Timeout.seconds(0))
    PLAN_APPROVED_WITH_COMMENT = Nudge("plans", "the_user_approved_the_plan_with_a_comment", "plan {{n}} approved with a comment: read message {{comment}} before you start", repeat=Timeout.seconds(0))
    CHECKPOINT_PHASE_END = Nudge("plans", "phase_complete_at_a_checkpoint", "plan {{n}}: phase {{phase}} done, a checkpoint", "wait for the user, then `journal plan start {{n}}`", repeat=Timeout.seconds(0))
    PHASE_END_TESTS = Nudge("plans", "phase_complete_run_its_tests", "plan {{n}}: phase {{phase}} done", "run {{commands|cap=300}} and see each pass, then `journal plan start {{n}}`", repeat=Timeout.seconds(0), longest_characters=392, longest_reason="it contains the test commands the agent runs")
    PHASE_END = Nudge("plans", "phase_complete_go_on", "plan {{n}}: phase {{phase}} done", "start the next with `journal plan start {{n}}`", repeat=Timeout.seconds(0))
    PLAN_BLOCKED = Nudge("plans", "plan_blocked", "plan {{n}} is blocked: {{why|cap=44}}", "unblock it by hand with `journal plan unblock {{n}}`", repeat=Timeout.seconds(0))
    DRIVE_ENDED = Nudge("plans", "drive_ended", "{{name|cap=17}}: no longer driven ({{why|cap=19}}); writes refused", "retake: `journal {{noun}} drive {{n}}`", repeat=Timeout.seconds(0))
    PLAN_RETURN_QUESTION = Nudge("plans", "return_to_the_paused_plan", "plan {{n}} paused, task {{task}} in hand: back to the plan after it?", "`journal plan return {{n}} yes` or `no`", repeat=Timeout.seconds(0))
    PLAN_REOPENED = Nudge("plans", "plan_reopened", "plan {{n}} is open again: {{why|cap=53}}", "continue with `journal plan start {{n}}`", repeat=Timeout.seconds(0))
    UNAPPROVED_PLAN = Nudge("plans", "plan_not_approved", "plan {{n}} is not approved", "only the user approves it", repeat=Timeout.seconds(0))
    REVIEW_ENTRY_REQUEST = Nudge("plans", "put_the_review_into_the_plan", "plan {{n}}: all reviewers are back{{reports|cap=53}}. put their findings into the plan", repeat=Timeout.seconds(0))

    @staticmethod
    def unread(reports: tuple[int, ...]) -> str:
        return f"; unread: reports {', '.join(map(str, reports))}" if reports else ""
