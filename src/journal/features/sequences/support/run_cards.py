from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.support.actor import Actor
from journal.support.run_place import RunPlace
from journal.support.sequence_run import SequenceRun

RUN = "sequence_run"


class RunCards:
    """A change of an agent's sequence run kept as an entry for the agent's panel, the words of its card in the chat, and the card's place in its run."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def recorded(self, environment_id: int, session: str, sequence_id: int, title: str, subject: str) -> str:
        data = {"session": session, "n": sequence_id, "title": title, "what": subject}
        self.entries.save(Entry(environment_id=environment_id, kind=RUN, actor=Actor.system(), data=data), Actor.system())
        return f"Sequence {sequence_id}, {title}: {subject}"

    def step_moved(self, environment_id: int, session: str, run: SequenceRun) -> str:
        return self.recorded(environment_id, session, run.sequence_id, run.title, "finished" if run.last else f"moved on to step {run.step + 2}")

    @staticmethod
    def place(run: SequenceRun, step: int) -> RunPlace:
        return RunPlace(f"{run.sequence_id}@{run.started_at}", step, f"Sequence {run.sequence_id}, {run.title}")
