from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.template import Template
from journal.repositories.links import Links
from journal.repositories.templates import Templates
from journal.support.actor import Actor
from journal.support.rejection import Rejection

TESTING_LINK = "testing"
NONE_TITLE = "none"
PLAN_TARGET = "plan"


class PlanTesting:
    """The testing template a plan follows, stored as a link from the plan to the template: chosen by its title, none clearing it, and read back."""

    def __init__(self, links: Links, templates: Templates) -> None:
        self.links, self.templates = links, templates

    def templates_offered(self) -> list[Template]:
        return self.templates.testing(PLAN_TARGET)

    def chosen(self, plan: Plan) -> list[Template]:
        return [self.templates.find(ref.id) for ref in self.links.targets(plan, TESTING_LINK)]

    def follow(self, plan: Plan, title: str, actor: Actor) -> list[Template]:
        if title == NONE_TITLE:
            self.clear(plan, actor)
            return []
        return [self.choose(plan, title, actor)]

    def choose(self, plan: Plan, title: str, actor: Actor) -> Template:
        matches = self.templates.testing_titled(title, PLAN_TARGET)
        if not matches:
            raise Rejection(f"no plan testing template is titled {title}: {', '.join(template.title for template in self.templates_offered())}")
        self.clear(plan, actor)
        self.links.save(Link(source=Ref.build(plan), target=Ref.build(matches[0]), kind=TESTING_LINK), actor)
        return matches[0]

    def clear(self, plan: Plan, actor: Actor) -> None:
        for link in self.links.source_links(plan, TESTING_LINK):
            self.links.delete(link, actor)
