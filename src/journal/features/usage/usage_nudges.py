from journal.engine.nudge import Nudge


class UsageNudges:
    LIMIT_CHECK = Nudge("usage", "limit_check", "checking whether the usage limit is over", "if it is, carry on with the work in hand", repeat_interval=0)
