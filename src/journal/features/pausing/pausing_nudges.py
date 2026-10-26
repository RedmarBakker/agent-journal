from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PausingNudges:
    PAUSED = Nudge("pausing", "paused", "the user paused you: stop your work here and wait", "until the user resumes you every tool call is held but journal commands; answer the user in the chat as ever", repeat=Timeout.seconds(0), chat_answerable=True)
    RESUMED = Nudge("pausing", "resumed", "the user resumed you: carry on where you stopped", repeat=Timeout.seconds(0))
