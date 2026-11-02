from dataclasses import dataclass, field
from typing import ClassVar

from journal.models.scoped import Scoped


@dataclass(frozen=True)
class SupervisorFeedback(Scoped):
    """One owner's feedback on a supervisor decision."""

    text_fields: ClassVar[tuple[str, ...]] = ("comment",)
    VERDICTS: ClassVar[tuple[str, ...]] = ("Useful", "Not useful")
    CORRECTIONS: ClassVar[tuple[str, ...]] = (
        "Should have done nothing",
        "Should have handed it to me",
        "Should have proposed instead",
        "Should have done something else",
    )
    SCENARIO_FIELDS: ClassVar[frozenset[str]] = frozenset({"plan", "area", "verb", "wake_event"})

    verdict: str = ""
    comment: str = ""
    correction: str = ""
    scenario: dict = field(default_factory=dict)

    def refusal(self) -> str:
        if self.verdict not in self.VERDICTS:
            return "the supervisor feedback verdict must be Useful or Not useful"
        if not isinstance(self.comment, str) or len(self.comment) > 1000:
            return "the supervisor feedback comment must be at most 1,000 characters"
        if self.correction not in self.CORRECTIONS:
            return "the supervisor feedback correction must be one of the documented choices"
        if not self._valid_scenario():
            return "the supervisor feedback scenario must name a plan, area, verb and wake-up"
        return ""

    def _valid_scenario(self) -> bool:
        return (
            isinstance(self.scenario, dict)
            and set(self.scenario) == self.SCENARIO_FIELDS
            and type(self.scenario["plan"]) is int
            and self.scenario["plan"] > 0
            and all(
                isinstance(self.scenario[name], str) and bool(self.scenario[name].strip())
                for name in ("area", "verb", "wake_event")
            )
        )
