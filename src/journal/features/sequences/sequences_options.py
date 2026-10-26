from journal.support.option import Option


class SequencesOptions:
    """The options of the sequences feature."""

    STEP_REPEAT_INTERVAL = Option("sequences.say_every", "Say the step again after", "Minutes a step stands unheard before it is said again to a quiet agent; three times as long while the agent waits", 10, unit="minutes")
