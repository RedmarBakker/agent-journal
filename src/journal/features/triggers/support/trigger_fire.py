from journal.events.announcer import Announcer
from journal.events.moments.trigger_fired import TriggerFired
from journal.models.trigger import Trigger
from journal.models.support.ref import Ref


class TriggerFire:
    """What matched triggers record, wherever the words appeared: a card for each; what is reported about them is the triggers conduct's."""

    def __init__(self, announcer: Announcer) -> None:
        self.announcer = announcer

    def fired(self, matched: list[Trigger], session: str, environment_id: int) -> None:
        for trigger in matched:
            self.announcer.announce(TriggerFired(environment_id=environment_id, session=session, text=trigger.text, phrases=tuple(trigger.phrases), ref=Ref.build(trigger)))
