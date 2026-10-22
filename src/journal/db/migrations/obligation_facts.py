from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ObligationFacts:
    """What an agent had to do for the journal, as the facts on its row that replace the old pauses: not oriented, the mark to decide, the skills to read."""

    has_overview: bool = True
    threshold_due: int = 0
    skills: tuple[str, ...] = ()

    def obligation(self, state: str, threshold: int, skill: str) -> "ObligationFacts":
        if state == "orienting":
            return replace(self, has_overview=False)
        if state == "at_mark":
            return replace(self, threshold_due=max(self.threshold_due, threshold))
        if state == "loading_skill" and skill:
            return replace(self, skills=(*self.skills, skill))
        return self
