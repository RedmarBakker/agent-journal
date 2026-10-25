from journal.engine.nudge import Nudge
from journal.support.rejection import Rejection


def refused(n: int) -> None:
    # @sin PlainJournalTextDetector
    raise Rejection(f"worker {n} holds no task: a worker clocks out of the task it was sent on")


def refused_plainly(n: int) -> None:
    # @righteous PlainJournalTextDetector
    raise Rejection(f"worker {n} has no task: a worker clocks out of the task it was sent on")


# @sin PlainJournalTextDetector
LINE = Nudge("tasks", "next_task", "the next task is named once you are told the plan")
# @righteous PlainJournalTextDetector
PLAIN_LINE = Nudge("tasks", "next_task", "the next task is shown once the plan is started")
