import re

from journal.support.tool_call import ToolCall

# words that say a task waits on something, written instead of a block the journal can see
WAIT_WORDS = re.compile(r"\b(wait(s|ing)?\s+(for|on|until)|blocked\s+(on|by|until))\b", re.IGNORECASE)
# a block with a wait the journal opens by itself
BLOCK_FLAGS = ("--on", "--until")
# the journal commands whose words are a log line or a reply
WORDED_COMMANDS = (("task", "log"), ("message", "send"))


class WrittenWait:
    """A wait written in words, in a log line, a message or a reply, rather than as a block with --on or --until."""

    @staticmethod
    def is_written(text: str) -> bool:
        return bool(WAIT_WORDS.search(text)) and not any(flag in text for flag in BLOCK_FLAGS)

    @staticmethod
    def worded(call: ToolCall) -> str:
        return " ".join(part.text for part in call.parts if tuple(part.text.split()[1:3]) in WORDED_COMMANDS and part.is_journal)
