from dataclasses import replace
from journal.models.sequence import Sequence
from journal.events.announcer import Announcer
from journal.events.moments.trigger_fired import TriggerFired
from journal.features.sequences.support.run_tracker import RunTracker
from journal.models.trigger import Trigger
from journal.models.trigger_action import TriggerAction
from journal.repositories.sequences import Sequences
from journal.models.support.ref import Ref


class TriggerFire:
    """What matched triggers record, wherever the words appeared: a card for each, and a sequence started at its first step, whose line is returned; what is reported about the rest is the triggers conduct's."""

    def __init__(self, announcer: Announcer, runs: RunTracker, sequences: Sequences) -> None:
        self.announcer, self.runs, self.sequences = announcer, runs, sequences

    def fired(self, matched: list[Trigger], session: str, environment_id: int, user_origin: bool) -> None:
        for trigger in matched:
            self.announcer.announce(TriggerFired(environment_id=environment_id, session=session, text=trigger.text, phrases=tuple(trigger.phrases), ref=Ref.build(trigger)))
            if trigger.action == TriggerAction.SEQUENCE and user_origin:
                self.started(trigger, session, environment_id)

    def started(self, trigger: Trigger, session: str, environment_id: int) -> None:
        for sequence in self.sequences.titled(trigger.text):
            self.silent_run_start(sequence, session, environment_id)

    def silent_run_start(self, sequence: Sequence, session: str, environment_id: int) -> None:
        if self.runs.new_run(sequence, session, environment_id) is not None:
            self.runs.changed(session, environment_id, lambda run: replace(run, announced_at=""))
