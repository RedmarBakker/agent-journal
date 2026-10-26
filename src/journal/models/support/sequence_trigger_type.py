from enum import StrEnum


class SequenceTriggerType(StrEnum):
    """What starts a sequence: a row's moment, a phrase in the user's message, a command run, a file edited, a file edited whose new text holds a text, or a tool used."""

    ROW = "row"
    PHRASE = "phrase"
    COMMAND = "command"
    FILE = "file"
    FILE_TEXT = "file-text"
    TOOL = "tool"
