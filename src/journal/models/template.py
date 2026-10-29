from typing import ClassVar
from dataclasses import dataclass

from journal.models.model import Model
from journal.models.template_schedule import TemplateSchedule
from journal.support.rejection import Rejection

# the purpose of a template that says how a plan's agent tests its work
TESTING = "testing"
PLAN_TARGET = "plan"


@dataclass(frozen=True)
class Template(Model):
    """Saved instructions and a starting outline for new items, written once and used many times, for a plan's testing template the commands that run at each phase end, and for a plan template how often it starts a plan of its own. Project-wide."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "purpose", "brief")
    title: str = ""
    targets: tuple[str, ...] = ()
    purpose: str = ""
    brief: str = ""
    parts: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    schedule: TemplateSchedule = TemplateSchedule.NONE

    def scheduled(self, schedule: TemplateSchedule) -> "Template":
        if schedule != TemplateSchedule.NONE and PLAN_TARGET not in self.targets:
            raise Rejection(f"template {self.id} is not for a plan: only a plan template starts on a schedule")
        return self.with_(schedule=schedule)

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.opening_line(self.brief)
