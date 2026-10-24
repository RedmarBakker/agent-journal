class MemoryThresholds:
    """The shares of the context window at which the agent must decide what to keep."""

    CONTEXT = (25, 50, 80)

    @classmethod
    def due(cls, context: float, highest: int) -> int:
        return max([threshold for threshold in cls.CONTEXT if context * 100 >= threshold > highest], default=0)
