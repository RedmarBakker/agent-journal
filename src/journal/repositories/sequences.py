from journal.models.sequence import Sequence
from journal.models.support.sequence_trigger_type import SequenceTriggerType
from journal.repositories.repository import Repository
from journal.support.call_triggers import CallTriggers
from journal.support.tool_call import ToolCall

# the triggers a tool call is matched against; a row's moment and the user's phrases are matched where they happen
CALL_KINDS = [SequenceTriggerType.COMMAND.value, SequenceTriggerType.FILE.value, SequenceTriggerType.FILE_TEXT.value, SequenceTriggerType.TOOL.value]


class Sequences(Repository[Sequence]):
    model = Sequence

    def triggered_sequences(self, moment: str) -> list[Sequence]:
        return self.selected(self.query().filter_record("triggers", trigger_type=SequenceTriggerType.ROW.value, moment=moment).order("id"))

    def requested_sequences(self, text: str) -> list[Sequence]:
        return [sequence for sequence in self.selected(self.query().filter_record("triggers", trigger_type=SequenceTriggerType.PHRASE.value).order("id")) if sequence.is_requested(text)]

    def call_sequences(self) -> list[Sequence]:
        return self.selected(self.query().filter_record_listed("triggers", "trigger_type", CALL_KINDS).order("id"))

    def called_sequences(self, call: ToolCall) -> list[Sequence]:
        return [sequence for sequence in self.call_sequences() if CallTriggers.is_called(sequence, call)]

    def titled(self, title: str) -> list[Sequence]:
        return self.all_matching(title=title)
