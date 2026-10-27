import json
from dataclasses import dataclass
from pathlib import Path

from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout

FREQUENCY_FILE = Path(__file__).resolve().parent / "nudge_frequency.json"
FREQUENT_PER_THOUSAND = 10
FREQUENT_REPEAT_SECONDS = 60
FREQUENT_LONGEST_CHARACTERS = 80
NORMAL_LONGEST_CHARACTERS = 120
RARE_CEILING_CHARACTERS = 400
FREQUENT, NORMAL, RARE = "frequent", "normal", "rare"


@dataclass(frozen=True)
class NudgeFrequency:
    """How often each line was sent in the simulator's long runs, frozen in tests/nudge_frequency.json, and the class each line's length budget follows: frequent when sent ten or more times per thousand actions or when it may repeat within a minute; rare when it declares a longest above 120 with its reason, or when every run sent it at most once and at least two runs sent it; normal otherwise, a line no run sent among them."""

    counts: dict

    @classmethod
    def frozen(cls) -> "NudgeFrequency":
        return cls(json.loads(FREQUENCY_FILE.read_text()) if FREQUENCY_FILE.is_file() else {})

    @classmethod
    def counted(cls, runs: list[tuple[int, dict[str, int]]], registered: list[str]) -> "NudgeFrequency":
        keys = sorted({*registered, *(key for _, sent in runs for key in sent)})
        actions = sum(count for count, _ in runs)
        return cls({key: {"sent": sum(sent.get(key, 0) for _, sent in runs), "runs": sum(1 for _, sent in runs if key in sent), "most_in_a_run": max((sent.get(key, 0) for _, sent in runs), default=0), "actions": actions} for key in keys})

    def written(self) -> None:
        FREQUENCY_FILE.write_text(json.dumps(self.counts, indent=4, sort_keys=True) + "\n")

    def line_class(self, nudge: Nudge) -> str:
        seen = self.counts.get(nudge.key)
        if self.repeats_within_a_minute(nudge) or seen is not None and seen["sent"] * 1000 >= FREQUENT_PER_THOUSAND * seen["actions"]:
            return FREQUENT
        if nudge.longest_characters > NORMAL_LONGEST_CHARACTERS or seen is not None and seen["most_in_a_run"] <= 1 and seen["runs"] >= 2:
            return RARE
        return NORMAL

    def budget_characters(self, nudge: Nudge) -> int:
        line_class = self.line_class(nudge)
        if line_class == FREQUENT:
            return FREQUENT_LONGEST_CHARACTERS
        return nudge.longest_characters if line_class == RARE else NORMAL_LONGEST_CHARACTERS

    @staticmethod
    def repeats_within_a_minute(nudge: Nudge) -> bool:
        return nudge.repeat.unit == Timeout.SECONDS and 0 < nudge.repeat.amount < FREQUENT_REPEAT_SECONDS
