from journal.events.listener import Listener
from journal.events.rows.plan_started import PlanStarted
from journal.features.plans.support.plan_focus import PlanFocus
from journal.support.actor import Actor


class StartedPlanFocus(Listener[PlanStarted]):
    """A plan started or resumed by a builder or a solo agent pauses every other started plan."""

    def __init__(self, focus: PlanFocus) -> None:
        self.focus = focus

    def handle(self, event: PlanStarted) -> None:
        self.focus.pause_rest(event.plan_id, Actor.system())
