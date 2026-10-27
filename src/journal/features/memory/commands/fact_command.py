from journal.features.memory.commands.record_command import RecordCommand
from journal.features.memory.support.threshold_decisions import ThresholdDecisions
from journal.features.memory.support.memory_context import MemoryContext
from journal.repositories.facts import Facts


class FactCommand(RecordCommand):
    noun = "fact"

    def __init__(self, facts: Facts, decisions: ThresholdDecisions, context: MemoryContext) -> None:
        super().__init__(decisions, context)
        self.repository = facts
