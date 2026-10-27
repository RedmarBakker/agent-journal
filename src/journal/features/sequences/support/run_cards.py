from journal.chat.moment_cards import MomentCards
from journal.models.entry import Entry
from journal.models.support.ref import Ref
from journal.repositories.entries import Entries
from journal.support.actor import Actor
from journal.support.card_type import CardType
from journal.support.sequence_run import SequenceRun

RUN = "sequence_run"


class RunCards:
    """A change of an agent's sequence run kept as an entry for the agent's panel, and its card in the chat, which names the run and the step it is at so the viewer gathers a run's cards in step order."""

    def __init__(self, entries: Entries, cards: MomentCards) -> None:
        self.entries, self.cards = entries, cards

    def recorded(self, environment_id: int, session: str, sequence_id: int, title: str, subject: str) -> str:
        data = {"session": session, "n": sequence_id, "title": title, "what": subject}
        self.entries.save(Entry(environment_id=environment_id, kind=RUN, actor=Actor.system(), data=data), Actor.system())
        return f"Sequence {sequence_id}, {title}: {subject}"

    def shown(self, environment_id: int, session: str, run: SequenceRun, subject: str, step: int, shows: CardType) -> None:
        label = self.recorded(environment_id, session, run.sequence_id, run.title, subject)
        self.cards.show(environment_id, session, label, row=Ref("sequences", run.sequence_id), shows=shows, fields=self.fields(run, step))

    def step_moved(self, environment_id: int, session: str, run: SequenceRun) -> None:
        self.shown(environment_id, session, run, "finished" if run.last else f"moved on to step {run.step + 2}", run.step + 1, CardType.SEQUENCES if run.last else CardType.SEQUENCE_STEPS)

    @staticmethod
    def fields(run: SequenceRun, step: int) -> dict:
        return {"run": f"{run.sequence_id}@{run.started_at}", "step": step, "run_title": f"Sequence {run.sequence_id}, {run.title}"}
