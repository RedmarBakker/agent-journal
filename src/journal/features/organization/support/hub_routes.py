from journal.features.organization.support.organization import Organization
from journal.features.organization.support.contracts import Contracts
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.worker import Worker
from journal.repositories.setting_rows import SettingRows

MAIN = "main"


class HubRoutes:
    """Where a send between agents may go: along the containment edges of the organization's graph, a Role to its Domain agent, a Domain agent to its Roles or the Plan agent, the Plan agent to its Domain agents or the main agent, and the main agent to the Plan agent; anything else is sideways and is refused with the hub to use."""

    def __init__(self, organization: Organization, settings: SettingRows) -> None:
        self.organization, self.settings = organization, settings

    def allowed(self, source: str, target: str) -> bool:
        contracts = self.organization.contracts()
        if any(edge.source == source and edge.target == target for edge in contracts.containment()):
            return True
        if self.settings.option(OrganizationOptions.HUB_ROUTE_STRATEGY) != "same_domain_peers":
            return False
        source_role, target_role = self.domain_role(source, contracts), self.domain_role(target, contracts)
        return bool(source_role and target_role and source_role.domain == target_role.domain and source_role.id != target_role.id)

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
            if self.settings.option(OrganizationOptions.HUB_ROUTE_STRATEGY) == "same_domain_peers":
                return f"Roles may send directly only to peers in one Domain. Send it to your Domain agent, domain:{domain}, which passes it on"
            return f"Roles do not send to each other. Send it to your Domain agent, domain:{domain}, which passes it on"
        if source.startswith("domain:"):
            return "Domain agents do not send sideways. Send it to your Plan agent, plan, which passes it on"
        if source == "plan":
            return "the Plan agent sends to the main agent; send it to your main agent, main"
        if source == MAIN:
            return "the main agent sends to the Plan agent, plan"
        return f"{source} may not send to {target} along the organization's hub routes"

    @staticmethod
    def domain_role(identity: str, contracts: Contracts):
        if not identity.startswith("role:"):
            return None
        domain_id, separator, role_id = identity.removeprefix("role:").partition("/")
        if not separator:
            return None
        return next((role for role in contracts.roles if role.domain == domain_id and role.id == role_id), None)
