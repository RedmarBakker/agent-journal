from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class TriggersNudges:
    NUDGE = Nudge("triggers", "nudge", "{{title}}")
    INSTRUCT = Nudge("triggers", "instruct", "do this now: {{title}}", repeat=Timeout.seconds(0))
    DENIED = Nudge("triggers", "denied", "a trigger denies this: {{title}}", repeat=Timeout.seconds(0))
