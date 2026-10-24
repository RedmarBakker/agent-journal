from dataclasses import dataclass

from journal.engine.demand import Demand
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.events.agent.tool_starting import ToolStarting
from journal.support.moment import Moment


@dataclass(frozen=True)
class DemandProgress:
    """A demand as an agent stands with it: its requirement now, none once it is met, the moment it started and the moment of the tool use in hand, its span measured between the two."""

    demand: Demand
    requirement: object | None = None
    start: Moment = Moment()
    moment: Moment = Moment()

    def is_active(self) -> bool:
        return self.requirement is not None

    def is_expired(self, settings: Settings) -> bool:
        return self.is_active() and self.demand.span(settings).reset(self.start).has_passed(self.moment)

    def balance(self, settings: Settings) -> int:
        span = self.demand.span(settings)
        return int(span.amount - (self.moment.value(span.unit) - self.start.value(span.unit))) - 1

    def has_announcement(self, settings: Settings) -> bool:
        return not self.is_expired(settings) and (self.demand.silence is None or self.demand.silence(settings).reset(self.start).has_passed(self.moment))

    def exempts(self, event: ToolStarting) -> bool:
        return event.subagent or self.demand.exemption(event, self.requirement)

    def blocks(self, event: ToolStarting) -> bool:
        return not self.exempts(event) and self.demand.block_scope(event)

    def line(self, settings: Settings) -> Nudge:
        return self.demand.line(self.requirement, self.balance(settings))

    def refusal(self) -> Nudge:
        return self.demand.refusal(self.requirement)
