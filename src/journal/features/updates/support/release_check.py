from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ReleaseCheck:
    """One machine's last look at GitHub for releases: when it was, until when GitHub refuses more looks, and the tags it read."""

    last_check_at: float = 0.0
    refusal_end_at: float = 0.0
    tags: tuple[str, ...] = ()

    @classmethod
    def parsed(cls, data: dict) -> "ReleaseCheck":
        return cls(float(data.get("last_check_at", 0.0)), float(data.get("refusal_end_at", 0.0)), tuple(data.get("tags", ())))

    def published(self) -> dict:
        return asdict(self)

    def next_check_time(self, interval_seconds: float) -> float:
        return max(self.last_check_at + interval_seconds, self.refusal_end_at)

    def prefixed_tags(self, prefix: str) -> list[str]:
        return [tag for tag in self.tags if tag.startswith(prefix)]
