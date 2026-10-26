from dataclasses import replace

from journal.features.seed import Seed
from journal.features.sequences.shipped import RETIRED, SHIPPED
from journal.support.actor import Actor
from journal.repositories.sequences import Sequences
from journal.sync.team_account import TeamAccount


class BuiltinSequences(Seed):
    """The shipped sequences, written by title, locked, and kept as the journal ships them, their triggers among them; in a team only by the machine that holds the team's upgrade, so no two machines write the same one."""

    def __init__(self, sequences: Sequences, account: TeamAccount) -> None:
        self.sequences, self.account = sequences, account

    def run(self) -> None:
        if not self.account.is_seed_writer():
            return
        present = {sequence.title: sequence for sequence in self.sequences.all()}
        for sequence in SHIPPED:
            data = present.get(sequence.title)
            if data is None:
                self.sequences.save(replace(sequence, locked=True), Actor.system())
            elif (data.steps, data.end_condition, data.triggers, data.locked) != (sequence.steps, sequence.end_condition, sequence.triggers, True):
                self.sequences.save(replace(data, steps=sequence.steps, end_condition=sequence.end_condition, triggers=sequence.triggers, locked=True), Actor.system())
        for title in RETIRED:
            data = present.get(title)
            if data is not None and data.updater == Actor.system():
                self.sequences.delete(data, Actor.system())
