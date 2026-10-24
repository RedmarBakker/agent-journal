from journal.engine.nudge import Nudge


class ChecksNudges:
    CHECK_FAILED = Nudge("checks", "check_failed", "check {{n}}, {{title}}, failed", "{{tail}}", repeat_interval=0)
    CHECK_FAILURE_REPEAT = Nudge("checks", "check_still_failing", "check {{n}}, {{title}}, is still failing", "{{tail}}", repeat_interval=0)
