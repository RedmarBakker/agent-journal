from journal.engine.nudge import Nudge


class SkillsNudges:
    """The nudges of the skills feature."""

    SKILL_READ_REQUEST = Nudge("skills", "read_the_skill_first", "read the {{skill}} skill before anything else: {{path}}", "every other tool waits until you have", repeat_interval=0)
    UNREAD_SKILL_STOP = Nudge("skills", "stopped_owing", "you stopped with the {{skills}} skill still to read", "read it first, or `journal stuck \"<why>\"`", repeat_interval=0)
