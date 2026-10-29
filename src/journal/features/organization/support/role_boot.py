from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role import Role
from journal.features.organization.support.tool_ids import ToolIds
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.support.rejection import Rejection


class RoleBoot:
    """What a job dispatched to a Role starts with: the Role found in the organization and refused when it is unknown or does not write, the instructions made of the worker's rules, its domain's and its own guidance, its duties and the skills to read first, and the model it runs on for the provider."""

    def __init__(self, organization: Organization, tools: ToolIds, profiles: ProfileFiles) -> None:
        self.organization, self.tools, self.profiles = organization, tools, profiles

    def role(self, role_id: str) -> Role:
        role = self.organization.contracts().role(role_id)
        if role is None:
            raise Rejection(f"{role_id} is no Role of the organization: see journal organization list")
        if not role.writes:
            raise Rejection(f"{role_id} does not write: a job that only reads goes to a subagent")
        return role

    def instructions(self, role: Role) -> str:
        domain = self.organization.contracts().domain(role.domain)
        body = role.profile(domain.guidance if domain else "", self.tools.words(role.tools)).body
        skills = f"Read these skills before you work: {', '.join(role.skills)}." if role.skills else ""
        return self.profiles.role_instructions("\n\n".join(part for part in (body, skills) if part))

    @staticmethod
    def model(role: Role, provider: str) -> str:
        return role.models.for_provider(provider)
