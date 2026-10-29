from dataclasses import dataclass


@dataclass(frozen=True)
class Timespan:
    """A span in tool uses and seconds, read as a limit: Timespan(tool_uses=30, seconds=300) <= elapsed holds once the elapsed span reaches either part the limit names; a part left at zero is no limit."""

    tool_uses: int = 0
    seconds: float = 0.0

    def __le__(self, elapsed: "Timespan") -> bool:
        return bool(self.tool_uses and elapsed.tool_uses >= self.tool_uses) or bool(self.seconds and elapsed.seconds >= self.seconds)
