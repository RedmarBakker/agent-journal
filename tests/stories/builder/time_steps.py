import json

from tests.replay import silent_tick


class TimeSteps:
    """Time and the context window in a story: the agent quiet for a while, as the clock's tick finds it, the context reaching a share of its window, as the statusline writes it, and a compaction, as the provider's hooks bring it."""

    def agent_is_quiet_for(self, minutes: float) -> None:
        silent_tick(self.app, minutes * 60)
        self.observed(f"agent is quiet for {minutes} minutes", None, None)

    def context_reaches(self, percent: int) -> None:
        self.app.config.status_home.mkdir(parents=True, exist_ok=True)
        (self.app.config.status_home / "s1.json").write_text(json.dumps({"context_window": {"used_percentage": percent}}))
        self.observed(f"context reaches {percent}%", None, None)

    def agent_consumes_context(self, percent: int) -> None:
        self.context_reaches(percent)
        self.agent_reads()

    def context_is_compacted(self) -> None:
        self.posted_hook("PreCompact")
        self.hooked("context is compacted", "SessionStart", source="compact")
