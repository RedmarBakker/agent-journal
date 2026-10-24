from dataclasses import dataclass, replace

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.rows.dump_answered import DumpAnswered
from journal.events.rows.dump_arrived import DumpArrived
from journal.events.rows.dump_question import DumpQuestion
from journal.events.rows.dump_choice import DumpChoice
from journal.events.rows.dump_sorted import DumpSorted
from journal.support.permission import Permission
from journal.features.dumps.dumps_nudges import DumpsNudges
from journal.features.dumps.dumps_part import DumpsPart

USER_TEXT = -2
AGENT_HANDOVER = -1


@dataclass(frozen=True)
class SortingDump(BaseState):
    """The agent files the dump the user dropped: the stop is blocked until every item is filed or failed, except while it waits for the user's answer; what arrives on the dump, the user's answer and the user's choice of a next step are typed to it; it pops when the dump is filed, when the agent is instructed to sum it up, or when it moves on to the next dump waiting."""

    name = "sorting_dump"
    title = "Sorting a dump"
    allows = frozenset({Permission.FILE_EDITS, Permission.RUN_COMMANDS, Permission.DISPATCH_SUBAGENTS})
    dump_id: int = 0
    asking: bool = False

    def wait_description(self) -> tuple[str, str]:
        return (f"your answer on dump {self.dump_id}", f"dump:{self.dump_id}") if self.asking else ("", "")

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.none() if self.asking else self.refuse(DumpsNudges.DUMP_OPEN_REMINDER.create(n=self.dump_id))

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.none()

    def on_dump_arrived(self, event: DumpArrived, settings: Settings) -> Transition:
        event.stop_propagation()
        if event.dump_id != self.dump_id or not event.waiting:
            return self.none()
        return self.none().typing(DumpsNudges.DUMP_ARRIVAL.create(n=event.dump_id, count=item_count(event.waiting)))

    def on_dump_question(self, event: DumpQuestion, settings: Settings) -> Transition:
        return self.swap(replace(self, asking=True)) if event.dump_id == self.dump_id else self.none()

    def on_dump_answered(self, event: DumpAnswered, settings: Settings) -> Transition:
        if event.dump_id != self.dump_id:
            return self.none()
        return self.swap(replace(self, asking=False)).typing(DumpsNudges.DUMP_ANSWER.create(n=event.dump_id, answer=event.answer, question=event.question))

    def on_dump_choice(self, event: DumpChoice, settings: Settings) -> Transition:
        if event.dump_id != self.dump_id or event.choice == USER_TEXT:
            return self.none()
        if event.choice == AGENT_HANDOVER:
            return self.none().typing(DumpsNudges.DUMP_HANDOVER.create(n=event.dump_id))
        return self.none().typing(DumpsNudges.DUMP_STEP_CHOICE.create(n=event.dump_id, label=event.label))

    def on_dump_sorted(self, event: DumpSorted, settings: Settings) -> Transition:
        if event.dump_id != self.dump_id:
            return self.none()
        summed = () if event.stopped else (DumpsNudges.DUMP_SUMMARY_REQUEST.create(n=event.dump_id, outcome=event.outcome),)
        following = event.data.part(DumpsPart)
        if following.current_dump and following.current_dump != self.dump_id:
            return self.swap(replace(self, dump_id=following.current_dump, asking=False)).typing(*summed, DumpsNudges.DUMP_ARRIVAL.create(n=following.current_dump, count=item_count(following.waiting)))
        return self.pop().typing(*summed)


def item_count(count: int) -> str:
    return f"{count} item{'s' * (count != 1)}"
