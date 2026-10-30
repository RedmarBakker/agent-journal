from dataclasses import replace

from journal.features.seed import Seed
from journal.features.templates.shipped import SHIPPED
from journal.support.actor import Actor
from journal.repositories.templates import Templates
from journal.sync.team_account import TeamAccount

SHIPPED_FIELDS = ("targets", "purpose", "brief", "parts", "commands")


class BuiltinTemplates(Seed):
    """The shipped templates, written by title and brought back to what this journal ships at every start, so an install or update carries their newest words; in a team only by the machine that holds the team's upgrade, so no two machines write the same one."""

    def __init__(self, templates: Templates, account: TeamAccount) -> None:
        self.templates, self.account = templates, account

    def run(self) -> None:
        if not self.account.is_seed_writer():
            return
        present = {template.title: template for template in self.templates.all()}
        for template in SHIPPED:
            stored = present.get(template.title)
            if stored is None:
                self.templates.save(template, Actor.system())
            elif any(getattr(stored, field) != getattr(template, field) for field in SHIPPED_FIELDS):
                self.templates.save(replace(stored, **{field: getattr(template, field) for field in SHIPPED_FIELDS}), Actor.system())
