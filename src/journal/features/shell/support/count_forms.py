import re
from collections import Counter
from dataclasses import dataclass

SLASH_PROGRESS = r"(\d+)\s*/\s*(\d+)"
WORD_PROGRESS = r"(\d+)\s+(?:of|out of)\s+(\d+)"
COUNT_PATTERN = re.compile(rf"\b{SLASH_PROGRESS}\b|\b{WORD_PROGRESS}\b")
PERCENT_PATTERN = re.compile(r"\[\s*(\d+)%\]")
# a line that names a total once and what it counts: collected 40 items, Found 12 servers, Deploying to 8 hosts; never a span of
# time, such as Refreshing run status every 20 seconds, whose number is an interval
TOTAL_LINE = re.compile(r"^\W*(?P<lead>[A-Za-z][A-Za-z ]*?[A-Za-z])\s+(?P<total>\d+)\s+(?!(?:seconds|secs|minutes|mins|hours|hrs|days|weeks|milliseconds|ms)\b)[A-Za-z]+s\b")
# a line that is a counter alone: processed 120, Downloaded: 15 files
COUNTER_LINE = re.compile(r"^\W*(?P<lead>[A-Za-z][A-Za-z ]*?[A-Za-z])\s*[:=]?\s*(?P<count>\d+)(?:\s+[A-Za-z]+)?\s*$")
# the lines that name one finished item each before the total counts, and the readings of a counter before it is one
LEAST_ITEMS = 2
LEAST_COUNTS = 3


@dataclass(frozen=True)
class CountForm:
    """A way a run prints how far it has come as a count of a total: the pattern that reads it, the pattern that counts finished items when the total is printed once, and the words that tell the agent how to give a reader both."""

    progress: str
    advice: str
    step: str = ""


class CountForms:
    """The common forms of a count of a total in a run's lines, 12/40, [3/10], Step 3/10, 3 of 10, (3 of 10), item 3 out of 10, and a total printed once followed by a line for each finished item; and a run that prints a counter and no total. Figures that count towards a total never pass it, and most of them share it, as a run's progress does; numbers inside names, such as the card numbers 65/131 and 225/182 in a list of products, pass their total or each name a total of its own."""

    @classmethod
    def form(cls, lines: list[str]) -> CountForm | None:
        if cls.is_count_series(cls.figures(SLASH_PROGRESS, lines)):
            return CountForm(SLASH_PROGRESS, "the run prints a count of a total: give the reader --progress '(\\d+)/(\\d+)'")
        if cls.is_count_series(cls.figures(WORD_PROGRESS, lines)):
            return CountForm(WORD_PROGRESS, "the run prints a count of a total: give the reader --progress '(\\d+) (?:of|out of) (\\d+)'")
        return cls.total_once(lines)

    @staticmethod
    def figures(pattern: str, lines: list[str]) -> list[tuple[int, int]]:
        return [(int(match[0]), int(match[1])) for line in lines for match in re.findall(pattern, line) if len(match) == 2 and all(match)]

    @staticmethod
    def percentages(pattern: str, lines: list[str]) -> list[int]:
        return [int(match) for line in lines for match in re.findall(pattern, line) if isinstance(match, str) and match.isdigit()]

    @staticmethod
    def is_count_series(figures: list[tuple[int, int]]) -> bool:
        if not figures or any(count > total for count, total in figures):
            return False
        _, shared = Counter(total for _, total in figures).most_common(1)[0]
        return shared * 2 >= len(figures)

    @classmethod
    def total_once(cls, lines: list[str]) -> CountForm | None:
        for number, line in enumerate(lines):
            match = TOTAL_LINE.match(line)
            if match is None or cls.lead_count(lines, match["lead"]) != 1:
                continue
            step, items = cls.item_step([following for following in lines[number + 1:] if following.split()])
            if LEAST_ITEMS <= items <= int(match["total"]):
                progress = rf"{re.escape(match['lead'])}\s+(?P<total>\d+)"
                return CountForm(progress, f"the run prints its total once, \"{line.strip()[:120]}\", and a line for each finished item: give the reader --progress '{progress}' --step '{step}'", step)
        return None

    @staticmethod
    def item_step(lines: list[str]) -> tuple[str, int]:
        first_counts, end_counts = Counter(line.split()[0] for line in lines), Counter(line.split()[-1] for line in lines)
        first, first_lines = max(first_counts.items(), key=lambda pair: pair[1], default=("", 0))
        end, end_lines = max(end_counts.items(), key=lambda pair: pair[1], default=("", 0))
        if end_lines > first_lines:
            return rf"\s{re.escape(end)}\s*$", end_lines
        return rf"^\s*{re.escape(first)}\b", first_lines

    @staticmethod
    def lead_count(lines: list[str], lead: str) -> int:
        return sum(1 for line in lines if (match := TOTAL_LINE.match(line)) and match["lead"] == lead)

    @classmethod
    def progress_lines(cls, lines: list[str]) -> list[str]:
        shown = [line for line in lines if PERCENT_PATTERN.search(line) or COUNT_PATTERN.search(line)]
        return shown or [line for line in lines if TOTAL_LINE.match(line)][:1]

    @classmethod
    def has_total(cls, lines: list[str]) -> bool:
        return any(PERCENT_PATTERN.search(line) for line in lines) or cls.form(lines) is not None

    @classmethod
    def lacks_total(cls, lines: list[str]) -> bool:
        if cls.has_total(lines):
            return False
        counts: dict[str, list[int]] = {}
        for line in lines:
            if match := COUNTER_LINE.match(line):
                counts.setdefault(match["lead"], []).append(int(match["count"]))
        return any(len(values) >= LEAST_COUNTS and values == sorted(set(values)) for values in counts.values())
