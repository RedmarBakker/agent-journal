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
    """Reports Role failures up the hub and reports seat or cost cap pauses directly to the Plan agent and user."""

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

    def cap_reached(self, worker: Worker, reason: str, actor: Actor, plan_id: int = 0) -> None:
        role = self.organization.at(worker.contract).role(worker.role)
        if role is None:
            return
        plan_id = plan_id or worker.plan_id
        report = (f"plan {plan_id} was paused after its Estimated API cost reached the configured cap: "
                  f"{reason} (Role {role.id} of {role.domain}, worker {worker.id}, {worker.name})")
        self.cap_notice(worker, "Estimated API cost cap reached", report, "cost", actor, plan_id)

    def seat_cap_waiting(self, worker: Worker, reason: str, actor: Actor) -> None:
        role = self.organization.at(worker.contract).role(worker.role)
        if role is None:
            return
        report = (f"seat for plan {worker.plan_id} is paused at the shared OpenRig seat cap; {reason} "
                  f"(Role {role.id} of {role.domain}, worker {worker.id}, {worker.name})")
        self.cap_notice(worker, "Shared OpenRig seat cap reached", report, "seats", actor, worker.plan_id)

    def cap_notice(self, worker: Worker, label: str, report: str, key: str, actor: Actor, plan_id: int) -> None:
        plan_agent_id = self.plans.agent_id(self.plans.find(plan_id)) if plan_id else 0
        plan_agent = self.agents.unended_agent(plan_agent_id) if plan_agent_id else None
        if plan_agent is not None:
            self.links.save(Link(source=Ref.build(worker), target=Ref.build(plan_agent), link_type=ESCALATED_LINK).with_event(
                RoleEscalated(environment_id=plan_agent.environment_id, recipient=plan_agent.session, report=report)), actor)
        self.cards.show(worker.environment_id, worker.dispatcher, label, report, row=Ref.build(worker), actor=actor,
                        key=f"organization-cap:{worker.id}:{key}", shows=CardType.WORKERS, outcome=CardOutcome.WARNED)

    def recipient(self, domain: str, plan_id: int) -> Agent | None:
        hub = (self.domains.agent_id(domain), self.plans.agent_id(self.plans.find(plan_id)) if plan_id else 0)
        return next((agent for agent_id in hub if agent_id and (agent := self.agents.unended_agent(agent_id))), None)
