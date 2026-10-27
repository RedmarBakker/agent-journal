from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PausingNudges:
    PAUSED = Nudge("pausing", "paused", "the user paused you", "stop and wait; only journal commands run until resumed. answer the user in the chat as usual", repeat=Timeout.seconds(0), chat_answerable=True)
    RESUMED = Nudge("pausing", "resumed", "the user resumed you: carry on where you stopped", repeat=Timeout.seconds(0))
