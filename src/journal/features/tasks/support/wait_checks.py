from collections.abc import Iterable

from journal.features.tasks.support.wait_targets import WaitTargets
from journal.models.check import Check
from journal.repositories.agents import Agents
from journal.repositories.checks import Checks
from journal.repositories.links import Links
from journal.repositories.tasks import WAIT_LINK
from journal.support.actor import Actor


class WaitChecks:
    """The checks a wait made for itself, deleted once nothing waits on them: no task or plan by a wait link, and no agent's wait on its stack."""

    def __init__(self, checks: Checks, links: Links, agents: Agents) -> None:
        self.checks, self.links, self.agents = checks, links, agents

    def deleted(self, ids: Iterable[int], actor: Actor) -> None:
        unwaited = set(ids) - self.waited()
        for check in self.checks.numbered(sorted(unwaited)):
            if check.wait_target:
                self.checks.delete(check, actor)

    def waited(self) -> set[int]:
        linked = {link.target.id for link in self.links.type_links(WAIT_LINK) if link.target.type == Check.table()}
        return linked | {number for agent in self.agents.unended() for number in WaitTargets.awaited_checks(agent.stack)}
