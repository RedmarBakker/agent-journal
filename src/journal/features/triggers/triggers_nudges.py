from journal.engine.nudge import Nudge


class TriggersNudges:
    NUDGE = Nudge("triggers", "nudge", "{{title}}")
    INSTRUCT = Nudge("triggers", "instruct", "do this now: {{title}}", repeat_interval=0)
    DENIED = Nudge("triggers", "denied", "a trigger denies this: {{title}}", repeat_interval=0)
