from dataclasses import replace

from journal.features.builtin_rows import BuiltinRows
from journal.features.seed import Seed
from journal.features.sequences.shipped import SHIPPED
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
        builtin = BuiltinRows(tuple(self.sequences.rows()), frozenset(sequence.title for sequence in SHIPPED))
        for leftover in builtin.leftovers():
            self.sequences.delete(leftover, Actor.system())
        for sequence in SHIPPED:
            data = builtin.standing(sequence.title)
            if data is None:
                self.sequences.save(replace(sequence, locked=True), Actor.system())
            elif (data.steps, data.end_condition, data.triggers, data.locked) != (sequence.steps, sequence.end_condition, sequence.triggers, True):
                self.sequences.save(replace(data, steps=sequence.steps, end_condition=sequence.end_condition, triggers=sequence.triggers, locked=True), Actor.system())
