import re

from journal.chat.card_detail import DETAIL_CHARACTERS

CODE_SYMBOLS = re.compile(r"[{}\[\]();=\"]")
CODE_SYMBOL_COUNT = 8
CARD_LINE_CHARACTERS = DETAIL_CHARACTERS
# the columns a report pads with runs of spaces, which a card line reads as one
SPACES = re.compile(r"\s{2,}")
FRAME = re.compile(r"^[=\-*#_~ ]{3,}|[=\-*#_~ ]{3,}$")
# a failed or errored test named by its id, or marked failed by vitest or jest, the line a person reads first however long the test's name
FAILED_TEST = re.compile(r"^(FAILED|ERROR) \S+::\S+|^(×|✗|✕|FAIL)\s+\S")
# a line of prose: a commit subject, a sentence, however long up to the most a card holds
PROSE_CHARACTERS = 200
PROSE_WORDS = 4
PROSE_SHARE = 0.8
WORD = re.compile(r"[\w'’,.;!?()-]+")
PROSE_BREAKS = re.compile(r"[{}\[\]=\"/\\]|\S:\d")


class CardLine:
    """A line a reader picks as the card shows it, its frame of = or - signs taken off, as pytest draws round its summary; and whether it reads as a status for the user: neither code nor data, though a long line of prose is read as a sentence, and short enough for the card's line, never cut to fit."""

    @staticmethod
    def plain(text: str) -> str:
        return SPACES.sub(" ", FRAME.sub("", text).strip())

    @staticmethod
    def is_poor(text: str) -> bool:
        if FAILED_TEST.match(text):
            return False
        if CardLine.is_prose(text):
            return False
        return len(text) > CARD_LINE_CHARACTERS or len(CODE_SYMBOLS.findall(text)) >= CODE_SYMBOL_COUNT

    @staticmethod
    def is_prose(text: str) -> bool:
        words = text.split()
        if len(text) > PROSE_CHARACTERS or len(words) < PROSE_WORDS or PROSE_BREAKS.search(text):
            return False
        return sum(1 for word in words if WORD.fullmatch(word)) >= len(words) * PROSE_SHARE
