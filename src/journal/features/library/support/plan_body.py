from dataclasses import asdict

from journal.features.library.support.phase_outline import PhaseOutline
from journal.features.library.support.portable_body import PortableBody


class PlanBody:
    """A plan as the library carries it, an outline alone: its title and its phases, each with its complete-when line, its checkpoint and its tasks' titles; never its state, its brief, its tasks' briefs or numbers."""

    @staticmethod
    def text(title: str, phases: list[PhaseOutline]) -> str:
        return PortableBody.text({"title": title, "phases": [asdict(phase) for phase in phases]})

    @staticmethod
    def title(body: str) -> str:
        return str(PortableBody.fields(body)["title"])

    @staticmethod
    def phases(body: str) -> list[PhaseOutline]:
        return [PhaseOutline(str(phase["title"]), str(phase["completion_rule"]), bool(phase["checkpoint"]), tuple(phase["task_titles"])) for phase in PortableBody.fields(body)["phases"]]
