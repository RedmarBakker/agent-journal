from journal.features.organization.support.domain_plans import DomainPlans
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role_queue_length import RoleQueueLength
from journal.repositories.domain_counts import DomainCounts
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class DomainFigures:
    """Works out one domain's live figures and keeps them in its DomainCount row: the plans active now, and for each of its Roles the instances running and the tasks queued for them."""

    def __init__(self, organization: Organization, domain_plans: DomainPlans, workers: Workers, queues: RoleQueueLength, counts: DomainCounts) -> None:
        self.organization, self.domain_plans, self.workers, self.queues, self.counts = organization, domain_plans, workers, queues, counts

    def figures(self, domain_id: str) -> tuple[int, dict]:
        active = sum(1 for plan in self.domain_plans.of(domain_id) if plan.is_active())
        roles = {}
        for role in self.organization.contracts().roles_of(domain_id):
            instances = self.workers.role_instances_everywhere(role.id)
            roles[role.id] = {"instances": len(instances), "queued": self.queues.of(instances)}
        return active, roles

    def refresh(self, domain_id: str, actor: Actor) -> None:
        if self.organization.contracts().domain(domain_id) is not None:
            active, roles = self.figures(domain_id)
            self.counts.kept(domain_id, active, roles, actor)

    def refresh_all(self, actor: Actor) -> None:
        for domain in self.organization.contracts().domains:
            self.refresh(domain.id, actor)
