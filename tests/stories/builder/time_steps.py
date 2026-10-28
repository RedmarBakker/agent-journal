import json

from tests.replay import pass_time, silent_tick


class TimeSteps:
    """Time and the context window in a story: the agent quiet for a while, as the clock's tick finds it, the context reaching a share of its window, as the statusline writes it, and a compaction, as the provider's hooks bring it."""

    def agent_is_quiet_for(self, minutes: float) -> None:
        silent_tick(self.app, minutes * 60)
        self.observed(f"agent is quiet for {minutes} minutes", None, None)

    def agent_is_quiet_past(self, seconds: float) -> None:
        self.silence_tick("agent", seconds)

    def agent_is_quiet_just_under(self, seconds: float) -> None:
        silent_tick(self.app, seconds - 1)
        self.observed(f"agent is quiet just under {seconds} seconds", None, None)

    def worker_is_quiet_past(self, seconds: float) -> None:
        self.silence_tick("worker", seconds)

    def silence_tick(self, agent_kind: str, seconds: float) -> None:
        silent_tick(self.app, seconds + 1)
        self.observed(f"{agent_kind} is quiet past {seconds} seconds", None, None)

    def time_travel(self, seconds: float = 0, minutes: float = 0) -> None:
        pass_time(self.app, seconds + minutes * 60)
        self.observed(f"the clock moves on {seconds + minutes * 60} seconds", None, None)

    def context_reaches(self, percent: int) -> None:
        self.app.config.status_home.mkdir(parents=True, exist_ok=True)
        (self.app.config.status_home / f"{self.scoped_session()}.json").write_text(json.dumps({"context_window": {"used_percentage": percent}}))
        self.observed(f"context reaches {percent}%", None, None)

    def agent_consumes_context(self, percent: int) -> None:
        self.context_reaches(percent)
        self.agent_reads()

    def compaction_begins(self) -> None:
        self.hooked("a compaction begins", "PreCompact")

    def compacted_session_starts(self) -> None:
        self.hooked("context is compacted", "SessionStart", source="compact")

    def context_is_compacted(self) -> None:
        self.compaction_begins()
        self.compacted_session_starts()
