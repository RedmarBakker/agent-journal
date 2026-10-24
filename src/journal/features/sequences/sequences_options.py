from journal.support.option import Option


class SequencesOptions:
    """The options of the sequences feature."""

    STALENESS_LIMIT = Option("sequences.stale_after", "Hold writes again after", "Writes since a step was taken up before the next write waits for the step to be moved on, followed again or paused", 25)
    STEP_REPEAT_INTERVAL = Option("sequences.say_every", "Say the step again after", "Minutes a step stands unheard before it is said again to a quiet agent; three times as long while the agent waits", 10, unit="minutes")
