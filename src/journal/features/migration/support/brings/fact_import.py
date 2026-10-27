from pathlib import Path

from journal.features.migration.support.environment_table_import import EnvironmentTableImport
from journal.features.migration.support.version_3_row import Version3Row
from journal.support.actor import Actor
from journal.models.environment import Environment
from journal.models.memory import Memory
from journal.repositories.environments import Environments
from journal.repositories.memories import Memories
from journal.repositories.migrated_rows import MigratedRows


class FactImport(EnvironmentTableImport):
    """A version 3 fact becomes a memory of weight 5 with its text and keywords; a struck one stays behind."""

    row_type = "fact"
    title = "facts"

    def __init__(self, environments: Environments, tally: MigratedRows, memories: Memories) -> None:
        super().__init__(environments, tally)
        self.memories = memories

    def skipped(self, row: Version3Row, target: Environment) -> str:
        return super().skipped(row, target) or ("struck" if row.completed else "")

    def created(self, row: Version3Row, target: Environment, attached: Path, actor: Actor) -> Memory:
        return self.memories.imported(Memory(environment_id=target.row_id, text=row.brief or row.title, keywords=tuple(row.listed("keywords"))), row.creation_moment(), actor)
