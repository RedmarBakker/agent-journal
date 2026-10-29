from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_models import RoleModels
from journal.features.organization.support.tool_ids import ToolIds
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.providers.support.profile_type import ProfileType


def a_role(**changes) -> Role:
    fields = dict(id="builder", title="Builder", domain="alpha", description="Builds what a task asks.", cardinality=Cardinality.MANY, writes=True, responsible=("the change",), not_responsible=("the release",),
                  inputs=("a task",), outputs=("a commit",), edges=(Edge(EdgeKind.DELEGATES_TO, "scout", "what to look up"), Edge(EdgeKind.ESCALATES_TO, "scout", "a blocker")), skills=("governance",),
                  tools=("read_files", "edit_files", "run_tests", "crm"), approval_required=(ApprovalAction.PRODUCTION_DEPLOYMENT,), models=RoleModels("sonnet", "gpt-6-luna", "max"), guidance="Work in small steps.")
    return Role(**{**fields, **changes})


def test_a_role_answers_what_it_may_do_and_is_the_one_value_solo_and_a_seat_both_read():
    builder, scout = a_role(), a_role(id="scout", writes=False, cardinality=Cardinality.JOURNAL, tools=("read_files",), models=RoleModels("opus", "gpt-6.1-sol", "xhigh"))
    assert builder.allows_edits() and builder.has_worktree() and not builder.waits_in_queue(), "a writer on many has a worktree and its own instance"
    assert not scout.allows_edits() and not scout.has_worktree() and scout.waits_in_queue(), "a non-writer has no worktree and a journal Role is queued on"
    assert builder.needs_approval(ApprovalAction.PRODUCTION_DEPLOYMENT) and not builder.needs_approval(ApprovalAction.CONTRACT_CHANGE)
    assert [edge.about for edge in builder.edges_of(EdgeKind.ESCALATES_TO)] == ["a blocker"] and builder.edge_targets() == ("scout",)
    assert builder.models.for_provider("claude") == "sonnet" and builder.models.for_provider("codex") == "gpt-6-luna"
    tools = ToolIds()
    assert tools.words(builder.tools) == "Read, Grep, Glob, Edit, Write, Bash" and tools.is_known("run_tests") and not tools.is_known("crm") and tools.is_well_formed("crm"), "tool ids become the provider's words; an external system brings none"
    profile = builder.profile("Shared guidance.", tools.words(builder.tools))
    assert profile.profile_type == ProfileType.WORKER and scout.profile("", "Read").profile_type == ProfileType.SUBAGENT
    assert profile.body.startswith("Shared guidance.\n\nWork in small steps.") and "- the release" in profile.body, "the body is the domain's guidance, the Role's and its duties"
    for provider in (Claude(), Codex()):
        text = provider.profile_text(profile, builder.models.claude, builder.models.codex)
        assert "builder" in text and "Work in small steps." in text, f"{provider.name} renders the same Role"
