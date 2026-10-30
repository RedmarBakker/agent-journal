import random

from journal.features.organization.support.domain import Domain
from journal.support.caller import Caller
from tests.lab.behaviour_profile import BehaviourProfile
from tests.observation import Observation
from tests.simulation.agent_session import AgentSession
from tests.simulation.simulator import Simulator


class DomainAgentActor:
    """A simulated Domain agent follows its routing rules at its sampled rate and may escalate a decision."""

    def __init__(self, simulator: Simulator, domain: Domain, environment: str, profile: BehaviourProfile, seed: int) -> None:
        if profile.agent_kind != "domain":
            raise ValueError("a Domain agent needs a domain behaviour profile")
        self.simulator, self.domain, self.profile, self.chance = simulator, domain, profile, random.Random(seed)
        self.session = AgentSession(simulator, Caller.agent(environment, f"lab-domain-{domain.id}", simulator.provider))

    @property
    def session_id(self) -> str:
        return self.session.caller.agent_session

    def session_start(self) -> Observation:
        return self.session.session_start()

    def route(self, job: str) -> str:
        rule = next((rule for rule in self.domain.routing if rule.when.casefold() in job.casefold()), None)
        if rule is None:
            raise ValueError(f"the {self.domain.id} Domain has no routing rule for this job")
        if not self.domain.has_role(rule.role):
            raise ValueError(f"the {self.domain.id} Domain routes to an unknown Role: {rule.role}")
        alternatives = tuple(role for role in self.domain.roles if role != rule.role)
        follows_route = self.profile.follows_line(self.chance) and not self.profile.routes_outside(self.chance)
        if not follows_route and alternatives:
            return self.chance.choice(alternatives)
        return rule.role

    def follows_line(self) -> bool:
        return self.profile.follows_line(self.chance)

    def escalates(self) -> bool:
        return self.profile.escalates(self.chance)
