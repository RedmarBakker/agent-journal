from journal.features.organization.support.domain_plan import DomainPlan
from journal.models.plan import Plan
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.tasks import PLAN_LINK


class DomainPlans:
    """The plans of every environment that have tasks in one domain, in the order they were made, each with only that domain's tasks."""

    def __init__(self, domains: DomainRows, links: Links, plans: Plans) -> None:
        self.domains, self.links, self.plans = domains, links, plans

    def of(self, domain_id: str) -> tuple[DomainPlan, ...]:
        tasks = self.domains.domain_tasks(domain_id)
        reviewed, grouped = self.domains.reviewed_ids(tasks), {}
        for task in tasks:
            for ref in self.links.targets(task, PLAN_LINK):
                grouped.setdefault(ref.id, []).append(task)
        return tuple(DomainPlan(self.plans.find(plan_id), tuple(planned), reviewed) for plan_id, planned in sorted(grouped.items()))

    def on_board(self, plan: Plan, domain_id: str) -> DomainPlan:
        tasks = self.domains.plan_domain_tasks(plan, domain_id)
        return DomainPlan(plan, tuple(tasks), self.domains.reviewed_ids(tasks))
