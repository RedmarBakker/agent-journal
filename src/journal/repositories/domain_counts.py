from journal.models.domain_count import DomainCount
from journal.repositories.repository import Repository
from journal.support.actor import Actor


class DomainCounts(Repository[DomainCount]):
    """One row per domain with its live figures, the same for every environment; a write that changes nothing is not made, so the viewer is told only of a count that moved."""

    model = DomainCount

    def kept(self, name: str, plans_active: int, roles: dict, actor: Actor) -> DomainCount:
        with self.writing():
            rows = self.all_matching(name=name)
            if not rows:
                return self.save(DomainCount(name=name, plans_active=plans_active, roles=roles), actor)
            row = rows[0]
            return row if (row.plans_active, row.roles) == (plans_active, roles) else self.save(row.with_(plans_active=plans_active, roles=roles), actor)
