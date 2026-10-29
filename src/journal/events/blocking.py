from enum import Enum


class Blocking(Enum):
    """The reason written beside a listener in a feature's listeners_before_answer: its result is part of the hook's answer, or it writes a row the agent's next decision reads."""

    ANSWER = "answer"
    NEXT_DECISION = "next decision"
