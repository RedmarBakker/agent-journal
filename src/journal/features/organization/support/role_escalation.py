from journal.chat.moment_cards import MomentCards
from journal.events.rows.role_escalated import RoleEscalated
from journal.features.organization.support.organization import Organization
from journal.models.agent import Agent
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.support.card_outcome import CardOutcome
from journal.support.card_type import CardType

ESCALATED_LINK = "reported_to"


class RoleEscalation:
    """Reports a Role that is stuck, was refused or ended without clocking out up the hub, to the first of these that is running: its Domain agent, the Plan agent of its plan, else the user. To an agent the report is a link from the worker to it carrying RoleEscalated, which that agent's conduct says to it; to the user it is a card in the chat of the agent that dispatched the worker."""

    def __init__(self, organization: Organization, domains: DomainRows, plans: Plans, agents: Agents, links: Links, cards: MomentCards) -> None:
        self.organization, self.domains, self.plans, self.agents, self.links, self.cards = organization, domains, plans, agents, links, cards

    def report(self, worker: Worker, what: str, why: str, actor: Actor) -> None:
        role = self.organization.at(worker.contract).role(worker.role)
        if role is None:
            return
        head, tail = f"the Role {role.id} of {role.domain} {what}", f"worker {worker.id}, {worker.name}"
        recipient = self.recipient(role.domain, worker.plan_id)
        if recipient is None:
            self.cards.show(worker.environment_id, worker.dispatcher, "Role reported to you", f"{head}\n{why}\n{tail}", row=Ref.build(worker), shows=CardType.WORKERS, outcome=CardOutcome.WARNED)
            return
        self.links.save(Link(source=Ref.build(worker), target=Ref.build(recipient), link_type=ESCALATED_LINK).with_event(RoleEscalated(environment_id=recipient.environment_id, recipient=recipient.session, report=f"{head}: {why} ({tail})")), actor)

    def recipient(self, domain: str, plan_id: int) -> Agent | None:
        hub = (self.domains.agent_id(domain), self.plans.agent_id(self.plans.find(plan_id)) if plan_id else 0)
        return next((agent for agent_id in hub if agent_id and (agent := self.agents.unended_agent(agent_id))), None)
