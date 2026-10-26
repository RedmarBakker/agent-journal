import re
from fnmatch import fnmatch

from journal.models.sequence import Sequence
from journal.models.support.sequence_trigger import SequenceTrigger
from journal.models.support.sequence_trigger_type import SequenceTriggerType
from journal.support.tool_call import ToolCall


class CallTriggers:
    """Whether a tool call is what a sequence's trigger waits for: a shell line its pattern finds, a file edited that its glob matches, with its text in the new content for a file-text trigger, or the tool it names with its pattern in the input."""

    @classmethod
    def is_called(cls, sequence: Sequence, call: ToolCall) -> bool:
        return any(cls.matches(trigger, call) for trigger in sequence.triggers)

    @classmethod
    def matches(cls, trigger: SequenceTrigger, call: ToolCall) -> bool:
        checks = {
            SequenceTriggerType.COMMAND: lambda: bool(call.command) and re.search(trigger.pattern, call.command) is not None,
            SequenceTriggerType.FILE: lambda: cls.is_file_edit(call, trigger.pattern),
            SequenceTriggerType.FILE_TEXT: lambda: cls.is_file_edit(call, trigger.pattern) and trigger.text in call.input_text,
            SequenceTriggerType.TOOL: lambda: call.tool == trigger.tool and re.search(trigger.pattern, call.input_text) is not None,
        }
        return trigger.kind in checks and checks[trigger.kind]()

    @staticmethod
    def is_file_edit(call: ToolCall, path_glob: str) -> bool:
        return call.writes and any(fnmatch(edited_path, path_glob) or fnmatch(edited_path, f"*/{path_glob}") for edited_path in call.edited_paths)
