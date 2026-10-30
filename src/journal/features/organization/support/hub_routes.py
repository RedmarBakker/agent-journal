from journal.features.organization.support.organization import Organization
from journal.models.worker import Worker

MAIN = "main"


class HubRoutes:
    """Where a send between agents may go: along the containment edges of the organization's graph, a Role to its Domain agent, a Domain agent to its Roles or the Plan agent, the Plan agent to its Domain agents or the main agent, and the main agent to the Plan agent; anything else is sideways and is refused with the hub to use."""

    def __init__(self, organization: Organization) -> None:
        self.organization = organization

    def allowed(self, source: str, target: str) -> bool:
        return any(edge.source == source and edge.target == target for edge in self.organization.contracts().containment())

    def refusal(self, sender: Worker, target: Worker) -> str:
        if not sender.role or not target.role:
            return ""
        contracts = self.organization.contracts()
        source, destination = contracts.role(sender.role), contracts.role(target.role)
        if source is None or destination is None or self.allowed(contracts.role_id(source), contracts.role_id(destination)):
            return ""
        return f"worker {sender.id} works as the Role {source.id} and worker {target.id} as {destination.id}: {self.refusal_for(contracts.role_id(source), contracts.role_id(destination))}"

    def refusal_for(self, source: str, target: str) -> str:
        if self.allowed(source, target):
            return ""
        if source.startswith("role:"):
            domain = source.removeprefix("role:").split("/", 1)[0]
            return f"Roles do not send to each other. Send it to your Domain agent, domain:{domain}, which passes it on"
        if source.startswith("domain:"):
            return "Domain agents do not send sideways. Send it to your Plan agent, plan, which passes it on"
        if source == "plan":
            return "the Plan agent sends to the main agent; send it to your main agent, main"
        if source == MAIN:
            return "the main agent sends to the Plan agent, plan"
        return f"{source} may not send to {target} along the organization's hub routes"
