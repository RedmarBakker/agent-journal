from journal.features.migration.support.builtin_type import BuiltinType
from journal.features.migration.support.version_3_row import Version3Row
from journal.support.actor import Actor
from journal.models.sequence import Sequence
from journal.models.support.sequence_trigger import SequenceTrigger
from journal.models.support.sequence_step import SequenceStep
from journal.repositories.migrated_rows import MigratedRows
from journal.repositories.sequences import Sequences


class SequenceImport(BuiltinType):
    """A sequence of the project's keeps its title, its steps in order and when it starts."""

    kind = "sequence"
    title = "sequences"

    def __init__(self, tally: MigratedRows, sequences: Sequences) -> None:
        super().__init__(tally)
        self.sequences = sequences

    def created(self, row: Version3Row, actor: Actor) -> Sequence:
        steps = tuple(SequenceStep(title=title, instructions=body or title) for title, body in row.sections)
        return self.sequences.imported(Sequence(title=row.title, steps=steps, triggers=tuple(SequenceTrigger.row(moment) for moment in (row.data.get("starts_on", ""),) if moment)), row.creation_moment(), actor)
