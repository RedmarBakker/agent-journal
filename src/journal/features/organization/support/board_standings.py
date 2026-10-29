from journal.events.rows.plan_entered_board_phase import PlanEnteredBoardPhase
from journal.features.organization.support.domain_plans import DomainPlans
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.domain_rows import BOARD_LINKS, DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.tasks import PLAN_LINK
from journal.support.actor import Actor


class BoardStandings:
    """Keeps the phase each plan stands in on each domain's board as a link from the plan to the domain, moved when a task of the plan changes and firing PlanEnteredBoardPhase as it moves; a plan with no task left in a domain leaves its board."""

    def __init__(self, domains: DomainRows, domain_plans: DomainPlans, links: Links, plans: Plans) -> None:
        self.domains, self.domain_plans, self.links, self.plans = domains, domain_plans, links, plans

    def task_moved(self, task: Task, actor: Actor) -> None:
        names = self.domains.domain_names(task)
        for ref in self.links.targets(task, PLAN_LINK):
            plan = self.plans.find(ref.id)
            for name in dict.fromkeys([*names, *self.domains.board_names(plan)]):
                self.placed(plan, name, actor)

    def placed(self, plan: Plan, name: str, actor: Actor) -> None:
        row, domain_plan = self.domains.named(name, actor), self.domain_plans.on_board(plan, name)
        phase = domain_plan.phase()
        if domain_plan.is_on_board() and self.domains.standing(plan, row) == phase:
            return
        for link in self.domains.standing_links(plan, row):
            self.links.delete(link, actor)
        if domain_plan.is_on_board():
            self.links.save(Link(source=Ref.build(plan), target=Ref.build(row), link_type=BOARD_LINKS[phase]).with_event(PlanEnteredBoardPhase(environment_id=plan.environment_id, plan_id=plan.id, domain=name, phase=phase)), actor)
