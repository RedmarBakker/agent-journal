from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.contracts import PLAN, Contracts
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_boot import RoleBoot
from journal.features.organization.support.seat import Seat
from journal.features.organization.support.tool_ids import ToolIds
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.support.allowed_models import AllowedModels
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.repositories.setting_rows import SettingRows

PLAN_POD = "plan"
PLAN_AGENT = "plan-agent"
DOMAIN_AGENT = "domain-agent"
LEADER_TOOLS = ("read_files",)
PLAN_GUIDANCE = "You are the Plan agent of {rig}: you hand the plan's work to the Domain agents of its domains and write no code."


class RigSeats:
    """Who sits in an organization plan's rig and how they are linked: the Plan agent on the strongest model allowed for its configured profile, and for each domain the plan staffs its Domain agent and its Roles of cardinality plan, linked by containment; journal Roles sit in the organization's own rig and many Roles are added per job."""

    def __init__(self, providers: Providers, tools: ToolIds, allowed: AllowedModels, settings: SettingRows) -> None:
        self.providers, self.tools, self.allowed, self.settings = providers, tools, allowed, settings

    def seats(self, rig: str, contracts: Contracts, domains: tuple[str, ...], provider: Provider) -> tuple[Seat, ...]:
        staffed = [domain for domain in contracts.domains if domain.id in domains]
        return (self.plan_agent(rig, provider), *(seat for domain in staffed for seat in (self.domain_agent(domain, provider), *self.role_seats(contracts, domain, provider))))

    def links(self, contracts: Contracts, seats: tuple[Seat, ...]) -> tuple[tuple[Seat, Seat], ...]:
        placed = {seat.qualified: seat for seat in seats}
        return tuple((placed[edge.source], placed[edge.target]) for edge in contracts.containment() if edge.kind is EdgeKind.DELEGATES_TO and edge.source in placed and edge.target in placed)

    def plan_agent(self, rig: str, provider: Provider) -> Seat:
        profile = str(self.settings.option(OrganizationOptions.PLAN_PROFILE))
        model = self.allowed.strongest(provider.name, profile)
        effort = str(self.settings.option(OrganizationOptions.PLAN_EFFORT)) if provider.supports_reasoning_effort else ""
        return Seat(PLAN, PLAN_POD, PLAN_AGENT, "", provider.name, model, effort, PLAN_GUIDANCE.format(rig=rig), (), self.tools.provider_tools(LEADER_TOOLS), False)

    def domain_agent(self, domain: Domain, provider: Provider) -> Seat:
        effort = domain.models.effort if provider.supports_reasoning_effort else ""
        return Seat(Contracts.domain_id(domain.id), domain.id, DOMAIN_AGENT, "", provider.name, domain.models.for_provider(provider.name), effort, domain.body(), domain.skills, self.tools.provider_tools(LEADER_TOOLS), False)

    def role_seats(self, contracts: Contracts, domain: Domain, provider: Provider) -> tuple[Seat, ...]:
        return tuple(self.role_seat(role, domain, provider) for role in contracts.roles_of(domain.id) if role.cardinality is Cardinality.PLAN)

    def role_seat(self, role: Role, domain: Domain, provider: Provider) -> Seat:
        effort = role.models.effort if provider.supports_reasoning_effort else ""
        return Seat(Contracts.role_id(role), domain.id, role.id, role.id, provider.name, RoleBoot.model(role, provider.name), effort, role.body(domain.guidance), role.skills, self.tools.provider_tools(role.tools), role.writes)
