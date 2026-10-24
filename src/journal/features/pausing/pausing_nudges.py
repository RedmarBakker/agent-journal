from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PausingNudges:
    PAUSED = Nudge("pausing", "paused", "the user paused you: stop here and wait", "every tool call is held until the user resumes you; say nothing more until then", repeat=Timeout.seconds(0))
    RESUMED = Nudge("pausing", "resumed", "the user resumed you: carry on where you stopped", repeat=Timeout.seconds(0))
