from collections import Counter
from statistics import mean

from tests.simulation.sample import Sample
from tests.simulation.trace_entry import TraceEntry


class Rescoring:
    """Scores recorded runs again with candidate profiles, offline, through the pure ModeProfile.scored, so a sweep over many profiles takes seconds: per profile its mean score over the measured steps, the run's mean load, and its nudges and refusals an hour."""

    def __init__(self, samples: list[Sample], trace: list[TraceEntry]) -> None:
        self.samples, self.trace = samples, trace

    def row(self, profile) -> dict:
        scores = [score.score for sample in self.samples if (score := profile.scored(sample.counts)).is_measured]
        hours = max(self.trace[-1].second / 3600, 1 / 60) if self.trace else 1.0
        return {
            "profile": profile.mode,
            "score": round(mean(scores), 1) if scores else None,
            "measured": len(scores),
            "mode": self.samples[-1].counts.mode if self.samples else "",
            "mode_uses": self.samples[-1].counts.mode_uses if self.samples else 0,
            "actions": self.actions(),
            "load": round(mean(sample.rho for sample in self.samples), 2) if self.samples else 0.0,
            "nudges_hourly": round(sum(len(entry.nudges) for entry in self.trace) / hours, 1),
            "refusals_hourly": round(sum(1 for entry in self.trace if entry.refused) / hours, 1),
            "refused": dict(Counter(f"{entry.action}: {entry.nudges[-1] if entry.nudges else entry.status}" for entry in self.trace if entry.refused).most_common(3)),
        }

    def actions(self) -> int:
        last = self.samples[-1].counts if self.samples else None
        return last.file_edits + last.handovers + last.subagent_dispatches + last.research_count if last else 0

    def table(self, profiles) -> list[dict]:
        return [self.row(profile) for profile in profiles]
