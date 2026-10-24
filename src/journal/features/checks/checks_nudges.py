from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ChecksNudges:
    CHECK_FAILED = Nudge("checks", "check_failed", "check {{n}}, {{title}}, failed", "{{tail}}", repeat=Timeout.seconds(0))
    CHECK_FAILURE_REPEAT = Nudge("checks", "check_still_failing", "check {{n}}, {{title}}, is still failing", "{{tail}}", repeat=Timeout.seconds(0))
