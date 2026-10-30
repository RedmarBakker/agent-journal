from datetime import datetime, timezone

from journal.events.clock_ticked import ClockTicked
from journal.events.listener import Listener
from journal.repositories.triggers import Triggers
from journal.support.actor import Actor


class FireDueTriggers(Listener[ClockTicked]):
    """Every tick of the journal's clock, each scheduled trigger whose time has come fires once: its row moves to its next time, or ends, and the fired event carries its line to the agents."""

    def __init__(self, triggers: Triggers) -> None:
        self.triggers = triggers

    def handle(self, event: ClockTicked) -> None:
        for trigger in self.triggers.due(datetime.fromtimestamp(event.time, timezone.utc)):
            self.triggers.save(trigger.fired(event.time), Actor.system())
