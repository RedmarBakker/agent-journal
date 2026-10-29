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


def loaded(app, tmp_path, **setup):
    from journal.features.organization.support.organization import Organization
    from tests.organization_fixture import OrganizationFixture
    from tests.user_settings import user_set
    fixture = OrganizationFixture(tmp_path / "organization").write()
    user_set(app, "workers.organization_folder", str(fixture.root))
    return fixture, app.container.get(Organization)


def test_the_loader_reads_the_domains_and_roles_the_folder_holds_and_ignores_what_is_not_one(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    contracts = organization.contracts()
    assert contracts.problems == () and [domain.id for domain in contracts.domains] == ["alpha", "beta"] and sorted(role.id for role in contracts.roles) == ["builder", "keeper", "scout"], "two domains and three Roles, the empty ghost folder ignored"
    builder = contracts.role("builder")
    assert builder.cardinality is Cardinality.MANY and builder.writes and builder.models.codex == "gpt-6-luna" and builder.skills == ("ids",) and builder.guidance == "Guidance of builder.\n" and builder.edges == (Edge(EdgeKind.DELEGATES_TO, "scout", "what to look up"),)
    assert contracts.cardinality_of("scout") is Cardinality.JOURNAL and contracts.role("keeper").needs_approval(ApprovalAction.CONTRACT_CHANGE) and contracts.domain("alpha").guidance == "Guidance of alpha.\n"
    graph = contracts.graph()
    assert [edge.declared for edge in graph].count(True) == 3 and any(edge.source == "plan" and edge.target == "domain:alpha" and not edge.declared for edge in graph), "containment edges and the three declared ones"
    fixture.domain("gamma", roles=["pilot"])
    fixture.role("gamma", "pilot")
    assert organization.contracts().role("pilot") is None and organization.reload().role("pilot").domain == "gamma", "a new domain and Role are seen after a reload with no code change"


import pytest


@pytest.mark.parametrize("domain, role, changes, rule, path", [
    ("alpha", "builder", {"writes": True, "tools": ["read_files", "edit_files"], "model": {"claude": "sonnet", "codex": {"model": "gpt-6.1-sol", "effort": "xhigh"}}}, "model", "domains/alpha/roles/builder/role.toml"),
    ("alpha", "scout", {"cardinality": "worktree"}, "cardinality", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"skills": ["Task-selected repository SKILL.md knowledge"]}, "skills", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"approval_required": ["fly_to_the_moon"]}, "approval", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"edges": [{"kind": "befriends", "to": "builder", "about": "x"}]}, "edge", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"edges": [{"kind": "delegates_to", "to": "ghostly", "about": "x"}]}, "edge", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"edges": [{"kind": "delegates_to", "to": "keeper", "about": "x"}]}, "edge", "domains/alpha/roles/scout/role.toml"),
    ("alpha", "scout", {"writes": True}, "tools", "domains/alpha/roles/scout/role.toml"),
])
def test_a_role_that_breaks_the_schema_is_left_out_and_reported_and_its_neighbours_are_kept(app, tmp_path, domain, role, changes, rule, path):
    fixture, organization = loaded(app, tmp_path)
    fixture.role(domain, role, **{"cardinality": "journal", "tools": ["read_files"], **changes})
    contracts = organization.reload()
    assert any(problem.rule == rule and problem.path == path for problem in contracts.problems), [(problem.rule, problem.path) for problem in contracts.problems]
    assert contracts.role(role) is None and contracts.role("keeper") is not None, "the file is left out whole, the others stay"


def test_a_domain_edge_to_an_unknown_domain_a_role_file_that_does_not_parse_and_a_role_folder_without_its_toml_are_reported(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    fixture.domain("beta", roles=["keeper"], edges=[{"kind": "escalates_to", "to": "nowhere", "about": "x"}])
    (fixture.root / "domains" / "alpha" / "roles" / "builder" / "role.toml").write_text("this is = = not toml")
    stray = fixture.root / "domains" / "alpha" / "roles" / "stray"
    stray.mkdir()
    (stray / "AGENTS.md").write_text("no contract\n")
    found = {(problem.rule, problem.path) for problem in organization.reload().problems}
    assert ("edge", "domains/beta/domain.toml") in found and ("parse", "domains/alpha/roles/builder/role.toml") in found and ("role", "domains/alpha/roles/stray") in found


def test_no_folder_set_is_no_organization_and_a_folder_that_is_missing_is_one_problem(app, tmp_path):
    from journal.features.organization.support.organization import Organization
    from tests.user_settings import user_set
    organization = app.container.get(Organization)
    assert organization.reload().is_empty() and organization.contracts().problems == (), "an empty setting is no organization and no problem"
    user_set(app, "workers.organization_folder", str(tmp_path / "missing"))
    assert [problem.rule for problem in organization.reload().problems] == ["folder"]


def test_journal_organization_lists_the_roles_of_each_domain_with_their_cardinality(app, tmp_path):
    from journal.support.caller import Caller
    loaded(app, tmp_path)
    shown = app.console().run(["organization", "list"], Caller.agent("main", "s1", "claude")).text
    assert "domain alpha: Alpha" in shown and "  role builder: many, writes, claude sonnet, codex gpt-6-luna on max" in shown and "  role keeper: plan, does not write" in shown and "version " in shown
