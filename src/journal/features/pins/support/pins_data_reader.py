import re

from journal.engine.support.lazy_facts import LazyFacts
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.repositories.notices import Notices
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.stage_times import StageTimes
from journal.features.pins.pins_nudges import PinsNudges
from journal.features.pins.pins_options import PinsOptions

LINK = re.compile(r"https?://[^\s<>()\[\]\"'`]+")


class PinsDataReader:
    """Reads the pins feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields PinsData names."""

    def __init__(self, notices: Notices, entries: Entries, settings: SettingRows, scope: Scope, stages: StageTimes) -> None:
        self.notices, self.entries, self.settings, self.scope, self.stages = notices, entries, settings, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("pins", {
            "pinned": lambda: tuple(n.link.rstrip("/") for n in self.notices.open_scoped()),
            "recent_suggestions": lambda: self.recent_suggestions(agent),
            "newest_pin_at": lambda: self.newest_pin_moment(),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def newest_pin_moment(self) -> float | None:
        newest = self.notices.newest_scoped()
        return newest.creation_time.timestamp() if newest is not None else None

    def recent_suggestions(self, agent: Agent) -> tuple[str, ...]:
        interval = self.settings.integer(PinsOptions.PIN_SUGGESTION_INTERVAL)
        return tuple(url.rstrip("/") for line in self.entries.use_lines(agent.session, PinsNudges.LINK_PIN_REQUEST.key, agent.tool_uses - interval) for url in LINK.findall(line))
