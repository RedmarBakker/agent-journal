from enum import Enum


class NudgeKind(Enum):
    """What a line does to the agent: an instruction asks it to act, or holds it, and goes with the hook that raised it or is typed to an idle agent; a remark asks for nothing now and rides on the agent's next hook that can carry a line."""

    INSTRUCTION = "instruction"
    REMARK = "remark"

    def is_remark(self) -> bool:
        return self is NudgeKind.REMARK
