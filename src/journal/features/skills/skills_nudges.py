from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class SkillsNudges:
    """The nudges of the skills feature."""

    SKILL_VIEWER_REQUEST = Nudge("skills", "read_the_skill_now", "read the {{name}} skill now: {{path}}", repeat=Timeout.seconds(0))

    SKILL_READ_REQUEST = Nudge("skills", "read_the_skill_first", "read the {{skill}} skill before anything else: {{path}}", "every other tool waits until you have", repeat=Timeout.seconds(0))
    UNREAD_SKILL_STOP = Nudge("skills", "stopped_owing", "you stopped with the {{skills}} skill still to read", "read it first, or `journal stuck \"<why>\"`", repeat=Timeout.seconds(0))
