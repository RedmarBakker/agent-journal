import re

TOKEN_PATTERN = re.compile(r"`[^`]*`|[A-Za-z][A-Za-z'-]*|\d+(?:[.:,/-]\d+)*|\S")
# the words that name a row before its number, so the number is already linked
ROW_KINDS = frozenset({
    "task", "tasks", "plan", "plans", "worker", "workers", "report", "reports", "doc", "docs", "document", "documents", "message", "messages",
    "question", "questions", "output", "outputs", "check", "checks", "phase", "phases", "commit", "point", "points", "step", "steps",
    "reaction", "reactions", "memory", "memories", "rule", "rules", "reminder", "reminders", "setting", "settings", "entry", "entries", "notice",
    "dump", "item", "items", "sequence", "sequences", "template", "templates", "alias", "aliases", "subagent", "turn", "line", "lines", "#",
})
# the words that make a number a count, a time or a size, never a row
COUNT_UNITS = frozenset({
    "passed", "pass", "passing", "failed", "fail", "failing", "errors", "error", "tests", "test", "seconds", "second", "minutes", "minute", "hours", "hour", "ms", "s", "points",
    "files", "file", "lines", "runs", "rows", "bytes", "mb", "gb", "kb", "%", "times", "tool", "uses", "words", "characters", "chars",
    "of", "more", "deselected", "skipped", "items", "places", "workers", "tasks", "sins", "commits", "messages", "per", "percent", "cent",
})
# the words before a number that make it a count or a position, such as case 121, at 100, clamped to 100 or 1324 of 1324
COUNT_PREFIXES = frozenset({"case", "cases", "at", "of", "to", "from", "number", "count", "total"})
# the words before a number that make it a status a program answered, such as the server answered 200 or HTTP 404
STATUS_PREFIXES = frozenset({"status", "http", "https", "answered", "answers", "returned", "returns", "code", "responded", "got"})
# the words after a number that make it a status, such as 200 OK
STATUS_FOLLOWERS = frozenset({"ok", "not", "created", "found", "forbidden", "unauthorized"})
# the kind amend-links takes for a number that names no row, so it stays as written
PLAIN = "none"
# the joining words of a list of numbers after one kind word, such as tasks 3345, 3346 and 3347
LIST_JOINS = frozenset({",", "and", "or", "&", "/"})
LEAST_ROW_NUMBER = 100
# the marks a number quoted as itself stands between, such as my message said "3419", which is cited and never linked
QUOTE_CHARACTERS = frozenset({'"', "'", "“", "”", "‘", "’"})
# the kind of row a number is linked to, by its word, in the order a number's most likely kind is looked up
ROW_TABLES = {"task": "tasks", "plan": "plans", "worker": "workers", "report": "reports", "doc": "docs", "question": "questions", "message": "messages"}


class UnlinkedRowNumbers:
    """The numbers in a message written without the kind of row before them, the ones that could name a row: a number of at least three digits, never a count, a position, a percentage, a time, a size, a version or a status a program answered, never inside code or quoted on its own, and never one of a list that follows a kind word."""

    @classmethod
    def numbers(cls, text: str) -> list[int]:
        return list(dict.fromkeys(number for number, _ in cls.spans(text)))

    @classmethod
    def spans(cls, text: str) -> list[tuple[int, tuple[int, int]]]:
        matches = list(TOKEN_PATTERN.finditer(text))
        tokens = [match.group() for match in matches]
        return [(int(tokens[i]), matches[i].span()) for i in range(len(tokens)) if cls.is_unlinked(tokens, i)]

    @classmethod
    def linked(cls, text: str, kinds: list[str]) -> str:
        spans = cls.spans(text)
        for (number, (start, end)), kind in reversed([(span, kind) for span, kind in zip(spans, kinds) if kind != PLAIN]):
            text = f"{text[:start]}{kind} {number}{text[end:]}"
        return text

    @classmethod
    def is_unlinked(cls, tokens: list[str], i: int) -> bool:
        candidate = tokens[i]
        if not candidate.isdigit() or int(candidate) < LEAST_ROW_NUMBER:
            return False
        next_token = tokens[i + 1].lower() if i + 1 < len(tokens) else ""
        quoted = i > 0 and tokens[i - 1] in QUOTE_CHARACTERS and next_token in QUOTE_CHARACTERS
        preceding = cls.preceding_word(tokens, i)
        return not quoted and next_token not in COUNT_UNITS | STATUS_FOLLOWERS and preceding not in ROW_KINDS | COUNT_PREFIXES | STATUS_PREFIXES and not cls.is_timed(tokens, i)

    @staticmethod
    def is_timed(tokens: list[str], i: int) -> bool:
        return i + 3 < len(tokens) and tokens[i + 1].lower() == "in" and tokens[i + 2].isdigit() and tokens[i + 3].lower() in COUNT_UNITS

    @staticmethod
    def preceding_word(tokens: list[str], i: int) -> str:
        j = i - 1
        while j >= 0 and (tokens[j].isdigit() or tokens[j].lower() in LIST_JOINS):
            j -= 1
        return tokens[j].lower() if j >= 0 else ""
