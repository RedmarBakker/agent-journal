from journal.features.faults.support.developer_tally import LOG_ROWS, STAGES_PREFIX, DeveloperTally
from journal.http.journal.answer_time import AnswerTime
from journal.models.support.model_load import ModelLoad
from journal.models.timing import Timing
from journal.features.faults.support.slow_group import SlowGroup

HOOKS_PREFIX = "developer.hooks."
LOADS_PREFIX = "developer.loads."
LOG_ENTRIES = 100


class DeveloperNumbers:
    """What the Developer tab and the journal developer command read of how the journal answers: the average and slowest per kind, the newest and slowest requests from the rolling log, the newest requests with the rows they loaded, and the rows loaded per model since the last reset."""

    def __init__(self, tally: DeveloperTally) -> None:
        self.tally = tally

    def series(self, prefix: str) -> dict[str, int]:
        return self.tally.series(prefix)

    def hook_time(self) -> AnswerTime:
        return AnswerTime.read(self.series(HOOKS_PREFIX), "developer.hooks")

    def request_time(self) -> AnswerTime:
        return AnswerTime.read(self.series("developer.requests."), "developer.requests")

    def hook_averages(self) -> dict[str, AnswerTime]:
        numbers = self.series(HOOKS_PREFIX)
        kinds = sorted({key.split(".")[2] for key in numbers if key.count(".") == 3})
        return {kind: AnswerTime.read(numbers, f"{HOOKS_PREFIX}{kind}") for kind in kinds}

    def stage_averages(self) -> dict[str, AnswerTime]:
        numbers = self.series(STAGES_PREFIX)
        stages = sorted({key.removeprefix(STAGES_PREFIX).rsplit(".", 1)[0] for key in numbers})
        return {stage: AnswerTime.read(numbers, f"{STAGES_PREFIX}{stage}") for stage in stages}

    def recent(self) -> list[Timing]:
        return self.tally.timings()[:LOG_ENTRIES]

    def slowest(self, limit: int = LOG_ENTRIES) -> list[Timing]:
        return sorted(self.tally.timings(), key=lambda timing: -timing.ms)[:limit]

    def groups(self) -> list[SlowGroup]:
        return SlowGroup.grouped(self.slowest(LOG_ROWS))

    def slowest_hooks(self, limit: int) -> list[Timing]:
        return [timing for timing in self.slowest(LOG_ROWS) if timing.is_hook()][:limit]

    def slowest_requests(self, limit: int) -> list[Timing]:
        return [timing for timing in self.slowest(LOG_ROWS) if not timing.is_hook()][:limit]

    def loaded(self) -> list[Timing]:
        return [timing for timing in self.recent() if timing.loads.counts]

    def model_totals(self) -> list[ModelLoad]:
        totals = [ModelLoad(key.removeprefix(LOADS_PREFIX), rows) for key, rows in self.series(LOADS_PREFIX).items()]
        return sorted(totals, key=lambda total: -total.rows)

    def reset(self) -> None:
        self.tally.cleared()
