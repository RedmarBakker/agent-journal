from dataclasses import asdict, dataclass, replace


@dataclass(frozen=True)
class AgentLoad:
    """The orchestrator's load as last measured, kept on its row: the smoothed arrivals λ and clearings μ an hour, ρ = λ/μ, what waits now (L), how many items and the refs of the oldest few, the minutes the oldest has waited, the minutes from arrival to clearing (W), λW to check L against by Little's law, how many minutes running ρ has stayed over the scale-up level and under the scale-down level, and the handling the fitness scores: the clearings that took the oldest waiting item first among those counted, the items ended without a clearing in the window (sent back, released or stopped), shown as the send-back rate, and the dispatches made while the queue grew over the scale-up level against those made into idle places while ρ was low; with when it was measured and when its places last changed; kept with only the values that differ from an empty load."""

    arrivals: float = 0.0
    clearings: float = 0.0
    rho: float = 0.0
    waiting: float = 0.0
    waiting_refs: tuple[str, ...] = ()
    waiting_items: int = 0
    oldest_wait_minutes: float = 0.0
    wait_minutes: float = 0.0
    little: float = 0.0
    over_minutes: float = 0.0
    under_minutes: float = 0.0
    oldest_first: int = 0
    clearings_counted: int = 0
    removals: int = 0
    dispatches_for: int = 0
    dispatches_against: int = 0
    measured_at: float = 0.0
    scaled_at: float = 0.0

    def published(self) -> dict:
        return {name: value for name, value in asdict(self).items() if value != getattr(EMPTY, name)}

    @classmethod
    def parsed(cls, data: dict) -> "AgentLoad":
        return cls(**{**data, "waiting_refs": tuple(data.get("waiting_refs", ()))})

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
