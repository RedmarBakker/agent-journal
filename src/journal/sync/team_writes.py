from journal.events.bus import Bus
from journal.events.models.model_event import ModelEvent
from journal.events.models.number_request import NumberRequest
from journal.sync.block_numbers import BlockNumbers
from journal.sync.record_outgoing_change import RecordOutgoingChange


class TeamWrites:
    """What every process that writes this journal's rows hears for its team, the server and a command run with no server alike: a new shared row numbered from this machine's blocks, and every write to a shared row queued for the team server."""

    def __init__(self, bus: Bus, numbers: BlockNumbers, outgoing: RecordOutgoingChange) -> None:
        self.bus, self.numbers, self.outgoing = bus, numbers, outgoing

    def listen(self) -> None:
        self.bus.listen(ModelEvent, self.outgoing)
        self.bus.listen(NumberRequest, self.numbers)
