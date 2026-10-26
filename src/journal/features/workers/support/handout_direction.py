from enum import Enum


class HandoutDirection(Enum):
    """Which way a measure line pushes the agent: to hand out more work, to hand out less, or neither."""

    INCREASE = "increase"
    DECREASE = "decrease"
    NEUTRAL = "neutral"
