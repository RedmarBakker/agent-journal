from dataclasses import dataclass, replace

# how many reports the dispatcher's row holds, the newest; older ones fall out of every window the fitness reads
REPORT_COUNT = 40


@dataclass(frozen=True)
class ReportUse:
    """The reports its workers filed to an agent, each with its time and the count of tasks open for workers at that moment, and the last quick report that cost it a drop in its fitness, with the drop's size and what caused it; and, as last measured, the reports an hour filed while plenty was open, the rates at full and at no score, and the points of the drop not yet recovered."""

    reports: tuple[tuple[float, int], ...] = ()
    drop_at: float = 0.0
    drop_points: int = 0
    hourly_reports: float = 0.0
    full_hourly_reports: float = 0.0
    zero_hourly_reports: float = 0.0
    unrecovered_points: int = 0
    is_measured: bool = False
    drop_cause: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "ReportUse":
        return cls(tuple((float(pair[0]), int(pair[1])) for pair in data["reports"]), float(data.get("drop_at", 0.0)), int(data.get("drop_points", 0)), float(data.get("hourly_reports", 0.0)),
                   float(data.get("full_hourly_reports", 0.0)), float(data.get("zero_hourly_reports", 0.0)), int(data.get("unrecovered_points", 0)), bool(data.get("is_measured", False)), str(data.get("drop_cause", "")))

    def recorded(self, time: float, open_tasks: int) -> "ReportUse":
        return replace(self, reports=(*self.reports, (time, open_tasks))[-REPORT_COUNT:])

    def dropped(self, time: float, points: int, cause: str) -> "ReportUse":
        return replace(self, drop_at=time, drop_points=points, drop_cause=cause)

    # the reports an hour over the window that were filed while plenty was open, and the drop worn down straight to nothing over its recovery minutes
    def measured(self, time: float, window_minutes: float, plenty: int, rates: tuple[float, float], recovery_minutes: float) -> "ReportUse":
        counted = [pair for pair in self.reports if time - pair[0] <= window_minutes * 60 and pair[1] >= plenty]
        recovered = min(1.0, (time - self.drop_at) / max(recovery_minutes * 60, 1.0)) if self.drop_points else 1.0
        return replace(self, hourly_reports=len(counted) * 60 / max(window_minutes, 1.0), full_hourly_reports=rates[0], zero_hourly_reports=rates[1], unrecovered_points=round(self.drop_points * (1 - recovered)), is_measured=bool(self.reports))
