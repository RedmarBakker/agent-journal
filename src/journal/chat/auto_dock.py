from journal.chat.process_cards import AUTO_DOCKED, DOCK_TIME_KEY, DOCKED, UNDOCK_TIME_KEY
from journal.models.message import Message
from journal.support.time_source import TimeSource

ENDED_DOCK_SECONDS = 5
DOCK_DELAY_SECONDS = 5


class AutoDock:
    """When a card the journal docks by itself comes and goes: docked once its run has gone on five seconds, so a quick run never docks, and taken down five seconds after its run ends, unless the user opened it."""

    def __init__(self, time_source: TimeSource) -> None:
        self.time_source = time_source

    @staticmethod
    def dock_fields(start_seconds: float) -> dict:
        return {DOCKED: True, AUTO_DOCKED: True, DOCK_TIME_KEY: start_seconds + DOCK_DELAY_SECONDS}

    def undock_fields(self, card: Message) -> dict:
        if not card.data.get(AUTO_DOCKED):
            return {}
        return {UNDOCK_TIME_KEY: card.data.get(UNDOCK_TIME_KEY) or self.undock_time(card.data.get(DOCK_TIME_KEY, 0))}

    def undock_time(self, dock_time: float) -> float:
        current_time = self.time_source.seconds()
        return dock_time if current_time < dock_time else current_time + ENDED_DOCK_SECONDS
