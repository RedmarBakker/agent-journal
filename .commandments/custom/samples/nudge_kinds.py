from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind


class SampleNudges:
    # @sin NudgeRemarkFlagDetector
    FLAGGED = Nudge("sample", "flagged", "no em dashes in the chat", is_remark=True)

    # @righteous NudgeRemarkFlagDetector
    DECLARED = Nudge("sample", "declared", "no em dashes in the chat", kind=NudgeKind.REMARK)

    # @righteous NudgeRemarkFlagDetector
    INSTRUCTION = Nudge("sample", "instruction", "carry on with the task")
