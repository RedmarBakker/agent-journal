from journal.engine.nudge import Nudge


class PausingNudges:
    PAUSED = Nudge("pausing", "paused", "the user paused you: stop here and wait", "every tool call is held until the user resumes you; say nothing more until then", repeat_interval=0)
    RESUMED = Nudge("pausing", "resumed", "the user resumed you: carry on where you stopped", repeat_interval=0)
