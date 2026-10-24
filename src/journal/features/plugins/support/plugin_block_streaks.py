from dataclasses import dataclass, field


@dataclass
class PluginBlockStreaks:
    """How many times in a row each plugin has held each session's agent with nothing of it getting through, and until when a plugin that held too often is passed over, so no plugin can hold an agent in a loop."""

    counts: dict[tuple[str, str], int] = field(default_factory=dict)
    pause_ends: dict[tuple[str, str], float] = field(default_factory=dict)

    def is_paused(self, plugin: str, session: str, time: float) -> bool:
        return self.pause_ends.get((plugin, session), 0.0) > time

    def exceeds_limit(self, plugin: str, session: str, time: float, limit: int, pause_seconds: float) -> bool:
        key = (plugin, session)
        self.counts[key] = self.counts.get(key, 0) + 1
        if limit <= 0 or self.counts[key] <= limit:
            return False
        self.counts[key] = 0
        self.pause_ends[key] = time + pause_seconds
        return True

    def passed(self, plugin: str, session: str) -> None:
        self.counts.pop((plugin, session), None)
