from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class SkillsNudges:
    """The nudges of the skills feature."""

    SKILL_VIEWER_REQUEST = Nudge("skills", "read_the_skill_now", "read the {{name}} skill now: {{path}}", repeat=Timeout.seconds(0))

    SKILL_READ_REQUEST = Nudge("skills", "read_the_skill_first", "read {{skills|cap=400}} first", "every other tool waits until you have read them all", repeat=Timeout.seconds(0), longest_characters=474, longest_reason="it lists every skill still to read, each with its path")
    UNREAD_SKILL_STOP = Nudge("skills", "stopped_owing", "you stopped with skill {{skills|cap=400}} unread", "read it now, or run `journal stuck \"<why>\"`", repeat=Timeout.seconds(0), longest_characters=485, longest_reason="it lists every skill still to read, each with its path")

    @staticmethod
    def listed(skill_paths: list[tuple[str, str]]) -> str:
        return "; ".join(f"the {name} skill, {path}" for name, path in skill_paths)

    @classmethod
    def read_request(cls, skill_paths: list[tuple[str, str]]) -> Nudge:
        return cls.SKILL_READ_REQUEST.create(skills=cls.listed(skill_paths))
