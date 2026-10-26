from journal.features.migration.support.builtin_kind import BuiltinKind
from journal.features.migration.support.version_3_row import Version3Row
from journal.support.actor import Actor
from journal.models.trigger import Trigger
from journal.models.trigger_action import TriggerAction
from journal.repositories.migrated_rows import MigratedRows
from journal.repositories.triggers import Triggers

ACTIONS = {"nudge": TriggerAction.NUDGE, "instruct": TriggerAction.INSTRUCT, "deny": TriggerAction.DENY}
# a version 3 trigger that started a sequence; version 4 keeps those words on the sequence itself
SEQUENCE_START = "start"


class TriggerImport(BuiltinKind):
    """A trigger of the project's keeps its words, what it does and its text, where version 4 can do the same."""

    kind = "trigger"
    title = "triggers"

    def __init__(self, tally: MigratedRows, triggers: Triggers) -> None:
        super().__init__(tally)
        self.triggers = triggers

    def skipped(self, row: Version3Row) -> str:
        return super().skipped(row) or self.unsupported(row.data.get("does", ""))

    @staticmethod
    def unsupported(action: str) -> str:
        if action == SEQUENCE_START:
            return "version 4 keeps the words that start a sequence on the sequence: add them with journal sequence edit <n> --trigger phrase:'<words>'"
        return "" if action in ACTIONS else f"version 4 has no trigger that does {action}"

    def created(self, row: Version3Row, actor: Actor) -> Trigger:
        return self.triggers.imported(Trigger(phrases=tuple(row.listed("words")), action=ACTIONS[row.data["does"]], text=row.data.get("text", "")), row.creation_moment(), actor)
