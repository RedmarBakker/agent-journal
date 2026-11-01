from dataclasses import asdict, dataclass, fields, replace

# the keys a load was stored under before they took their plain names, read as the names they have now
OLD_KEY_NAMES = {"over_minutes": "busy_minutes", "under_minutes": "low_minutes"}


@dataclass(frozen=True)
class AgentLoad:
    """The worker or message queue's load as last measured, kept on its agent: arrivals and clearings an hour, their ratio, what waits now and its oldest rows, how long the oldest has waited and what a cleared item waited on average; plus the busy and quiet stretches used to scale worker places, and when it was measured and last scaled."""

    arrivals: float = 0.0
    clearings: float = 0.0
    rho: float = 0.0
    waiting: float = 0.0
    waiting_refs: tuple[str, ...] = ()
    waiting_items: int = 0
    oldest_wait_minutes: float = 0.0
    wait_minutes: float = 0.0
    little: float = 0.0
    busy_minutes: float = 0.0
    low_minutes: float = 0.0
    measured_at: float = 0.0
    scaled_at: float = 0.0

    def published(self) -> dict:
        return {name: value for name, value in asdict(self).items() if value != getattr(EMPTY, name)}

    @classmethod
    def parsed(cls, data: dict) -> "AgentLoad":
        field_names = {field.name for field in fields(cls)}
        renamed_data = {OLD_KEY_NAMES.get(key, key): value for key, value in data.items()}
        return cls(**{**{key: value for key, value in renamed_data.items() if key in field_names}, "waiting_refs": tuple(renamed_data.get("waiting_refs", ()))})

    def is_measured(self) -> bool:
        return self.measured_at > 0

    def scaled(self, time: float) -> "AgentLoad":
        return replace(self, scaled_at=time)

    def waiting_text(self, shown_count: int) -> str:
        labels = [self.label(ref) for ref in self.waiting_refs[:shown_count]]
        remaining_count = self.waiting_items - shown_count
        return ", ".join(labels) + (f" and {remaining_count} more" if remaining_count > 0 else "")

    def oldest(self) -> str:
        return self.label(self.waiting_refs[0]) if self.waiting_refs else "nothing"

    @staticmethod
    def label(ref: str) -> str:
        table, _, number = ref.partition(":")
        return f"{table.removesuffix('s')} {number}"


EMPTY = AgentLoad()
