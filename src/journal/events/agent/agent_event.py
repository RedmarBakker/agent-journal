from dataclasses import dataclass, field, replace
from typing import ClassVar, Self

from journal.events.event import Event
from journal.events.feature_data import FeatureData


@dataclass(frozen=True, kw_only=True)
class AgentEvent(Event):
    """Something the agent did, as its hook reported it, with that hook's key, or as the journal saw it. One subclass per kind; features listen to these, never to raw hooks."""

    answers_hook: ClassVar[bool] = True
    has_lines: ClassVar[bool] = True
    typing_delay: ClassVar[float] = 0.0
    is_work: ClassVar[bool] = False
    is_turn_end: ClassVar[bool] = False

    session: str = ""
    environment_id: int = 0
    provider: str = ""
    context: float | None = None
    time: float = 0.0
    data: FeatureData = field(default_factory=lambda: FeatureData({}), compare=False)
    subagent: str = ""
    boot_wait_seconds: float = 0.0
    tool_use: int = 0
    hook_key: str = ""

    @property
    def content(self) -> str:
        return ""

    def journal_text(self) -> str:
        return ""

    def has_hook_lines(self) -> bool:
        return self.answers_hook and self.has_lines

    def with_data(self, data: FeatureData) -> Self:
        return replace(self, data=data)

    def recorded(self) -> dict:
        return {}

    def gap_seconds(self) -> float:
        return 0.0

    def counted(self, tool_use: int) -> Self:
        return replace(self, tool_use=tool_use)

    def hooked(self, key: str) -> Self:
        return replace(self, hook_key=key)

    def boot_delayed(self, seconds: float) -> Self:
        return replace(self, boot_wait_seconds=seconds)

    def is_boot_delayed(self) -> bool:
        return self.boot_wait_seconds > 0

    def placed(self, session: str, environment_id: int, provider: str, context: float | None, time: float, subagent: str = "") -> Self:
        return replace(self, session=session, environment_id=environment_id, provider=provider, context=context, time=time, subagent=subagent)
