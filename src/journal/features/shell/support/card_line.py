import re

from journal.chat.card_detail import DETAIL_CHARACTERS

CODE_SYMBOLS = re.compile(r"[{}\[\]();=\"]")
CODE_SYMBOL_COUNT = 8
CARD_LINE_CHARACTERS = DETAIL_CHARACTERS
FRAME = re.compile(r"^[=\-*#_~ ]{3,}|[=\-*#_~ ]{3,}$")
# a failed or errored test named by its id, the line a person reads first however long the test's name
FAILED_TEST = re.compile(r"^(FAILED|ERROR) \S+::\S+")


class CardLine:
    """A line a reader picks as the card shows it, its frame of = or - signs taken off, as pytest draws round its summary; and whether it reads as a status for the user: neither code nor data, and short enough for the card's line, never cut to fit."""

    @staticmethod
    def plain(text: str) -> str:
        return FRAME.sub("", text).strip()

    @staticmethod
    def is_poor(text: str) -> bool:
        if FAILED_TEST.match(text):
            return False
        return len(text) > CARD_LINE_CHARACTERS or len(CODE_SYMBOLS.findall(text)) >= CODE_SYMBOL_COUNT
