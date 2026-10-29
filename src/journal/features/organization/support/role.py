from dataclasses import dataclass

from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.role_models import RoleModels
from journal.providers.support.profile import Profile
from journal.providers.support.profile_type import ProfileType

EDIT_TOOL = "edit_files"


@dataclass(frozen=True)
class Role:
    """One Role read from its contract: who it is, what it may do and the guidance it works by; solo pushes it as a state and a seat renders it as an agent spec, both from this one value."""

    id: str
    title: str
    domain: str
    description: str
    cardinality: Cardinality
    writes: bool
    responsible: tuple[str, ...]
    not_responsible: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    edges: tuple[Edge, ...]
    skills: tuple[str, ...]
    tools: tuple[str, ...]
    approval_required: tuple[ApprovalAction, ...]
    models: RoleModels
    guidance: str

    def needs_approval(self, action: ApprovalAction) -> bool:
        return action in self.approval_required

    def allows_tool(self, tool: str) -> bool:
        return tool in self.tools

    def allows_edits(self) -> bool:
        return self.writes and self.allows_tool(EDIT_TOOL)

    def has_worktree(self) -> bool:
        return self.writes

    def waits_in_queue(self) -> bool:
        return self.cardinality.is_queued()

    def edges_of(self, kind: EdgeKind) -> tuple[Edge, ...]:
        return tuple(edge for edge in self.edges if edge.is_kind(kind))

    def edge_targets(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(edge.to for edge in self.edges))

    def profile(self, domain_guidance: str, tools: str) -> Profile:
        return Profile(self.id, self.description, tools, self.body(domain_guidance), ProfileType.WORKER if self.writes else ProfileType.SUBAGENT)

    def body(self, domain_guidance: str) -> str:
        duties = "\n".join([self.listed("You are responsible for", self.responsible), self.listed("You do not", self.not_responsible), self.listed("You start from", self.inputs), self.listed("You deliver", self.outputs)])
        return "\n\n".join(part for part in (domain_guidance.strip(), self.guidance.strip(), duties) if part)

    @staticmethod
    def listed(heading: str, lines: tuple[str, ...]) -> str:
        return f"{heading}:\n" + "\n".join(f"- {line}" for line in lines)
