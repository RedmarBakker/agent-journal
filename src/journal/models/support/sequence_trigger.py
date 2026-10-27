import re
from dataclasses import asdict, dataclass

from journal.models.support.sequence_trigger_type import SequenceTriggerType
from journal.support.rejection import Rejection

# how a trigger is written on the command line, by its kind
LINE_FORMS = "row:<table>.<moment> | phrase:<words> | command:<pattern> | file:<glob> | file-text:<glob>:<text> | tool:<name>:<pattern>"
MOMENT = re.compile(r"^[a-z_]+\.[a-z_]+$")
KIND_VALUES = {trigger.value for trigger in SequenceTriggerType}


@dataclass(frozen=True)
class SequenceTrigger:
    """One thing that starts a sequence, by its type and the fields that type reads, read under the name kind too as a row stored before the rename has it: a row's moment such as plan.created; a phrase in the user's message, as text; a pattern on a command's line; a path glob of a file edited, with a text its new content holds; a tool's name with a pattern on its input."""

    trigger_type: SequenceTriggerType
    moment: str = ""
    text: str = ""
    pattern: str = ""
    tool: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "SequenceTrigger":
        trigger_type = data.get("trigger_type", data.get("kind"))
        if trigger_type not in KIND_VALUES:
            raise Rejection(f"a trigger has a trigger_type, one of {', '.join(sorted(KIND_VALUES))}; {trigger_type!r} is none of them")
        return cls(SequenceTriggerType(trigger_type), str(data.get("moment", "")), str(data.get("text", "")), str(data.get("pattern", "")), str(data.get("tool", "")))

    @classmethod
    def row(cls, moment: str) -> "SequenceTrigger":
        return cls(SequenceTriggerType.ROW, moment=moment)

    @classmethod
    def phrase(cls, text: str) -> "SequenceTrigger":
        return cls(SequenceTriggerType.PHRASE, text=text)

    @classmethod
    def line_trigger(cls, line: str) -> "SequenceTrigger":
        kind_text, _, value = line.partition(":")
        if kind_text not in KIND_VALUES:
            raise Rejection(f"a trigger is written {LINE_FORMS}; {line!r} does not start with a kind of trigger")
        type_name = SequenceTriggerType(kind_text)
        value_parts = [*value.split(":", 1), ""]
        kind_fields = {SequenceTriggerType.ROW: {"moment": value}, SequenceTriggerType.PHRASE: {"text": value}, SequenceTriggerType.COMMAND: {"pattern": value}, SequenceTriggerType.FILE: {"pattern": value},
                       SequenceTriggerType.FILE_TEXT: {"pattern": value_parts[0], "text": value_parts[1]}, SequenceTriggerType.TOOL: {"tool": value_parts[0], "pattern": value_parts[1]}}
        return cls(type_name, **kind_fields[type_name]).checked()

    def checked(self) -> "SequenceTrigger":
        if self.trigger_type == SequenceTriggerType.ROW and not MOMENT.match(self.moment):
            raise Rejection(f"a row trigger names a table and a moment, such as plan.created; {self.moment!r} is not one")
        if self.trigger_type in (SequenceTriggerType.PHRASE, SequenceTriggerType.FILE_TEXT) and not self.text.strip():
            raise Rejection(f"a {self.trigger_type} trigger needs a text to look for")
        if self.trigger_type in (SequenceTriggerType.FILE, SequenceTriggerType.FILE_TEXT) and not self.pattern.strip():
            raise Rejection(f"a {self.trigger_type} trigger needs the path glob of the files it watches, such as src/**/*.py")
        if self.trigger_type == SequenceTriggerType.TOOL and not self.tool.strip():
            raise Rejection("a tool trigger needs the name of the tool, such as Edit or Bash")
        if self.trigger_type in (SequenceTriggerType.COMMAND, SequenceTriggerType.TOOL):
            self.compiled_pattern()
        return self

    def compiled_pattern(self) -> re.Pattern:
        try:
            return re.compile(self.pattern)
        except re.error as fault:
            raise Rejection(f"the pattern {self.pattern!r} of a {self.trigger_type} trigger is not a regular expression: {fault}") from fault

    def line(self) -> str:
        parts = {SequenceTriggerType.ROW: (self.moment,), SequenceTriggerType.PHRASE: (self.text,), SequenceTriggerType.COMMAND: (self.pattern,), SequenceTriggerType.FILE: (self.pattern,),
                 SequenceTriggerType.FILE_TEXT: (self.pattern, self.text), SequenceTriggerType.TOOL: (self.tool, self.pattern)}[self.trigger_type]
        return ":".join((self.trigger_type.value, *parts))

    def published(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value} | {"trigger_type": self.trigger_type.value}
