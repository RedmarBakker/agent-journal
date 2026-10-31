from contextlib import nullcontext
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from threading import Lock
from types import SimpleNamespace
import tomllib

import pytest

from journal.config import Config
from journal.engine.agent_launcher import AgentLauncher
from journal.engine.support.settings import Settings
from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.events.bus import Bus
from journal.events.listener import Listener
from journal.events.rows.role_escalated import RoleEscalated
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.role_conduct import RoleConduct
from journal.features.organization.listeners.role_refusal_report import RoleRefusalReport
from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.approval_actions import ApprovalActions
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.caps import Caps
from journal.features.organization.support.edge import Edge
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.organization_data_reader import OrganizationDataReader
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.features.organization.support.role_escalation import RoleEscalation
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_models import RoleModels
from journal.features.organization.support import seat_runner as seat_runner_module
from journal.features.organization.support import seat_runtime as seat_runtime_module
from journal.features.organization.support.seat_runner import SeatJobIdentity, SeatRunner
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.rig_seats import RigSeats
from journal.features.organization.support.rig_specs import DENIED, RigSpecs
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.organization.support.tool_ids import ToolIds
from journal.features.organization.support.usage_ledger import UsageEstimate, UsageLedger, UsageReading
from journal.support.inner_repositories import InnerRepositories
from journal.features.tasks.states.ready import Ready
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.workers_data import WorkersData
from journal.features.workers.support.session_workers_data import SessionWorkersData
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.models.support.ref import Ref
from journal.models.agent import Agent
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.agents import Agents
from journal.repositories.domain_rows import DomainRows
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.scope import Scope
from journal.repositories.approvals import Approvals
from journal.repositories.questions import Questions
from journal.repositories.plans import Plans
from journal.repositories.tasks import PLAN_LINK, Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL, Caller
from journal.support.rejection import Rejection
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.providers.support.profile_type import ProfileType
from journal.providers.support.helper_setup import JOURNAL_ACTIVE
from journal.support.agent_token import AgentToken
from tests.test_features import booted, hook
from tests.in_process import posted
from tests.worker_dispatch import dispatched
from tests.test_engine import CLASSIFIER
from tests.user_settings import user_set


@pytest.fixture(scope="module")
def boot():
    return booted


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


def plan_contracts(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "planner", cardinality="plan", writes=True, tools=["read_files", "edit_files", "run_tests"], skills=["ids"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "planner"], skills=["ids"])
    return organization.reload()


def use_provider(app, monkeypatch, name):
    providers = app.container.get(RigSeats).providers
    for provider in providers.all():
        for marker in provider.inherited_markers:
            monkeypatch.delenv(marker, raising=False)
    for marker in providers.lookup(name).inherited_markers:
        monkeypatch.setenv(marker, "active-session")


def test_a_plan_rig_places_its_plan_agent_domain_agent_and_plan_roles_by_contract_containment(app, tmp_path):
    contracts = plan_contracts(app, tmp_path)
    seats = app.container.get(RigSeats)
    providers = seats.providers
    placed = seats.seats("plan-29", contracts, ("alpha",), providers.lookup("claude"))
    assert [(seat.qualified, seat.pod, seat.member, seat.model) for seat in placed] == [
        ("plan", "plan", "plan-agent", "opus"),
        ("domain:alpha", "alpha", "domain-agent", "sonnet"),
        ("role:alpha/planner", "alpha", "planner", "sonnet"),
    ], "journal and many Roles stay out of a plan rig"
    assert [(source.logical_id(), target.logical_id()) for source, target in seats.links(contracts, placed)] == [
        ("plan.plan-agent", "alpha.domain-agent"),
        ("alpha.domain-agent", "alpha.planner"),
    ], "the links come from the containment edges"
    codex = seats.seats("plan-29", contracts, ("alpha",), providers.lookup("codex"))
    assert [(seat.qualified, seat.model, seat.effort) for seat in codex] == [
        ("plan", "gpt-6.1-sol", "xhigh"),
        ("domain:alpha", "gpt-6.1-sol", "xhigh"),
        ("role:alpha/planner", "gpt-6-luna", "max"),
    ], "Codex seats use contract model and effort, with the configured plan selection"
    user_set(app, OrganizationOptions.DOMAIN_AGENT_MODEL_TIER.key, "lowest_allowed")
    user_set(app, WorkersOptions.ALLOWED_MODELS.key, ["claude domain-agent: haiku, sonnet"])
    lowest = seats.seats("plan-29", contracts, ("alpha",), providers.lookup("claude"))[1]
    assert (lowest.model, lowest.effort) == ("haiku", placed[1].effort), "the candidate picks the lowest user-allowed Domain model and retains the contract-selected reasoning effort"


def test_a_domain_pod_lead_routes_by_domain_rules_and_returns_role_reports_over_the_same_handoff(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "claude")
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "primary", cardinality="plan", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.role("alpha", "reviewer", cardinality="plan", writes=False, tools=["read_files"], model=fixture.model("opus", False))
    fixture.domain("alpha", roles=["scout", "builder", "primary", "reviewer"], routing=[
        {"when": "a feature task", "role": "primary", "then": ["reviewer"]},
    ])
    contracts = organization.reload()
    writer = app.container.get(RigSpecs)
    rig = f"plan-routing-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")

    path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
    spec = json.loads(path.read_text())
    members = {member["id"]: member for pod in spec["pods"] for member in pod["members"]}
    guidance = (path.parent / "agents" / "alpha-domain-agent" / "guidance" / "role.md").read_text()

    assert "You are the Domain agent for Alpha. Lead your pod's Roles and never write code." in guidance
    assert "After a Role responds, return its report to the Plan agent through the same delegation." in guidance
    assert "For a feature task, start with Role primary; for a real handoff, review, or approval, continue to Role reviewer." in guidance
    assert spec["edges"] == [{"kind": "delegates_to", "from": "plan.plan-agent", "to": "alpha.domain-agent"}]
    assert spec["pods"][1]["edges"] == [
        {"kind": "delegates_to", "from": "domain-agent", "to": "primary"},
        {"kind": "delegates_to", "from": "domain-agent", "to": "reviewer"},
    ], "a Role result follows the same Plan -> Domain -> Role delegation path back to the Plan agent"
    assert {"Edit", "Write"}.issubset(members["domain-agent"]["claude_permissions"]["deny"])
    assert "Edit" in members["primary"]["claude_permissions"]["allow"]
    assert "Write" in members["primary"]["claude_permissions"]["deny"]


def test_a_plan_rig_writes_openrig_specs_with_journal_hooks_skills_tokens_models_and_permissions(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "claude")
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    rig = f"plan-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
    spec = json.loads(path.read_text())
    members = {member["id"]: member for pod in spec["pods"] for member in pod["members"]}
    assert spec["version"] == "0.2" and [pod["id"] for pod in spec["pods"]] == ["plan", "alpha"]
    assert spec["edges"] == [{"kind": "delegates_to", "from": "plan.plan-agent", "to": "alpha.domain-agent"}]
    assert spec["pods"][1]["edges"] == [{"kind": "delegates_to", "from": "domain-agent", "to": "planner"}]
    planner = members["planner"]
    environment = planner["env"]
    assert planner["runtime"] == "claude-code" and planner["model"] == "sonnet" and environment[ACTOR] == "worker:29" and environment[ACTOR_TOKEN] == "token-alpha-planner"
    assert "effort" not in planner
    assert environment[AGENT_SHELL] == environment[JOURNAL_ACTIVE] == "1" and environment["JOURNAL_ENV"] == "main"
    assert environment["JOURNAL_ROOT"] == str(app.config.root)
    assert environment["PATH"].split(os.pathsep)[0] == str(app.config.home / "bin")
    assert planner["claude_permissions"]["deny"] == [*DENIED, "Write"]
    assert "Edit" not in planner["claude_permissions"]["deny"] and "Write" in planner["claude_permissions"]["deny"]
    assert "Bash(journal *)" in planner["claude_permissions"]["allow"]
    assert {"Edit", "Bash"}.issubset(planner["claude_permissions"]["allow"])
    assert all({"Bash(rig send *)", "Bash(rig queue *)"}.issubset(member["claude_permissions"]["deny"]) for member in members.values()), "every seat denies direct sends and all queue mutation verbs, including create, handoff and inbox-drop"
    domain = members["domain-agent"]
    assert {"Edit", "Write"}.issubset(domain["claude_permissions"]["deny"])
    journal_command = os.path.relpath(writer.command(), app.config.root)
    worker_rules = {
        f"Bash({command} worker {verb} *)"
        for command in ("journal", str(writer.command()), journal_command)
        for verb in ("send", "check", "merge")
    }
    assert worker_rules.issubset(domain["claude_permissions"]["allow"])
    scoped_commands = tuple(f"JOURNAL_ENV=* {command}" for command in ("journal", str(writer.command()), journal_command))
    scoped_rules = {
        f"Bash({command} {noun} *)"
        for command in scoped_commands
        for noun in ("task", "proof", "clock-out", "worker send", "worker check", "worker merge")
    }
    assert scoped_rules.issubset(domain["claude_permissions"]["allow"])
    assert {"Bash(rig send *)", "Bash(rig queue *)"}.issubset(domain["claude_permissions"]["deny"])
    assert path.stat().st_mode & 0o777 == 0o600, "the rig file holds worker tokens"

    seats = writer.seats.seats(rig, contracts, ("alpha",), writer.providers.lookup("claude"))
    domain_seat = next(seat for seat in seats if seat.member == "domain-agent")
    alpha_seats = tuple(seat for seat in seats if seat.pod == domain_seat.pod)
    links = writer.seats.links(contracts, seats)
    _, pod = writer.pod_fragment(rig, domain_seat.pod, alpha_seats, links, app.config.root, worker_for)
    pod_domain = next(member for member in pod["members"] if member["id"] == "domain-agent")
    assert worker_rules.issubset(pod_domain["claude_permissions"]["allow"]), "an incrementally added Domain pod keeps the Journal worker commands"
    assert {"Bash(rig send *)", "Bash(rig queue *)"}.issubset(pod_domain["claude_permissions"]["deny"]), "the incremental Domain pod keeps direct rig send and queue denied"

    agent = path.parent / "agents" / "alpha-planner"
    agent_spec = json.loads((agent / "agent.yaml").read_text())
    uses = agent_spec["profiles"]["default"]["uses"]
    assert agent_spec["version"] == "1.0" and {"ids", "journal"}.issubset(uses["skills"])
    assert agent_spec["defaults"]["runtime"] == "claude-code"
    assert uses["runtime_resources"] == ["journal-hooks"]
    assert agent_spec["resources"]["runtime_resources"] == [{"id": "journal-hooks", "path": "runtime/journal-hooks.json", "runtime": "claude-code", "type": "claude_settings_fragment"}]
    assert (agent / "skills" / "ids" / "SKILL.md").read_text() == "---\nname: ids\n---\nA skill.\n"
    hooks = json.loads((agent / "runtime" / "journal-hooks.json").read_text())["hooks"]
    assert "SessionStart" in hooks and "UserPromptSubmit" in hooks


def test_generated_claude_plan_domain_and_role_seats_allow_read_commands_without_prompts(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "claude")
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    rig = f"plan-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
    spec = json.loads(path.read_text())
    members = {member["id"]: member for pod in spec["pods"] for member in pod["members"]}
    read_commands = {
        "Bash(echo *)", "Bash(pwd)", "Bash(ls *)", "Bash(awk *)", "Bash(sed -n *)",
        "Bash(head *)", "Bash(tail *)", "Bash(grep *)", "Bash(wc *)", "Bash(cat *)",
    }
    journal_commands = tuple(dict.fromkeys(("journal", str(writer.command()), os.path.relpath(writer.command(), app.config.root))))
    scoped_journal_commands = {f"Bash(JOURNAL_ENV=* {command} *)" for command in journal_commands}
    shell_guidance = (
        "Run each journal command on its own. Do not combine it with curl, cd, a pipe, semicolon, &&, "
        "or another shell command. If needed, check this journal's health with "
        f"`{OrganizationSeatRouting.health_command}` as a separate command. Do not use curl for another URL."
    )
    file_guidance = (
        "Prefer the Read tool for files. Use awk, sed -n, head, tail, grep, wc, or cat only to read files in this mission. "
        "Use Edit for file changes only when this seat is allowed to write."
    )
    health_read = f"Bash({OrganizationSeatRouting.health_command})"

    for member_id in ("plan-agent", "domain-agent", "planner"):
        permissions = members[member_id]["claude_permissions"]
        assert members[member_id]["env"]["JOURNAL_PORT"] == writer.journal_port(), f"{member_id} targets this journal's health port"
        assert read_commands.issubset(permissions["allow"]), f"{member_id} can inspect its workspace without approval"
        assert scoped_journal_commands.issubset(permissions["allow"]), f"{member_id} can run its scoped journal without approval"
        assert health_read in permissions["allow"], f"{member_id} can read the local journal health endpoint without approval"
        assert "Bash(curl *)" not in permissions["allow"], f"{member_id} can curl only the local journal health endpoint"
        assert "Bash(tee *)" not in permissions["allow"] and "Bash(sed -i *)" not in permissions["allow"], f"{member_id} cannot use shell commands to write files"
        assert set(DENIED).issubset(permissions["deny"]), f"{member_id} still denies git and direct hub changes"
        if member_id == "planner":
            assert "Edit" in permissions["allow"] and "Write" in permissions["deny"], "a writing Role changes files with Edit only"
        else:
            assert {"Edit", "Write"}.issubset(permissions["deny"]), f"{member_id} cannot write files"
        agent = path.parent / "agents" / members[member_id]["agent_ref"].removeprefix("local:agents/")
        guidance = (agent / "guidance" / "role.md").read_text()
        spec = json.loads((agent / "agent.yaml").read_text())
        routing_skills = [
            agent / resource["path"] / "SKILL.md"
            for resource in spec["resources"]["skills"]
            if "organization-seat-routing" in resource["id"]
        ]
        assert file_guidance in guidance, f"{member_id} guidance does not prefer Read and keep shell use read-only"
        assert shell_guidance in guidance, f"{member_id} guidance does not keep journal commands separate"
        assert routing_skills and all(file_guidance in skill.read_text() for skill in routing_skills), (
            f"{member_id} routing skill does not prefer Read and keep shell use read-only"
        )
        assert routing_skills and all(shell_guidance in skill.read_text() for skill in routing_skills), (
            f"{member_id} routing skill does not keep journal commands separate"
        )


def test_a_worker_role_can_run_rig_and_detached_commands_without_git_or_hub_sends(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "claude")
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "builder", cardinality="plan", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["builder", "scout"])
    contracts = organization.reload()
    writer = app.container.get(RigSpecs)
    provider = writer.providers.lookup("claude")
    seat = next(seat for seat in writer.seats.seats("plan-worker-58", contracts, ("alpha",), provider) if seat.role == "builder")

    permissions = writer.permissions(provider, seat, app.config.root)

    assert {"Bash(rig context *)", "Bash(nohup *)", "Bash(journal *)"}.issubset(permissions["allow"]), "a Role worker can inspect its rig and run a detached journal server"
    assert "Bash" not in permissions["allow"], "command access stays limited to its task tools and the needed programs"
    assert {"Bash(git *)", "Bash(rig send *)", "Bash(rig queue *)"}.issubset(permissions["deny"]), "git and direct hub sends and queue changes remain refused"


def test_generated_member_bash_environment_prefers_its_project_journal_command(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "claude")
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    rig = f"plan-path-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    project_journal = tmp_path / "project" / ".journal" / "bin" / "journal"
    with monkeypatch.context() as patch:
        patch.setattr(writer, "command", lambda: project_journal)
        spec_path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
        shell_path_command = writer.shell_path_command()
    spec = json.loads(spec_path.read_text())
    planner = next(member for pod in spec["pods"] for member in pod["members"] if member["id"] == "planner")
    project_journal.parent.mkdir(parents=True, exist_ok=True)
    project_journal.write_text("#!/bin/sh\nprintf 'project-journal:%s\\n' \"$*\"\n")
    project_journal.chmod(0o700)

    global_bin = tmp_path / "global-bin"
    global_bin.mkdir()
    global_journal = global_bin / "journal"
    global_journal.write_text("#!/bin/sh\nprintf 'global-journal:%s\\n' \"$*\"\n")
    global_journal.chmod(0o700)
    seat_bin = tmp_path / "openrig-seat-bin"
    seat_bin.mkdir()
    seat_rig = seat_bin / "rig"
    seat_rig.write_text("#!/bin/sh\nexit 0\n")
    seat_rig.chmod(0o700)
    environment = {"PATH": os.pathsep.join((str(seat_bin), str(global_bin))), "BASH_ENV": planner["env"]["BASH_ENV"]}

    try:
        resolved = subprocess.run(["/bin/bash", "-c", "journal task show 117"], cwd=tmp_path, env=environment,
                                  capture_output=True, text=True, check=True)
    finally:
        project_journal.unlink()

    assert planner["env"]["PATH"].split(os.pathsep)[0] == str(project_journal.parent)
    assert planner["env"]["PROMPT_COMMAND"].endswith(shell_path_command)
    assert Path(planner["env"]["BASH_ENV"]).read_text().strip() == shell_path_command
    assert resolved.stdout.strip() == "project-journal:task show 117", "the member's noninteractive shell runs the generated project command over a global journal"


def test_generated_seat_keeps_its_plan_journal_root_through_the_project_command(app, tmp_path, monkeypatch):
    from journal.providers.support.helper_setup import HelperSetup
    from journal.support.project_command import ProjectCommand

    use_provider(app, monkeypatch, "claude")
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    main_root = tmp_path / "main checkout"
    plan_root = tmp_path / "isolated plan"
    shim = tmp_path / "journal shim.sh"
    shim.write_text('#!/bin/sh\nprintf "%s\\n" "$JOURNAL_ROOT"\n')
    command = ProjectCommand(main_root, shim).write()
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "plan-1")
    with monkeypatch.context() as patch:
        patch.setattr(writer, "command", lambda: command)
        patch.setattr(writer, "setup", HelperSetup(Config(plan_root, port=0), writer.providers))
        spec_path = writer.write("plan-1", contracts, ("alpha",), app.config.root, worker_for)
    spec = json.loads(spec_path.read_text())
    planner = next(member for pod in spec["pods"] for member in pod["members"] if member["id"] == "planner")
    environment = planner["env"]
    seat_environment = {name: environment[name] for name in ("JOURNAL_ROOT", "PATH", "BASH_ENV")}

    resolved = subprocess.run(["/bin/bash", "-c", "journal task show 117"], cwd=tmp_path, env=seat_environment,
                              capture_output=True, text=True, check=True)

    assert environment["JOURNAL_ENV"] == "plan-1"
    assert environment["JOURNAL_ROOT"] == str(plan_root) and environment["JOURNAL_ROOT"] != str(main_root)
    assert resolved.stdout.strip() == str(plan_root), "the generated seat's project command keeps its isolated plan journal root"


def test_journal_organization_audit_finds_a_planted_cross_pod_queue_transition(app, tmp_path, monkeypatch):
    from journal.support.caller import Caller

    use_provider(app, monkeypatch, "claude")
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "builder", cardinality="plan", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    contracts = organization.reload()
    rig = f"plan-audit-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    app.container.get(RigSpecs).write(rig, contracts, ("alpha", "beta"), app.config.root, worker_for)

    item = {"id": "88", "source": f"alpha-builder@{rig}", "destination": f"beta-keeper@{rig}", "state": "pending"}
    transition = {"qitemId": "88", "state": "created", "actorSession": f"alpha-builder@{rig}", "identityProvenance": {"kind": "seat"}}

    def run(_runtime, *arguments, check=True):
        if arguments == ("queue", "list", "--all", "--all-rigs", "--full", "--json"):
            return subprocess.CompletedProcess(["rig", *arguments], 0, json.dumps({"rows": [item]}), "")
        if arguments == ("telemetry", "transitions", "--start", "retained", "--json"):
            return subprocess.CompletedProcess(["rig", *arguments], 0, json.dumps({"rows": [], "page": {"hasMore": True, "nextCursor": "next"}}), "")
        if arguments == ("telemetry", "transitions", "--cursor", "next", "--json"):
            return subprocess.CompletedProcess(["rig", *arguments], 0, json.dumps({"rows": [transition], "page": {"hasMore": False}}), "")
        raise AssertionError(f"unexpected OpenRig command: {arguments}")

    monkeypatch.setattr(SeatRuntime, "run", run)
    shown = app.console().run(["organization", "audit"], Caller.agent("main", "s1", "claude")).text

    assert "hub-skipping queue item 88" in shown and "role:alpha/builder" in shown and "role:beta/keeper" in shown
    assert "alpha-builder@" in shown and "identity provenance" in shown and "seat" in shown


def test_a_plan_rig_uses_the_active_codex_contract_models_hooks_and_permissions(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "codex")
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    rig = f"plan-codex-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
    spec = json.loads(path.read_text())
    members = {member["id"]: member for pod in spec["pods"] for member in pod["members"]}
    planner = members["planner"]
    assert planner["runtime"] == "codex" and planner["model"] == "gpt-6-luna" and planner["effort"] == "max"
    assert planner["codex_permissions"] == {"sandbox": "workspace-write", "approval": "never", "network_access": True}
    assert "claude_permissions" not in planner
    for member in members.values():
        rules = Path(member["cwd"]) / ".codex" / "rules" / "journal-organization-route.rules"
        policy = rules.read_text()
        assert 'pattern = ["rig", "send"]' in policy
        assert 'pattern = ["rig", "queue", ["create", "handoff", "inbox-drop"]]' in policy
        assert policy.count('decision = "forbidden"') == 2
        assert '["rig", "queue", "create", "--rig", "plan-1"]' in policy
        assert '["rig", "queue", "handoff", "--rig", "plan-1"]' in policy
        assert '["rig", "queue", "inbox-drop", "--rig", "plan-1"]' in policy
        assert '["rig", "queue", "list", "--rig", "plan-1"]' in policy
    assert members["plan-agent"]["runtime"] == "codex" and members["plan-agent"]["model"] == "gpt-6.1-sol" and members["plan-agent"]["effort"] == "xhigh"
    assert members["plan-agent"]["codex_permissions"] == {"sandbox": "read-only", "approval": "never"}
    assert members["plan-agent"]["model"] == "gpt-6.1-sol" and members["plan-agent"]["effort"] == "xhigh"
    assert planner["env"][ACTOR_TOKEN] == "token-alpha-planner"
    assert planner["env"]["PATH"].split(os.pathsep)[0] == str(app.config.home / "bin")

    agent = path.parent / "agents" / "alpha-planner"
    agent_spec = json.loads((agent / "agent.yaml").read_text())
    assert agent_spec["defaults"]["runtime"] == "codex"
    assert agent_spec["profiles"]["default"]["uses"]["runtime_resources"] == ["journal-hooks"]
    assert agent_spec["resources"]["runtime_resources"] == [{"id": "journal-hooks", "path": "runtime/journal-hooks.toml", "runtime": "codex", "type": "codex_config_fragment"}]
    hooks = tomllib.loads((agent / "runtime" / "journal-hooks.toml").read_text())["hooks"]
    assert hooks["SessionStart"][0]["hooks"][0]["type"] == "command"
    provider_command = app.container.get(RigSeats).providers.lookup("codex").hook_command(app.config.root)
    assert hooks["PreToolUse"][0]["hooks"][0]["command"] == provider_command
    assert hooks["UserPromptSubmit"][0]["hooks"][0]["command"] == provider_command
    assert "hook.sh codex" in provider_command
    assert str(app.config.root) in provider_command
    assert "hook.sh codex" in hooks["PreToolUse"][0]["hooks"][0]["command"]
    assert str(app.config.root) in hooks["PreToolUse"][0]["hooks"][0]["command"]
    assert "hook.sh codex" in hooks["UserPromptSubmit"][0]["hooks"][0]["command"]


def test_a_plan_rig_selects_its_plan_model_from_the_configured_allowed_profile_and_effort(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "codex")
    user_set(app, OrganizationOptions.PLAN_PROFILE.key, "organization-plan-review")
    user_set(app, OrganizationOptions.PLAN_EFFORT.key, "xhigh")
    user_set(app, WorkersOptions.ALLOWED_MODELS.key, ["codex organization-plan-review: gpt-6-luna"])
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    rig = f"plan-restricted-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
    members = {member["id"]: member for pod in json.loads(path.read_text())["pods"] for member in pod["members"]}
    plan = members["plan-agent"]
    assert plan["runtime"] == "codex" and plan["model"] == "gpt-6-luna" and plan["effort"] == "xhigh"
    assert plan["codex_permissions"]["sandbox"] == "read-only"


def test_an_organization_plan_rig_starts_with_only_its_plan_seat_and_adds_the_first_used_domain_and_role(app, tmp_path, monkeypatch):
    contracts = plan_contracts(app, tmp_path)
    user_set(app, "plans.plan_agents", True)
    user_set(app, "workers.openrig_version", "0.7.6")
    calls = []

    def run(_runtime, *arguments, check=True):
        calls.append(arguments)
        output = "rig version 0.7.6\n" if arguments == ("--version",) else "{}"
        return subprocess.CompletedProcess(["rig", *arguments], 0, output, "")

    monkeypatch.setattr(SeatRuntime, "run", run)
    agent, user = Caller.agent("main", "s1", "claude"), Caller.user("main")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    plan_id = int(console.run(["plan", "create", "the floors", "--brief", "the floors are laid"], user).text.split()[1].rstrip(":"))
    console.run(["plan", "add", str(plan_id), "lay the first boards", "--brief", "write the floor"], user)
    console.run(["plan", "mode", str(plan_id), "organization"], user)
    assert console.run(["plan", "approve", str(plan_id)], user).code == 0
    assert console.run(["plan", "start", str(plan_id)], user).code == 0
    app.runtime().deferred.drain()

    path = app.config.home / "runtime" / "rigs" / f"plan-{plan_id}" / "rig.yaml"
    initial = json.loads(path.read_text())
    assert [(pod["id"], [member["id"] for member in pod["members"]]) for pod in initial["pods"]] == [("plan", ["plan-agent"])], "starting an organization plan launches no unused Domain or Role seats"
    assert any(call[0] == "up" for call in calls), "the Plan-only spec starts the plan's rig"
    before_first_job = len(calls)

    environment = app.container.get(Environments).existing(f"plan-{plan_id}")
    with app.container.get(Scope).environment(environment.row_id):
        worker = app.container.get(Workers).save(Worker(
            environment_id=environment.row_id, name="Ada Lovelace", brief="write the floor",
            role="planner", contract=contracts.version, plan_id=plan_id, provider="claude", model="sonnet",
        ), Actor.system())
        seat = app.container.get(SeatRunner).member(worker)

    grown = json.loads(path.read_text())
    pods = {pod["id"]: pod for pod in grown["pods"]}
    assert seat.logical_id == "alpha.planner" and any(call[0] == "expand" for call in calls[before_first_job:]), "the first Role job adds its Domain pod through OpenRig"
    placement = calls[before_first_job:]
    expanded = next(index for index, call in enumerate(placement) if call[0] == "expand")
    launches = [call[2] for call in placement if call[:2] == ("seat", "launch")]
    assert expanded < next(index for index, call in enumerate(placement) if call[:2] == ("seat", "launch"))
    assert launches[:2] == [f"alpha-domain-agent@plan-{plan_id}", f"alpha-planner@plan-{plan_id}"], "every newly expanded member is relaunched from its saved environment"
    assert {pod: [member["id"] for member in value["members"]] for pod, value in pods.items()} == {
        "plan": ["plan-agent"], "alpha": ["domain-agent", "planner"],
    }, "the used Domain and Role appear, while the other Domain and unassigned Roles stay out"
    assert grown["edges"] == [{"kind": "delegates_to", "from": "plan.plan-agent", "to": "alpha.domain-agent"}]


def test_journal_roles_from_two_organization_plans_share_one_long_lived_rig_and_seat(app, tmp_path, monkeypatch):
    _fixture, organization = loaded(app, tmp_path)
    contracts = organization.reload()
    user_set(app, "workers.openrig_version", "0.7.6")
    calls = []

    def run(_runtime, *arguments, check=True):
        calls.append(arguments)
        output = "rig version 0.7.6\n" if arguments == ("--version",) else "{}"
        return subprocess.CompletedProcess(["rig", *arguments], 0, output, "")

    monkeypatch.setattr(SeatRuntime, "run", run)
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        plans, workers, runner = (app.container.get(kind) for kind in (Plans, Workers, SeatRunner))
        first_plan = plans.save(Plan(environment_id=1, title="First plan", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        second_plan = plans.save(Plan(environment_id=1, title="Second plan", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        worker = workers.save(Worker(environment_id=1, name="Ada Lovelace", role="scout", contract=contracts.version,
                                     plan_id=first_plan.id, provider="claude", model="opus"), actor)
        first = runner.member(worker)
        second = runner.member(workers.save(worker.with_(plan_id=second_plan.id), actor))
        spec = json.loads((app.config.home / "runtime" / "rigs" / "organization-1" / "rig.yaml").read_text())

    members = {member["id"] for pod in spec["pods"] for member in pod["members"]}
    assert first.rig == second.rig == "organization-1" and first.logical_id == second.logical_id == "alpha.scout", "both plans use the same shared Role seat"
    assert len([call for call in calls if call[0] == "up"]) == 1 and members == {"domain-agent", "scout"}, "the shared rig starts once and has no plan-specific Role copy"


def test_a_many_role_in_an_organization_plan_gets_its_own_rig_seat_and_worktree_then_drops_both_after_merge(app, tmp_path, monkeypatch):
    _fixture, organization = loaded(app, tmp_path)
    organization.reload()
    user_set(app, "plans.plan_agents", True)
    user_set(app, "workers.openrig_version", "0.7.6")
    root = app.config.root
    calls = []

    def run(_runtime, *arguments, check=True):
        calls.append(arguments)
        output = "rig version 0.7.6\n" if arguments == ("--version",) else "{}"
        return subprocess.CompletedProcess(["rig", *arguments], 0, output, "")

    monkeypatch.setattr(SeatRuntime, "run", run)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, _actor: self.seats.member(worker))

    def git(*arguments):
        return subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True, timeout=30)

    for arguments in (("init", "-q", "-b", "main"), ("config", "user.email", "test@example.com"), ("config", "user.name", "Test"),
                      ("commit", "-q", "--allow-empty", "-m", "start")):
        result = git(*arguments)
        assert result.returncode == 0, result.stderr

    agent, user = Caller.agent("main", "s1", "claude"), Caller.user("main")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    plan_id = int(console.run(["plan", "create", "the parser", "--brief", "the parser works"], user).text.split()[1].rstrip(":"))
    console.run(["plan", "add", str(plan_id), "prepare the parser", "--brief", "inspect the parser"], user)
    console.run(["plan", "add", str(plan_id), "build the parser", "--brief", "write the parser"], user)
    console.run(["plan", "mode", str(plan_id), "organization"], user)
    assert console.run(["plan", "approve", str(plan_id)], user).code == 0
    assert console.run(["plan", "start", str(plan_id)], user).code == 0
    app.runtime().deferred.drain()
    with app.container.get(Scope).environment(1):
        task = app.container.get(Plans).plan_tasks(app.container.get(Plans).find(plan_id))[1]
    dispatched = console.run(["worker", "dispatch", "Grace Hopper", "--task", str(task.id), "--changes", "the parser", "--tests", "Scoped tests", "--role", "builder"], agent)
    assert dispatched.code == 0, dispatched.error

    with app.container.get(Scope).environment(1):
        worker = app.container.get(Workers).find(1)
        branch = app.container.get(WorkerBranch)
        folder = branch.folder(worker)
        seat_id = f"builder-{worker.id}"
        spec_path = app.config.home / "runtime" / "rigs" / f"plan-{plan_id}" / "rig.yaml"
        placed = json.loads(spec_path.read_text())
        members = {member["id"]: member for pod in placed["pods"] for member in pod["members"]}
        assert worker.plan_id == plan_id and worker.worktree and folder.is_dir() and members[seat_id]["cwd"] == str(folder), "each planned many-cardinality Role gets a unique rig seat rooted in its own worktree without an extra flag"
        worker = app.container.get(Workers).save(worker.reported(1.0, 0), Actor.system())
        line = app.container.get(WorkerActions).merged_worktree_line(worker)
        after = json.loads(spec_path.read_text())
        remaining = {member["id"] for pod in after["pods"] for member in pod["members"]}
        assert "its worktree and branch are removed" in line and not folder.exists() and seat_id not in remaining, "the many Role's seat and clean worktree are retired on its merge path"
        assert any(call[0] == "remove" and call[2] == f"alpha.{seat_id}" for call in calls), "OpenRig removes the one-use seat after its job is merged"
    app.runtime().deferred.drain()


def test_a_codex_plan_rig_trusts_only_the_generated_journal_hooks(app, tmp_path, monkeypatch):
    use_provider(app, monkeypatch, "codex")
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config_path = codex_home / "config.toml"
    original_config = '[[hooks.SessionStart]]\nmatcher = ""\n[[hooks.SessionStart.hooks]]\ntype = "command"\ncommand = "echo unrelated"\n'
    config_path.write_text(original_config)
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    contracts = plan_contracts(app, tmp_path)
    writer = app.container.get(RigSpecs)
    rig = f"plan-codex-trusted-{tmp_path.name}"
    worker_for = lambda seat: SeatWorker(Actor.worker(29), AgentToken(f"token-{seat.agent()}"), "main")
    path = writer.write(rig, contracts, ("alpha",), app.config.root, worker_for)
    fragment = path.parent / "agents" / "alpha-planner" / "runtime" / "journal-hooks.toml"
    parsed = tomllib.loads(fragment.read_text())["hooks"]
    generated = {event: groups for event, groups in parsed.items() if event != "state"}
    state = parsed["state"]
    existing = tomllib.loads(config_path.read_text()).get("hooks", {})
    expected = {}
    commands = []
    for event, groups in generated.items():
        current_groups = existing.get(event, [])
        for group_offset, group in enumerate(groups):
            group_index = len(current_groups) + group_offset
            for handler_index, handler in enumerate(group["hooks"]):
                commands.append(handler["command"])
                normalized = {"type": "command", "command": handler["command"], "async": handler.get("async") is True}
                for name in ("timeout", "statusMessage", "additionalContextLimit"):
                    if handler.get(name) is not None:
                        normalized[name] = handler[name]
                identity = {"event_name": Codex.state_name(event), "hooks": [normalized]}
                if "matcher" in group and event not in ("UserPromptSubmit", "Stop", "Interrupt"):
                    identity["matcher"] = group["matcher"]
                serialized = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                digest = "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()
                key = f"{config_path.resolve()}:{Codex.state_name(event)}:{group_index}:{handler_index}"
                expected[key] = {"trusted_hash": digest}

    assert len(expected) == 9 and len(commands) == 9
    assert all("hook.sh codex" in command and str(app.config.root) in command for command in commands)
    assert all("additionalContextLimit" not in generated[event][0]["hooks"][0] for event in ("PreCompact", "SessionEnd", "SubagentStop", "Stop"))
    assert generated["SessionEnd"][0]["hooks"][0]["timeout"] == 3
    assert state == expected, "the member trusts each exact journal hook command and no unrelated command"
    assert all("echo unrelated" not in key for key in state)
    assert config_path.read_text() == original_config, "spec generation leaves the Codex configuration untouched"


def test_the_loader_reads_the_domains_and_roles_the_folder_holds_and_ignores_what_is_not_one(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    contracts = organization.contracts()
    assert contracts.problems == () and [domain.id for domain in contracts.domains] == ["alpha", "beta"] and sorted(role.id for role in contracts.roles) == ["builder", "keeper", "scout"], "two domains and three Roles, the empty ghost folder ignored"
    builder = contracts.role("builder")
    assert builder.cardinality is Cardinality.MANY and builder.writes and builder.models.codex == "gpt-6-luna" and builder.skills == ("ids",) and builder.guidance == "Guidance of builder.\n" and builder.edges == (Edge(EdgeKind.DELEGATES_TO, "scout", "what to look up"),)
    assert contracts.cardinality_of("scout") is Cardinality.JOURNAL and contracts.role("keeper").needs_approval(ApprovalAction.CONTRACT_CHANGE) and contracts.domain("alpha").guidance == "Guidance of alpha.\n"
    graph = contracts.graph()
    assert [edge.declared for edge in graph].count(True) == 2 and any(edge.source == "plan" and edge.target == "domain:alpha" and not edge.declared for edge in graph), "containment edges and the two declared ones"
    fixture.domain("gamma", roles=["pilot"])
    fixture.role("gamma", "pilot")
    assert organization.contracts().role("pilot") is None and organization.reload().role("pilot").domain == "gamma", "a new domain and Role are seen after a reload with no code change"


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
    user_set(app, "workers.organization_folder", "")
    organization = app.container.get(Organization)
    assert organization.reload().is_empty() and organization.contracts().problems == (), "an empty setting is no organization and no problem"
    user_set(app, "workers.organization_folder", str(tmp_path / "missing"))
    assert [problem.rule for problem in organization.reload().problems] == ["folder"]


def test_journal_organization_lists_the_roles_of_each_domain_with_their_cardinality(app, tmp_path):
    from journal.support.caller import Caller
    loaded(app, tmp_path)
    shown = app.console().run(["organization", "list"], Caller.agent("main", "s1", "claude")).text
    assert "domain alpha: Alpha" in shown and "  role builder: many, writes, claude sonnet, codex gpt-6-luna on max" in shown and "  role keeper: plan, does not write" in shown and "version " in shown


def test_writing_profiles_work_without_an_organization_and_while_plan_agents_are_off(app, tmp_path):
    agent = Caller.agent("main", "s1", "claude")
    user_set(app, "workers.organization_folder", "")
    user_set(app, "plans.plan_agents", False)
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    workers = app.container.get(Workers)
    no_role = dispatched(console, ["Ada Lovelace", "the job", "--changes", "the files of its task", "--role", "builder"], agent)
    assert (
        "Set organization folder + plans.plan_agents for --role; off:" in no_role.error
        and "--profile journal-medior" in no_role.error
        and "--profile journal-senior" in no_role.error
    ), "with no organization, journal asks for its generic writing profile"
    without_folder = dispatched(console, ["Ada Lovelace", "the job", "--changes", "the files of its task", "--profile", "journal-medior"], agent)
    with app.container.get(Scope).environment(1):
        medior = workers.scoped()[-1]
    assert without_folder.code == 0 and medior.profile == "journal-medior", "the shipped medior profile still dispatches without an organization folder"

    loaded(app, tmp_path)
    user_set(app, "plans.plan_agents", False)
    role_while_off = dispatched(console, ["Grace Hopper", "the job", "--changes", "the files of its task", "--role", "builder"], agent)
    assert (
        "Set organization folder + plans.plan_agents for --role; off:" in role_while_off.error
        and "--profile journal-medior" in role_while_off.error
        and "--profile journal-senior" in role_while_off.error
    ), "an organization folder by itself does not switch journal to Role dispatch"
    without_roles = dispatched(console, ["Grace Hopper", "the job", "--changes", "the files of its task", "--profile", "journal-senior"], agent)
    with app.container.get(Scope).environment(1):
        worker = workers.scoped()[-1]
    assert without_roles.code == 0 and worker.profile == "journal-senior" and not worker.role and not worker.contract, "the senior profile remains generic when an organization exists but Plan agents are off"


def test_a_domain_agent_can_dispatch_each_read_only_helper_profile(app, tmp_path):
    loaded(app, tmp_path)
    user_set(app, "plans.plan_agents", True)
    environment = app.container.get(Environments).lookup("domain-alpha")
    with app.container.get(Scope).environment(environment.row_id):
        domain_agent = app.container.get(Agents).save(Agent(environment_id=environment.row_id, session="domain-session", provider="claude", state="idle"), Actor.system())
        domains = app.container.get(DomainRows)
        domains.agent_linked("alpha", domain_agent, Actor.system())
        assert domains.agent_id("alpha") == domain_agent.id, "the agent session belongs to the alpha Domain"
    environment_header = {"X-Journal-Env": environment.name}
    status, answer = posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "domain-session"}, environment_header)
    assert status == 200, answer
    for profile in ("journal-researcher", "journal-planner", "journal-debugger", "journal-plan-reviewer"):
        tool_input = {"subagent_type": profile, "model": "sonnet", "description": f"read with {profile}", "prompt": "read the requested files"}
        status, answer = posted(app, "/hooks/claude", {"hook_event_name": "PreToolUse", "session_id": "domain-session", "tool_name": "Agent", "tool_input": tool_input}, environment_header)
        assert status == 200, f"the Domain agent may dispatch {profile}: {answer}"


def test_a_job_dispatched_to_a_role_starts_with_that_roles_and_its_domains_guidance_and_its_model(app, tmp_path, monkeypatch):
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    from journal.support.caller import Caller
    from tests.test_features import hook
    started = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture, organization = loaded(app, tmp_path)
    user_set(app, "plans.plan_agents", True)
    fixture.role("beta", "porter", cardinality="plan", writes=True, tools=["read_files", "edit_files"], skills=["ids"], model=fixture.model("sonnet", True))
    fixture.domain("beta", roles=["keeper", "porter"])
    organization.reload()
    agent = Caller.agent("main", "s1", "claude")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    refused = lambda *argv: dispatched(console, ["Ada Lovelace", "the job", "--changes", "the files of its task", *argv], agent)
    assert "--role" in refused().error, "a job names the Role it works as"
    assert "no Role" in refused("--role", "nobody").error and "does not write" in refused("--role", "scout").error, "an unknown Role and a Role that does not write are refused"
    assert "writing work uses the organization's Role" in refused("--profile", "journal-medior").error, "with Plan agents and an organization folder on, a writing job cannot fall back to a profile"
    sent = refused("--role", "porter", "--provider", "claude")
    assert sent.code == 0, sent.error
    [worker] = started
    assert worker.model == "sonnet" and worker.profile is None, "the Role's model for the provider, and no profile"
    assert worker.role == "porter" and worker.contract == organization.contracts().version, "the worker records its Role and the version of the contracts it began on"
    instructions = app.container.get(WorkerRunner).instructed(worker)
    assert "Guidance of beta." in instructions and "Guidance of porter." in instructions and "Read these skills before you work: ids." in instructions and "the job" in instructions, "the domain's and the Role's guidance, its skills and the job"


def test_a_worker_dispatched_to_a_role_is_refused_a_write_without_a_write_tool_and_an_approval_required_action_waits_for_the_user(app, tmp_path):
    from pathlib import Path
    from journal.engine.support.settings import Settings
    from journal.events.agent.tool_starting import ToolStarting
    from journal.events.feature_data import FeatureData
    from journal.features.organization.organization_nudges import OrganizationNudges
    from journal.features.organization.role_conduct import RoleConduct
    from journal.features.organization.support.organization_data import OrganizationData
    from journal.features.tasks.states.ready import Ready
    from journal.features.workers.support.workers_data import WorkersData
    from journal.models.worker import Worker
    from tests.test_engine import CLASSIFIER
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files"], approval_required=["production_deployment"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()

    def asked(role: str, tool: str, arguments: dict):
        worker = Worker(environment_id=1, name="Ada Lovelace", brief="b", role=role, session="role-session")
        call = Claude().call(tool, arguments, frozenset(), CLASSIFIER)
        data = FeatureData({"workers": WorkersData((), (), 0, (), Path("/w"), ()), "session_workers": SessionWorkersData((worker,) if role else ()), "organization": OrganizationData(contracts)})
        agent = Agent(environment_id=1, session=worker.session, provider="claude")
        event = ToolStarting(agent=agent, session=worker.session, environment_id=1, call=call).with_data(data)
        return RoleConduct.on_tool_starting(Ready(), event, Settings({}))

    assert asked("scout", "Write", {"file_path": "a.py", "content": "x"}).refusal == OrganizationNudges.ROLE_WRITES_NOTHING.create(role="scout"), "a Role without a write tool is refused a write"
    assert asked("builder", "Write", {"file_path": "a.py", "content": "x"}).refusal is None and asked("scout", "Read", {"file_path": "a.py"}).refusal is None, "a Role with one writes, and reading is not writing"
    assert asked("deployer", "Bash", {"command": "gh workflow run deploy.yml"}).refusal == OrganizationNudges.ACTION_WAITS_FOR_USER.create(action="production_deployment"), "an approval-required action waits for the user"
    assert asked("builder", "Bash", {"command": "gh workflow run deploy.yml"}).refusal is None, "an action the Role does not list is not held"
    assert asked("", "Write", {"file_path": "a.py", "content": "x"}).refusal is None and asked("ghost", "Write", {"file_path": "a.py", "content": "x"}).refusal is None, "a worker with no Role, or one the folder no longer holds, is let through"


def test_each_contract_approval_id_is_recognized_from_a_command_and_a_tool():
    for action in ApprovalAction:
        tool = Claude().call(f"mcp__organization__{action.value}", {"action_id": action.value}, frozenset(), CLASSIFIER)
        assert ApprovalActions.of(f"journal role action --approval {action.value}") == (action,)
        assert ApprovalActions.of(tool) == (action,), action.value


def test_an_approved_role_deployment_runs_once_and_a_refusal_stays_refused(app, tmp_path, monkeypatch):
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files"], approval_required=["production_deployment", "financial_transaction", "contract_change", "security_decision"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()
    actor = Actor.user(1)
    scope = app.container.get(Scope)
    with scope.environment(1):
        worker = app.container.get(Workers).save(Worker(name="Ada Lovelace", brief="deploy", session="worker-session", role="deployer", contract=contracts.version), actor)
        tasks = app.container.get(Tasks)
        task = tasks.save(Task(title="release", state=TaskState.STARTED), actor)
        tasks.handover(task, Ref.build(worker), actor)
    approvals = app.container.get(RoleApprovals)
    organization_data = app.container.get(OrganizationDataReader).read(Agent(environment_id=worker.environment_id, session=worker.session))

    def call_for(command: str):
        return Claude().call("Bash", {"command": command}, frozenset(), CLASSIFIER)

    def attempt(command: str):
        data = FeatureData({
            "workers": WorkersData((), (), 0, (), Path("/w"), ()),
            "session_workers": SessionWorkersData((worker,)),
            "organization": organization_data,
        })
        agent = Agent(environment_id=worker.environment_id, session=worker.session, provider=worker.provider)
        event = ToolStarting(agent=agent, session=worker.session, environment_id=worker.environment_id, call=call_for(command)).with_data(data)
        return RoleConduct.on_tool_starting(Ready(), event, Settings({}))

    def approval_for(command: str, action: ApprovalAction):
        request_hash, _ = ApprovalActions.identity(call_for(command))
        return app.container.get(Approvals).for_action(Actor.agent(worker.session).stamp, worker.role, worker.plan_id, task.row_id, action.value, request_hash)

    deployment = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.PRODUCTION_DEPLOYMENT.value)
    assert attempt("make deploy").refusal == deployment, "the deployment waits before any approval"
    listener = app.container.get(RoleRefusalReport)
    refusal = LineDelivered(agent=Agent(environment_id=worker.environment_id, session=worker.session, provider=worker.provider), session=worker.session, environment_id=worker.environment_id, nudge=OrganizationNudges.ACTION_WAITS_FOR_USER.key, values={"action": ApprovalAction.PRODUCTION_DEPLOYMENT.value})
    with monkeypatch.context() as patch:
        patch.setattr(listener.escalation, "report", lambda *args: None)
        with scope.environment(1):
            listener.handle(refusal)
    approved = approval_for("make deploy", ApprovalAction.PRODUCTION_DEPLOYMENT)
    assert approved and (approved.actor, approved.role, approved.task_id, approved.action) == (Actor.agent(worker.session).stamp, "deployer", task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT)
    assert approved.expires_at is not None and approved.question_id > 0, "the saved request names its answer question and expiry"
    approved = approvals.approve(approved, actor)
    assert approved.updater == actor and approved.decision == approved.APPROVED, "the user's decision is durable"
    assert attempt("make deploy && wire transfer").refusal == deployment, "one approval cannot release a call that carries a second required action"
    assert attempt("make deploy").refusal is None, "the approved deployment passes once"
    assert attempt("make deploy").refusal == deployment, "the same approval is spent after one pass"

    transfer = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.FINANCIAL_TRANSACTION.value)
    assert attempt("wire transfer").refusal == transfer, "a separate approval action waits"
    refused = approval_for("wire transfer", ApprovalAction.FINANCIAL_TRANSACTION)
    refused = approvals.refuse(refused, actor)
    assert attempt("wire transfer").refusal == transfer, "a refusal never lets the action through"
    assert approval_for("wire transfer", ApprovalAction.FINANCIAL_TRANSACTION).row_id == refused.row_id, "a refused exact request stays current instead of opening another question"

    contract_change = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.CONTRACT_CHANGE.value)
    assert attempt("amend contract").refusal == contract_change, "a contract change creates its first request"
    expired = approval_for("amend contract", ApprovalAction.CONTRACT_CHANGE)
    expired = app.container.get(Approvals).save(expired.with_(expires_at=expired.expires_at - timedelta(hours=2)), actor)
    assert attempt("amend contract").refusal == contract_change, "an expired approval cannot authorize a call"
    replacement = approval_for("amend contract", ApprovalAction.CONTRACT_CHANGE)
    with scope.environment(expired.question_environment_id):
        question = app.container.get(Questions).find(expired.question_id)
    assert app.container.get(Approvals).find(expired.row_id).decision == expired.EXPIRED and question.is_closed(), "expiry settles the approval and closes its question"
    assert replacement.row_id != expired.row_id and replacement.decision == replacement.PENDING, "the same exact request gets a fresh current approval after expiry"
    assert app.container.get(Approvals).for_action(Actor.agent(worker.session).stamp, worker.role, worker.plan_id, task.row_id, ApprovalAction.CONTRACT_CHANGE.value, replacement.request_hash).row_id == replacement.row_id, "lookup selects the replacement request"
    replacement = approvals.approve(replacement, actor)
    assert replacement.decision == replacement.APPROVED and attempt("amend contract").refusal is None, "the approved replacement passes once"
    assert attempt("amend contract").refusal == contract_change, "the approved replacement cannot pass a second time"

    assert attempt("grant access").refusal == OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.SECURITY_DECISION.value)
    security = approval_for("grant access", ApprovalAction.SECURITY_DECISION)
    with scope.environment(security.question_environment_id):
        question = app.container.get(Questions).find(security.question_id)
        approvals.answering.answer(question, "yes", Actor.agent(worker.session))
    security_wait = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.SECURITY_DECISION.value)
    assert attempt("grant access").refusal == security_wait, "an agent's positive question answer cannot approve its own action"
    assert app.container.get(Approvals).find(security.row_id).decision == security.REFUSED, "the non-user answer is recorded as refused"


def test_an_approval_is_bound_to_the_exact_tool_arguments_target_and_full_command(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files"], approval_required=["production_deployment"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()
    actor = Actor.user(1)
    scope = app.container.get(Scope)
    with scope.environment(1):
        worker = app.container.get(Workers).save(Worker(name="Ada Lovelace", brief="deploy", session="bound-worker", role="deployer", contract=contracts.version), actor)
        tasks = app.container.get(Tasks)
        task = tasks.save(Task(title="release", state=TaskState.STARTED), actor)
        tasks.handover(task, Ref.build(worker), actor)
    approvals = app.container.get(RoleApprovals)
    repository = app.container.get(Approvals)
    questions = app.container.get(Questions)
    organization_data = app.container.get(OrganizationDataReader).read(Agent(environment_id=worker.environment_id, session=worker.session))
    data = FeatureData({"workers": WorkersData((), (), 0, (), Path("/w"), ()), "session_workers": SessionWorkersData((worker,)), "organization": organization_data})

    def call_for(tool: str, target: str):
        return Claude().call(tool, {"target": target}, frozenset(), CLASSIFIER)

    def attempt(call):
        agent = Agent(environment_id=worker.environment_id, session=worker.session, provider=worker.provider)
        event = ToolStarting(agent=agent, session=worker.session, environment_id=worker.environment_id, call=call).with_data(data)
        return RoleConduct.on_tool_starting(Ready(), event, Settings({}))

    def approval_for(call):
        request_hash, _ = ApprovalActions.identity(call)
        return repository.for_action(Actor.agent(worker.session).stamp, worker.role, worker.plan_id, task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT.value, request_hash)

    original = call_for("mcp__release__production_deployment", "production")
    altered_target = call_for("mcp__release__production_deployment", "staging")
    altered_tool = call_for("mcp__release_v2__production_deployment", "production")
    waits = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.PRODUCTION_DEPLOYMENT.value)
    assert attempt(original).refusal == waits, "a tool request waits for a user decision"
    approved = approval_for(original)
    assert approved.request_hash and '"target": "production"' in approved.request_details, "the saved grant names its exact normalized arguments and target"
    with scope.environment(approved.question_environment_id):
        question = questions.find(approved.question_id)
    assert "mcp__release__production_deployment" in question.text and '"target": "production"' in question.text, "the question gives the user the tool and target being approved"
    approvals.approve(approved, actor)
    assert attempt(altered_target).refusal == waits and attempt(altered_tool).refusal == waits, "an altered target or tool name cannot use the grant"
    assert approval_for(altered_target).row_id != approved.row_id and approval_for(altered_tool).row_id != approved.row_id, "each altered request has its own pending grant"
    assert attempt(original).refusal is None and attempt(original).refusal == waits, "the exact approved call passes once and then is refused"

    command = Claude().call("Bash", {"command": "make deploy"}, frozenset(), CLASSIFIER)
    appended = Claude().call("Bash", {"command": "make deploy && make deploy"}, frozenset(), CLASSIFIER)
    command_hash, _ = ApprovalActions.identity(command)
    appended_hash, appended_details = ApprovalActions.identity(appended)
    assert ApprovalActions.of(appended) == (ApprovalAction.PRODUCTION_DEPLOYMENT,), "both operations belong to one approval category"
    assert appended.command == "make deploy && make deploy" and appended_hash != command_hash and "make deploy && make deploy" in appended_details, "normalization retains the full appended operation in the identity and user details"
    assert attempt(command).refusal == waits, "the single deployment command asks for its own approval"
    approved_command = approval_for(command)
    approvals.approve(approved_command, actor)
    assert attempt(appended).refusal == waits, "a second same-category operation cannot use the single-command grant"
    assert approval_for(appended).request_hash == appended_hash and approval_for(appended).row_id != approved_command.row_id, "the appended command has a distinct pending request"
    assert attempt(command).refusal is None and attempt(command).refusal == waits, "the old grant remains available for one exact single-command run"


def test_a_solo_role_rejects_an_excluded_mcp_tool_without_spending_approval_and_allows_its_tool_once(app, tmp_path):
    from journal.features.organization.states.role_work import RoleWork
    from journal.features.plans.plans_part import PlansPart
    from journal.features.plans.support.plans_data import PlansData
    from journal.features.plans.support.started_plan import StartedPlan
    from journal.features.organization.support.role_approvals import RoleApprovalContext

    fixture, organization = loaded(app, tmp_path)
    fixture.role("alpha", "deployer", writes=True, tools=["read_files", "edit_files", "run_tests"], approval_required=["production_deployment"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "deployer"])
    contracts = organization.reload()
    scope = app.container.get(Scope)
    with scope.environment(1):
        task = app.container.get(Tasks).save(Task(title="release", state=TaskState.STARTED), Actor.user(1))
    started = StartedPlan(plan_id=41, next_task=task.row_id, started_task=task.row_id, started_task_briefing="", recent_tasks=(task.row_id,), remaining_tasks=1,
                          checkpoint_pause=False, checkpoint_phase=0, testing="")
    data = FeatureData({"organization": app.container.get(OrganizationDataReader).read(Agent(environment_id=1, session="solo-plan")), PlansPart.name: PlansData(approved=(41,), started=started)})
    state = RoleWork(role="deployer", version=contracts.version)

    def attempt(call):
        event = ToolStarting(agent=Agent(environment_id=1, session="solo-plan", provider="claude"), session="solo-plan", environment_id=1, call=call).with_data(data)
        with scope.environment(1):
            return state.on_tool_starting(event, Settings({}))

    role = contracts.role("deployer")
    context = RoleApprovalContext("solo-plan", "deployer", 41, task.row_id, 1)
    approvals = app.container.get(RoleApprovals)
    repository = app.container.get(Approvals)
    waits = OrganizationNudges.ACTION_WAITS_FOR_USER.create(action=ApprovalAction.PRODUCTION_DEPLOYMENT.value)

    excluded = Claude().call("mcp__release__production_deployment", {"target": "production"}, frozenset(), CLASSIFIER)
    excluded_approval = approvals.request(context, ApprovalAction.PRODUCTION_DEPLOYMENT, excluded)
    assert excluded_approval and approvals.approve(excluded_approval, Actor.user(1)).decision == excluded_approval.APPROVED
    tool_refusal = OrganizationNudges.ROLE_TOOL_REFUSED.create(role=role.title, tool=excluded.tool, tools=ToolIds().words(role.tools))
    assert attempt(excluded).refusal == tool_refusal, "a user grant does not add an excluded MCP tool to a solo Role"
    excluded_hash, _ = ApprovalActions.identity(excluded)
    still_approved = repository.for_action(Actor.agent("solo-plan").stamp, "deployer", 41, task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT.value, excluded_hash)
    assert still_approved.decision == still_approved.APPROVED and still_approved.used_at is None, "tool refusal does not spend the grant"

    call = Claude().call("Bash", {"command": "make deploy"}, frozenset(), CLASSIFIER)
    assert attempt(call).refusal == waits, "a permitted tool still asks before running an approval-required action"
    request_hash, _ = ApprovalActions.identity(call)
    approved = repository.for_action(Actor.agent("solo-plan").stamp, "deployer", 41, task.row_id, ApprovalAction.PRODUCTION_DEPLOYMENT.value, request_hash)
    assert approved and approvals.approve(approved, Actor.user(1)).decision == approved.APPROVED
    assert attempt(call).refusal is None and attempt(call).refusal == waits, "the permitted tool consumes the approval on exactly one tool start"


def test_a_domain_carries_its_icon_and_its_boards_phase_names_and_a_board_with_another_key_is_refused(app, tmp_path):
    fixture, organization = loaded(app, tmp_path)
    assert organization.contracts().domain("alpha").icon == "🧪" and organization.contracts().domain("alpha").board.done == "Done", "a domain with no [board] has the plain phase names"
    fixture.domain("alpha", roles=["scout", "builder"], board={"in_progress": "Active", "done": "Completed"})
    board = organization.reload().domain("alpha").board
    assert (board.planned, board.in_progress, board.in_review, board.done) == ("Planned", "Active", "In review", "Completed"), "the names the domain gives, the plain ones for the rest"
    fixture.domain("alpha", roles=["scout", "builder"], board={"finished": "Closed", "done": ""})
    contracts = organization.reload()
    assert contracts.domain("alpha") is None and len([problem for problem in contracts.problems if problem.path == "domains/alpha/domain.toml"]) == 2, "an unknown phase and an empty name are each a problem and the domain is left out"


REAL_FOLDER = __import__("os").environ.get("JOURNAL_ORGANIZATION_FOLDER", "")
if not REAL_FOLDER:
    candidate = next((parent / "agentic-organization-journal" for parent in Path(__file__).resolve().parents if (parent / "agentic-organization-journal").is_dir()), None)
    REAL_FOLDER = str(candidate) if candidate else ""


@pytest.mark.skipif(not REAL_FOLDER, reason="No real agentic-organization folder is set or found beside the workspace")
def test_the_real_organization_folder_loads_domains_roles_and_many_plans(app):
    from collections import Counter
    from journal.features.organization.support.organization import Organization
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.support.actor import Actor
    from tests.in_process import get_answer
    from tests.user_settings import user_set
    user_set(app, "workers.organization_folder", REAL_FOLDER)
    contracts = app.container.get(Organization).reload()
    role_folders = [folder for domain in Path(REAL_FOLDER, "domains").iterdir() if (domain / "roles").is_dir() for folder in (domain / "roles").iterdir() if (folder / "role.toml").is_file()]
    known_problem = ("domains/engineering/roles/release-manager/role.toml", "skills", '"make-environment" is not the id of a skill; list the name of a skill folder')
    problems = [(problem.path, problem.rule, problem.message) for problem in contracts.problems]
    expected_counts = {Cardinality.JOURNAL: 23, Cardinality.PLAN: 18, Cardinality.MANY: 8} if problems else {Cardinality.JOURNAL: 24, Cardinality.PLAN: 18, Cardinality.MANY: 8}
    assert len(contracts.domains) == 13 and len(role_folders) == 50 and Counter(role.cardinality for role in contracts.roles) == expected_counts
    assert problems in ([], [known_problem]), "the real release-manager Role must reference a skill folder that exists"
    domain_id = contracts.domains[0].id
    plans, tasks, links, domains = (app.container.get(kind) for kind in (Plans, Tasks, Links, DomainRows))
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        for number in range(101):
            plan = plans.save(Plan(environment_id=1, title=f"Load plan {number + 1}"), actor)
            task = tasks.save(Task(environment_id=1, title=f"Load task {number + 1}"), actor)
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
            domains.task_tied(task, domain_id, actor)
    status, shown = get_answer(app, "/journal/organization", {"X-Journal-Env": "main"})
    visible_roles = sum(len(domain["roles"]) for domain in shown["domains"])
    assert status == 200 and Path(shown["folder"]).resolve() == Path(REAL_FOLDER).resolve() and len(shown["domains"]) == 13 and visible_roles == len(contracts.roles), "the viewer answer carries every valid Role from the real folder's 13 domains"
    loaded_domain = next(domain for domain in shown["domains"] if domain["id"] == domain_id)
    assert len(loaded_domain["plans"]) == 101 and all(len(plan["tasks"]) == 1 for plan in loaded_domain["plans"]), "the real organization board reads a large set of plans and their task progress"


def test_openrig_usage_estimates_are_native_session_deltas_and_subscription_windows_stay_separate(tmp_path):
    ledger = UsageLedger(Config.rooted(tmp_path), stale_after_seconds=60)
    assert ledger.estimate(3, 100).status == "missing" and ledger.estimate(3, 100).amount_usd is None
    assert ledger.estimate(4, 100, 2).coverage == "0 of 2 seats observed"
    first = ledger.observe(3, "builder@release", "native-a", 2.5, 100, 2)
    next_turn = ledger.observe(3, "builder@release", "native-a", 3.0, 110, 2)
    reset = ledger.observe(3, "builder@release", "native-a", 0.2, 120, 2)
    new_session = ledger.observe(3, "builder@release", "native-b", 0.4, 130, 2)
    assert first.amount_usd == 2.5 and next_turn.amount_usd == 3.0 and reset.amount_usd == 3.2 and new_session.amount_usd == 3.6
    assert new_session.source == "OpenRig native-session estimate" and new_session.coverage == "1 of 2 seats reported Estimated API cost" and new_session.freshness == "fresh" and new_session.status == "partial"
    ledger.observe(4, "older-seat", "native-c", 1.0, 100, 2)
    ledger.observe(4, "newer-seat", "native-d", 1.0, 190, 2)
    assert ledger.estimate(4, 200, 2).freshness == "stale", "one stale seat makes the plan estimate stale even if another seat is recent"
    ledger.record_subscription_limits({"five_hour": {"used_percentage": 40, "resets_at": 200}}, "Claude Code status line", "5h", 130)
    limits = ledger.subscription_limits(140)
    assert limits.status == "available" and limits.coverage == "account-wide subscription windows" and limits.limits["five_hour"]["used_percentage"] == 40
    ledger.record_subscription_limits(None, "Codex journal status files", "account-wide subscription windows", 150)
    missing_limits = ledger.subscription_limits(151)
    assert missing_limits.status == "missing" and missing_limits.freshness == "fresh" and missing_limits.source == "Codex journal status files"
    assert ledger.estimate(3, 1000).status == "stale" and ledger.subscription_limits(1000).status == "stale"


def test_plan_rig_cost_coverage_counts_plan_domain_and_role_agents(tmp_path):
    runtime = SeatRuntime(SimpleNamespace(home=tmp_path), SimpleNamespace())
    folder = runtime.spec_folder("plan-1")
    folder.mkdir(parents=True)
    (folder / "rig.yaml").write_text(json.dumps({"pods": [
        {"id": "plan", "members": [{"id": "plan-agent"}]},
        {"id": "engineering", "members": [{"id": "domain-agent"}, {"id": "builder", "role": "builder"}]},
    ]}))

    assert runtime.expected_seats("plan-1") == 3, "coverage includes the Plan, Domain and Role agent seats"


def test_openrig_075_cost_json_preserves_per_seat_estimate_metadata():
    payload = {"seats": [{
        "seatSession": "alpha-builder@release", "status": "reported", "kind": "claude",
        "source": "Claude statusline", "costUsd": 2.5,
        "window": {"nativeSessionId": "native-a", "since": "2026-10-29T10:00:00Z",
                   "asOf": "2026-10-29T10:01:00Z", "resets": 1},
        "coverage": "current native session", "stale": False, "ageSeconds": 3,
    }], "note": "current daemon only"}
    calls = []
    runtime = SeatRuntime(SimpleNamespace(), SimpleNamespace())
    runtime.run = lambda *args, **kwargs: calls.append((args, kwargs)) or subprocess.CompletedProcess(
        ["rig", *args], 0, json.dumps(payload), "")

    reading = runtime.usage_cost("alpha-builder@release")

    assert calls == [(('usage', 'cost', '--seat', 'alpha-builder@release', '--json'), {"check": False})]
    assert (reading.amount_usd, reading.source, reading.estimate_kind, reading.native_session_id) == (
        2.5, "Claude statusline", "claude", "native-a")
    assert reading.window == payload["seats"][0]["window"] and reading.coverage == "current native session"
    assert reading.freshness == "fresh" and reading.status == "estimated" and reading.sampled_at is not None


def test_organization_plan_agent_usage_is_recorded_from_its_rig_seat(tmp_path):
    from journal.features.plans.support.plan_agents import PlanAgents

    reading = UsageReading(0.37, "Claude statusline", "claude", "native-plan",
                           {"since": "window-a", "resets": 0, "asOf": 12.0},
                           "current native session", "fresh", "estimated", "reported", "", 12.0)
    runtime = SimpleNamespace(target=SeatRuntime.target, usage_cost=lambda _target: reading,
                              expected_seats=lambda _rig: 3)
    agents = object.__new__(PlanAgents)
    agents.agent = lambda _plan: SimpleNamespace(provider="claude", session="")
    agents.plans = SimpleNamespace(rig_id=lambda _plan: 8)
    agents.staffing = SimpleNamespace(find_rig=lambda _rig_id: SimpleNamespace(name="plan-4"), runtime=runtime)
    agents.usage = UsageLedger(Config.rooted(tmp_path))
    agents.time_source = SimpleNamespace(seconds=lambda: 12.0)
    plan = SimpleNamespace(id=4, mode=PlanMode.ORGANIZATION)

    agents.record_usage(plan)

    assert agents.usage.seat_estimates(4) == {"plan-plan-agent@plan-4": 0.37}, "the Plan agent's OpenRig session is included even when it has no provider session row"


def test_shared_role_usage_samples_its_domain_and_role_seats():
    from journal.features.organization.support.seat_runtime import SeatAddress

    runner = object.__new__(SeatRunner)
    addresses = (SeatAddress("engineering", "domain-agent"), SeatAddress("engineering", "builder"),
                 SeatAddress("support", "domain-agent"), SeatAddress("support", "reviewer"))
    runner.runtime = SimpleNamespace(roster=lambda _rig: addresses, target=SeatRuntime.target)

    assert runner.usage_targets(SimpleNamespace(rig="shared", pod="engineering", member="builder")) == (
        "engineering-domain-agent@shared", "engineering-builder@shared",
    ), "a shared Role estimate includes its Domain agent without attributing other shared seats to the plan"


def test_openrig_cost_json_keeps_unreported_cost_explicit():
    payload = {"seats": [{"seatSession": "alpha-builder@release", "status": "not_reported",
                          "kind": "codex", "reason": "Codex reports no cost", "tokens": {"input": 10}}],
               "note": "current daemon only"}
    runtime = SeatRuntime(SimpleNamespace(), SimpleNamespace())
    runtime.run = lambda *_args, **_kwargs: subprocess.CompletedProcess(
        ["rig", "usage", "cost"], 0, json.dumps(payload), "")

    reading = runtime.usage_cost("alpha-builder@release")

    assert reading.amount_usd is None and reading.status == "unavailable"
    assert reading.source_status == "not_reported" and reading.reason == "Codex reports no cost"


def test_openrig_ledger_retains_session_reset_and_unavailable_metadata(tmp_path):
    ledger = UsageLedger(Config.rooted(tmp_path), stale_after_seconds=60)

    def reading(amount, native_id, since, resets, as_of, freshness="fresh", status="estimated"):
        return UsageReading(amount, "Claude statusline", "claude", native_id,
                            {"since": since, "resets": resets, "asOf": as_of},
                            "current native session", freshness, status, "reported", "",
                            float(as_of))

    first = ledger.record(3, "alpha-builder@release", "worker-session-a",
                          reading(2.5, "native-a", "window-a", 0, 100), 100, 1)
    continued = ledger.record(3, "alpha-builder@release", "worker-session-a",
                              reading(3.0, "native-a", "window-a", 0, 110), 110, 1)
    reset = ledger.record(3, "alpha-builder@release", "worker-session-a",
                          reading(4.0, "native-a", "window-b", 1, 120), 120, 1)
    new_session = ledger.record(3, "alpha-builder@release", "worker-session-b",
                                reading(0.4, "native-b", "window-c", 0, 130), 130, 1)
    stale = ledger.record(3, "alpha-builder@release", "worker-session-b",
                          reading(0.6, "native-b", "window-c", 0, 140, "stale", "stale"), 140, 1)
    unavailable = ledger.record(3, "alpha-builder@release", "worker-session-b",
                                UsageReading(None, "OpenRig rig usage cost --json", "claude", "native-b", {},
                                             "not reported", "unavailable", "unavailable", "not_reported", "no sample"),
                                150, 1)
    persisted = json.loads(ledger.path.read_text())["seats"]["3:alpha-builder@release"]

    assert [first.amount_usd, continued.amount_usd, reset.amount_usd, new_session.amount_usd] == [2.5, 3.0, 7.0, 7.4]
    assert stale.amount_usd == pytest.approx(7.6) and stale.status == "stale"
    assert unavailable.amount_usd == pytest.approx(7.6) and unavailable.status == "unavailable" and unavailable.freshness == "unavailable"
    assert persisted["native_session_id"] == "native-b" and persisted["worker_native_session"] == "worker-session-b"
    assert persisted["latest"]["label"] == "Estimated API cost"
    assert persisted["last_estimate"]["source"] == "Claude statusline"
    assert persisted["reset_window"] == {"since": "window-c", "resets": 0, "asOf": 140.0}
    assert persisted["latest"]["source"] == "OpenRig rig usage cost --json"
    assert persisted["latest"]["estimate_kind"] == "claude" and persisted["latest"]["source_status"] == "not_reported"
    assert persisted["latest"]["coverage"] == "not reported" and persisted["latest"]["status"] == "unavailable"


def test_openrig_ledger_migrates_legacy_session_snapshot_without_double_counting(tmp_path):
    config = Config.rooted(tmp_path)
    ledger = UsageLedger(config)
    ledger.path.parent.mkdir(parents=True)
    ledger.path.write_text(json.dumps({"seats": {"3:seat": {
        "plan_id": 3, "seat": "seat", "native_session": "native-a", "native_total_usd": 3.0,
        "estimated_usd": 3.0, "first_seen": 100.0, "last_seen": 110.0, "source": "legacy harness",
    }}, "subscription_limits": None}))

    estimate = ledger.record(3, "seat", "worker-session", UsageReading(
        3.2, "Claude statusline", "claude", "native-a", {"since": "current", "resets": 0},
        "current native session", "fresh", "estimated", "reported", "", 120.0), 120.0, 1)

    assert estimate.amount_usd == 3.2, "the first structured snapshot continues the legacy cumulative baseline"


def test_over_budget_plan_pauses_after_recording_separate_subscription_limits(tmp_path):
    reading = UsageReading(5.0, "Claude statusline", "claude", "native-a",
                           {"since": "window-a", "resets": 0, "asOf": 10.0},
                           "current native session", "fresh", "estimated", "reported", "", 10.0)
    ledger = UsageLedger(Config.rooted(tmp_path))

    class Settings:
        @staticmethod
        def integer(_option):
            return 2

        @staticmethod
        def decimal(_option):
            return 5.0

    order, paused, stopped, notified = [], [], [], []
    plan = SimpleNamespace(state=PlanState.STARTED)
    windows = [SimpleNamespace(key="five_hour", used=40.0, resets_at=500.0, label="five hours")]
    runner = object.__new__(SeatRunner)
    addresses = (SimpleNamespace(pod="plan", member="plan-agent"),
                 SimpleNamespace(pod="engineering", member="domain-agent"),
                 SimpleNamespace(pod="engineering", member="builder"))
    runner.runtime = SimpleNamespace(usage_cost=lambda _target: reading, roster=lambda _rig: addresses,
                                     target=SeatRuntime.target, expected_seats=lambda _rig: 3,
                                     stop=lambda target, reason: (order.append("stop"), stopped.append((target, reason))))
    runner.ledger = ledger
    runner.caps = Caps(Settings())
    runner.plans = SimpleNamespace(find=lambda _plan_id: plan,
                                   agent_postponed=lambda current, _actor: (order.append("pause"), paused.append(current)))
    runner.escalation = SimpleNamespace(cap_reached=lambda *_args: (order.append("notify"), notified.append(_args)))
    runner.providers = SimpleNamespace(lookup=lambda _provider: SimpleNamespace(
        status=lambda _session, _home: SimpleNamespace(windows=windows)))
    runner.config = SimpleNamespace(status_home=tmp_path)
    worker = SimpleNamespace(plan_id=3, provider="claude")
    member = SimpleNamespace(target="alpha-builder@release", rig="release")

    with pytest.raises(Rejection, match="Estimated API cost"):
        runner.record_usage(worker, member, "worker-session", 20.0, Actor.system(), SimpleNamespace(plan_id=4))

    assert paused == [plan] and len(stopped) == 1 and stopped[0][0] == member.target
    assert order == ["notify", "pause", "stop"] and notified[0][1].startswith("the plan's Estimated API cost") and notified[0][-1] == 4
    assert "not money billed" in stopped[0][1]
    assert ledger.estimate(4, 20.0, 3).status == "estimated"
    assert set(ledger.seat_estimates(4)) == {
        "plan-plan-agent@release", "engineering-domain-agent@release", "engineering-builder@release",
    }, "the estimate includes Plan, Domain and Role seats"
    limits = ledger.subscription_limits(20.0)
    assert limits.status == "available" and limits.limits["five_hour"]["used_percentage"] == 40.0


def test_plan_cost_cap_notifies_plan_agent_and_user():
    worker = Worker(id=17, name="Ada", role="builder", plan_id=3, contract="contract-1",
                    environment_id=1, dispatcher="plan-session")
    role = SimpleNamespace(id="builder", domain="release")
    plan = SimpleNamespace(id=3)
    plan_agent = Agent(id=9, environment_id=2, session="plan-agent-session", provider="claude")
    links, cards = [], []
    escalation = RoleEscalation(
        SimpleNamespace(at=lambda _contract: SimpleNamespace(role=lambda _role: role)),
        SimpleNamespace(),
        SimpleNamespace(find=lambda _plan_id: plan, agent_id=lambda _plan: 9),
        SimpleNamespace(unended_agent=lambda _agent_id: plan_agent),
        SimpleNamespace(save=lambda link, actor: links.append((link, actor))),
        SimpleNamespace(show=lambda *args, **kwargs: cards.append((args, kwargs))),
    )

    escalation.cap_reached(worker, "the plan's Estimated API cost reached $5.00; this is an estimate, not money billed", Actor.system())

    assert len(links) == 1 and links[0][0].target.id == 9
    assert links[0][0].events[0].recipient == "plan-agent-session"
    assert "Estimated API cost reached $5.00" in links[0][0].events[0].report
    assert len(cards) == 1 and cards[0][0][2] == "Estimated API cost cap reached"
    assert "not money billed" in cards[0][0][3] and cards[0][0][1] == "plan-session"

    escalation.seat_cap_waiting(worker, "it will resume when a seat is free", Actor.system())

    assert len(links) == 2 and "paused at the shared OpenRig seat cap" in links[1][0].events[0].report
    assert len(cards) == 2 and cards[1][0][2] == "Shared OpenRig seat cap reached"


def test_seat_runner_notifies_when_a_shared_rig_seat_cap_pauses_staffing(monkeypatch):
    worker = Worker(id=17, name="Ada", provider="claude", model="sonnet", plan_id=3,
                    role="builder", contract="contract-1", environment_id=1)
    member = SimpleNamespace(openrig_version="0.7.5", provider="claude", model="sonnet")
    notifications = []
    runner = object.__new__(SeatRunner)
    runner.member = lambda _worker: member
    runner.runtime = SimpleNamespace(check_version=lambda _version: None, worker_token=lambda *_args: object())
    runner.environments = SimpleNamespace(find=lambda _environment_id: SimpleNamespace(name="plan-3"))
    runner.capacity_available = lambda _worker: False
    runner.current_job = lambda _identity: None
    runner.escalation = SimpleNamespace(seat_cap_waiting=lambda *args: notifications.append(args))
    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)

    runner.run(worker, SeatJobIdentity.from_worker(worker), Actor.system(), "do the work", lambda *_args: None)

    assert len(notifications) == 1
    assert notifications[0][0] == worker and "resume when a seat is free" in notifications[0][1]


def test_worker_caps_keep_account_seat_capacity_and_plan_estimates_distinct():
    class Settings:
        @staticmethod
        def integer(option):
            return 2

        @staticmethod
        def decimal(option):
            return 5.0

    caps = Caps(Settings())
    assert caps.seats(1).allowed and caps.seats(2).status == "full"
    assert "shared OpenRig seat cap" in caps.seats(2).reason
    missing = UsageEstimate(3, None, "OpenRig native-session estimate", None, None, "0 of unknown seats observed", "missing", "missing")
    over = UsageEstimate(3, 5.0, "OpenRig native-session estimate", 10, 20, "1 of 1 seats observed", "fresh", "estimated")
    partial = UsageEstimate(3, 4.0, "OpenRig native-session estimate", 10, 20, "1 of 2 seats observed", "fresh", "partial", 1, 2)
    partial_over = UsageEstimate(3, 6.0, "OpenRig native-session estimate", 10, 20, "1 of 2 seats observed", "fresh", "partial", 1, 2)
    stale_over = UsageEstimate(3, 6.0, "OpenRig native-session estimate", 10, 20, "1 of 1 seats observed", "stale", "stale", 1, 1)
    assert caps.plan_cost(missing).status == "unknown" and not caps.plan_cost(missing).allowed
    assert caps.plan_cost(over).status == "exceeded" and "Estimated API cost" in caps.plan_cost(over).reason and "not money billed" in caps.plan_cost(over).reason
    assert caps.plan_cost(partial).status == "unknown" and "1 of 2 seats" in caps.plan_cost(partial).reason
    assert caps.plan_cost(partial_over).status == "exceeded" and caps.plan_cost(stale_over).status == "exceeded"


def test_plan_cost_setting_names_estimated_api_cost_and_separates_subscription_billing():
    option = OrganizationOptions.COST_CAP

    assert option.title == "Estimated API cost cap per plan"
    assert "estimated API cost" in option.abstract
    assert "not money billed" in option.abstract and "share of your subscription" in option.abstract


def test_a_followup_codex_job_uses_the_existing_openrig_session_while_its_monitor_is_winding_down(monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace
    import threading
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.features.organization.support.seat_runtime import SeatSession
    from journal.models.worker import Worker
    from journal.support.actor import Actor
    from journal.support.agent_token import AgentToken

    class CapturedThread:
        def __init__(self, *, target, args, name, daemon):
            self.target, self.args, self.name, self.daemon = target, args, name, daemon
            threads.append(self)

        def start(self):
            pass

    threads = []
    monkeypatch.setattr(seat_runner_module.threading, "Thread", CapturedThread)
    prior_job = Worker(id=8, name="Ada Lovelace", role="builder", plan_id=8, contract="contract", provider="codex", model="gpt-6-luna", resume="thread-9", pid=0).moved("dispatched", 10)
    worker = prior_job.moved("sent a job", 20)
    runner = object.__new__(SeatRunner)
    role = SimpleNamespace(cardinality=Cardinality.PLAN, models=SimpleNamespace(for_provider=lambda _provider: "gpt-6-luna"))
    runner.organization = SimpleNamespace(at=lambda _contract: SimpleNamespace(role=lambda _role: role))
    runner.tasks = SimpleNamespace(holder_task=lambda _holder: None, ready_queue=lambda _holder: ())
    runner._guard = threading.Lock()
    runner._active = {worker.id}
    from journal.features.organization.support.seat_runner import SeatJobIdentity
    prior_identity = SeatJobIdentity.from_worker(prior_job)
    identity = SeatJobIdentity.from_worker(worker)
    runner._active_jobs = {worker.id: prior_identity}
    runner.start(worker, Actor.system(), "next job", lambda *args: None)

    assert len(threads) == 1 and threads[0].target == runner.send_existing and threads[0].args[1] == identity and threads[0].args[3] == "next job"

    member = SimpleNamespace(provider="codex", model="gpt-6-luna", openrig_version="0.7.5", target="alpha-builder@release")
    sent, saved = [], []
    runner.scope = SimpleNamespace(environment=lambda _environment: nullcontext())
    runner.member = lambda _worker: member
    runner.runtime = SimpleNamespace(
        check_version=lambda _version: "0.7.5",
        worker_token=lambda *_args: AgentToken("seat-token"),
        session=lambda _member, native: SeatSession(91, native, "running", 25),
        send=lambda _member, prompt: sent.append(prompt),
    )
    runner.environments = SimpleNamespace(find=lambda _environment: SimpleNamespace(name="development"))
    runner.workers = SimpleNamespace(find=lambda _row: worker, save=lambda current, _actor: saved.append(current) or current)
    runner.time_source = SimpleNamespace(seconds=lambda: 30)
    runner.monitor = lambda *args: None
    monkeypatch.setattr("journal.features.organization.support.seat_runner.ProcessCheck.is_running", lambda _pid: True)
    runner.send_existing(worker, identity, Actor.system(), "next job", lambda *args: None)

    assert sent == ["next job"] and saved[-1].pid == 91 and saved[-1].resume == "thread-9" and saved[-1].token_hash == AgentToken("seat-token").digest()


def test_a_codex_job_runs_on_its_selected_role_seat_and_saves_the_native_session(monkeypatch):
    from types import SimpleNamespace
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.features.organization.support.seat_runtime import SeatSession
    from journal.models.worker import Worker
    from journal.support.actor import Actor
    from journal.support.agent_token import AgentToken

    worker = Worker(id=9, name="Ada Lovelace", role="builder", plan_id=8, contract="contract", provider="codex", model="gpt-6-luna", resume="thread-9").moved("dispatched", 10)
    member = SimpleNamespace(provider="codex", model="gpt-6-luna", openrig_version="0.7.5", target="alpha-builder@release")
    sent, saved, monitored = [], [], []
    runner = object.__new__(SeatRunner)
    runner.member = lambda _worker: member
    runner.runtime = SimpleNamespace(
        check_version=lambda _version: "0.7.5",
        worker_token=lambda *_args: AgentToken("seat-token"),
        session=lambda _member, native: SeatSession(91, native, "running", 25),
        send=lambda _member, prompt: sent.append(prompt),
    )
    runner.environments = SimpleNamespace(find=lambda _environment: SimpleNamespace(name="development"))
    role = SimpleNamespace(cardinality=Cardinality.PLAN, models=SimpleNamespace(for_provider=lambda provider: "gpt-6-luna" if provider == "codex" else ""))
    runner.organization = SimpleNamespace(at=lambda _contract: SimpleNamespace(role=lambda _role: role))
    runner.capacity_available = lambda _worker: True
    runner.workers = SimpleNamespace(find=lambda _row: worker, save=lambda current, _actor: saved.append(current) or current)
    runner.time_source = SimpleNamespace(seconds=lambda: 30)
    runner.monitor = lambda *args: monitored.append(args)
    monkeypatch.setattr("journal.features.organization.support.seat_runner.ProcessCheck.is_running", lambda _pid: True)

    from journal.features.organization.support.seat_runner import SeatJobIdentity
    identity = SeatJobIdentity.from_worker(worker)
    runner.run(worker, identity, Actor.system(), "write the patch", lambda *args: None)

    assert sent == ["write the patch"] and saved[-1].pid == 91 and saved[-1].session == "thread-9" and saved[-1].resume == "thread-9"
    assert saved[-1].token_hash == AgentToken("seat-token").digest() and monitored[0][1] == identity and monitored[0][3] == "thread-9"


def test_seat_recovery_attaches_to_an_existing_process_without_launching_a_new_agent(monkeypatch):
    import threading
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.models.worker import Worker
    from journal.support.actor import Actor

    class CapturedThread:
        def __init__(self, *, target, args, name, daemon):
            self.target, self.args, self.name, self.daemon = target, args, name, daemon
            threads.append(self)

        def start(self):
            pass

    threads = []
    monkeypatch.setattr(seat_runner_module.threading, "Thread", CapturedThread)
    worker = Worker(id=10, name="Ada Lovelace", role="builder", plan_id=8, provider="codex", model="gpt-6-luna", pid=91, resume="thread-9").moved("dispatched", 10)
    runner = object.__new__(SeatRunner)
    runner._guard = threading.Lock()
    runner._active = set()
    runner._active_jobs = {}
    runner.recover(worker, Actor.system(), "do not resend this job", lambda *args: None)

    assert len(threads) == 1 and threads[0].target == runner.monitor_existing and threads[0].args[0] == worker


def test_seat_monitor_finishes_on_clockout_or_when_its_queue_item_is_done(monkeypatch):
    import threading
    from types import SimpleNamespace
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.support.actor import Actor

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)

    def monitored(current, holders, finished):
        runner = object.__new__(SeatRunner)
        runner._guard = threading.Lock()
        runner._finishing = set()
        runner.workers = SimpleNamespace(find=lambda _row: current)
        runner.tasks = SimpleNamespace(holder_task_ids=lambda _ref: holders, finished_task_ids=lambda _ref: finished)
        runner.time_source = SimpleNamespace(seconds=lambda: 20)
        usage = []
        runner.record_usage = lambda *args: usage.append(args)
        ended = []
        worker = Worker(id=11, name="Ada Lovelace", role="builder", plan_id=8, state=WorkerState.DISPATCHED, pid=91).moved("dispatched", 10)
        from journal.features.organization.support.seat_runner import SeatJobIdentity
        identity = SeatJobIdentity.from_worker(worker)
        runner.monitor(worker, identity, None, "thread-9", Actor.system(), lambda *args: ended.append(args), 10)
        return ended, usage

    dispatched = Worker(id=11, name="Ada Lovelace", state=WorkerState.DISPATCHED, pid=91).moved("dispatched", 10)
    clocked_out, clockout_usage = monitored(dispatched.reported(20, 1), (), ())
    queue_done, queue_usage = monitored(dispatched, (), (42,))

    assert len(clocked_out) == 1 and clockout_usage, "clockout ends the active job after recording usage"
    assert len(queue_done) == 1 and not queue_usage, "a finished queue item ends its seat job"


def test_old_seat_completion_cannot_finish_or_unmonitor_a_followup_generation(monkeypatch):
    from threading import Event, Lock, Thread
    from types import SimpleNamespace
    from journal.events.rows.worker_reused import WorkerReused
    from journal.features.organization.support import seat_runner as seat_runner_module
    from journal.features.organization.support.seat_runner import SeatJobIdentity, SeatRunner
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.models.worker import Worker
    from journal.support.actor import Actor

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    old = Worker(id=16, name="Ada Lovelace", pid=91).moved("dispatched", 10)
    old_identity = SeatJobIdentity.from_worker(old)
    followup = old.resumed("write the follow-up", 20, WorkerReused, "sent a job")
    followup_identity = SeatJobIdentity.from_worker(followup)
    current = old
    runner = object.__new__(SeatRunner)
    runner._guard = Lock()
    runner._active = {old.id}
    runner._active_jobs = {old.id: old_identity}
    runner._finishing = set()
    runner.workers = SimpleNamespace(find=lambda _row: current)
    runner.tasks = SimpleNamespace(holder_task_ids=lambda _ref: (), finished_task_ids=lambda _ref: (42,))
    runner.time_source = SimpleNamespace(seconds=lambda: 30)
    entered, resume, failures = Event(), Event(), []
    worker_runner = object.__new__(WorkerRunner)
    worker_runner._locks = {}
    worker_runner._locks_lock = Lock()
    worker_runner.workers = runner.workers
    worker_runner.seats = SimpleNamespace(preserve=lambda *_args: failures.append("stale preserve"))

    def old_completion(worker, identity, code, actor):
        entered.set()
        if not resume.wait(2):
            failures.append("completion was not resumed")
            return
        worker_runner.finish_seat(worker, identity, code, actor)

    def monitor_old_job():
        try:
            runner.monitor(old, old_identity, None, "thread-9", Actor.system(), old_completion, 10)
        except BaseException as failure:
            failures.append(str(failure))
        finally:
            runner.release(old_identity)

    monitor = Thread(target=monitor_old_job)
    monitor.start()
    assert entered.wait(2), "the old monitor reached its pending completion callback"
    current = followup
    with runner._guard:
        runner._active_jobs[old.id] = followup_identity
    resume.set()
    monitor.join(2)

    assert not monitor.is_alive() and not failures
    assert current == followup and current.brief == "write the follow-up"
    assert runner._active == {old.id} and runner._active_jobs[old.id] == followup_identity


def test_seat_monitor_requires_fresh_openrig_idle_evidence_after_job_start(monkeypatch):
    import threading
    from types import SimpleNamespace
    from journal.features.organization.support.seat_runner import SeatRunner
    from journal.features.organization.support.seat_runtime import SeatRuntime, SeatSession
    from journal.models.worker import Worker
    from journal.support.actor import Actor

    monkeypatch.setattr("journal.features.organization.support.seat_runner.ProcessCheck.is_running", lambda _pid: True)
    member = SimpleNamespace(provider="codex", model="gpt-6-luna", openrig_version="0.7.5", target="alpha-builder@release")

    def check(sampled_at):
        worker = Worker(id=17, name="Ada Lovelace", pid=91).moved("dispatched", 100)
        runner = object.__new__(SeatRunner)
        runner._guard = threading.Lock()
        runner._finishing = set()
        runner.workers = SimpleNamespace(find=lambda _row: worker)
        runner.settings = SimpleNamespace(decimal=lambda _option: 0)
        runner.time_source = SimpleNamespace(seconds=lambda: 120)
        runner.member = lambda _worker: member
        node_status = {"nodes": [{"name": member.target, "agentActivity": {
            "state": "idle", "reason": "no recent agent event", "evidenceSource": "native_hook",
            "sampledAt": sampled_at, "evidence": None,
        }}]}
        activity, updated = SeatRuntime.activity_status(node_status)
        runner.runtime = SimpleNamespace(
            session=lambda *_args: SeatSession(91, "thread-9", "running", updated, activity),
        )
        ended = []
        finished = runner.is_finished(worker, Actor.system(), lambda *args: ended.append(args))
        return finished, ended

    stale_finished, stale_callbacks = check("1970-01-01T00:01:39Z")
    fresh_finished, fresh_callbacks = check("1970-01-01T00:01:41Z")

    assert not stale_finished and not stale_callbacks, "idle evidence sampled before dispatch cannot end a delivered-late job"
    assert fresh_finished and len(fresh_callbacks) == 1, "a fresh idle sample can end a job after its grace period"


def test_seat_runtime_uses_the_existing_rig_spec_and_pinned_openrig_version(tmp_path, monkeypatch):
    config = Config.rooted(tmp_path)
    spec = config.home / "runtime" / "rigs" / "release" / "rig.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text(json.dumps({"pods": [{"id": "alpha", "members": [{
        "id": "builder", "agent_ref": "local:agents/alpha-builder", "runtime": "codex",
        "model": "gpt-6-luna", "env": {"JOURNAL_ACTOR": "worker:7", "JOURNAL_ACTOR_TOKEN": "seat-token",
        "JOURNAL_ENV": "development", "JOURNAL_ROOT": str(config.root), "PATH": str(config.home / "bin") + os.pathsep + "/usr/bin",
        "AGENT_JOURNAL_ACTIVE": "1", "JOURNAL_AGENT_SHELL": "1"},
        "codex_permissions": {"sandbox": "workspace-write", "approval": "never"},
    }]}]}))
    agent = spec.parent / "agents" / "alpha-builder"
    agent.mkdir(parents=True)
    (agent / "agent.yaml").write_text(json.dumps({"resources": {"runtime_resources": [{"id": "journal-hooks", "path": "runtime/journal-hooks.json", "runtime": "codex"}],
        "skills": [{"id": "journal", "path": "skills/journal"}]},
        "profiles": {"default": {"uses": {"skills": ["journal"]}}}}))
    (agent / "runtime").mkdir()
    (agent / "runtime" / "journal-hooks.json").write_text("{}")

    class Settings:
        @staticmethod
        def option(option):
            return "0.7.5" if option == OrganizationOptions.OPENRIG_VERSION else ""

    calls = []

    def execute(arguments, **kwargs):
        calls.append(arguments)
        if arguments[1:3] == ["seat", "status"]:
            return subprocess.CompletedProcess(arguments, 0, json.dumps({"session_status": "running"}), "")
        if arguments[1:2] == ["ps"]:
            return subprocess.CompletedProcess(arguments, 0, json.dumps([{
                "logicalId": "alpha.builder",
                "contextUsage": {"sessionId": "thread-9"},
                "identityVerdict": {"evidence": {"observedPid": 91}},
                "agentActivity": {"state": "running", "reason": "agent is working", "evidenceSource": "native_hook",
                                  "sampledAt": "2026-10-29T15:00:00Z", "evidence": None},
            }]), "")
        if arguments[1:] == ["--version"]:
            return subprocess.CompletedProcess(arguments, 0, "rig version 0.7.5\n", "")
        if arguments[1:2] == ["send"]:
            assert arguments == ["rig", "send", "alpha-builder@release", "write the patch", "--json"], "0.7.5 treats --rig as fan-out; a seat send has only the bare seat and text positionals"
            return subprocess.CompletedProcess(arguments, 0, "{}", "")
        return subprocess.CompletedProcess(arguments, 0, "{}", "")

    monkeypatch.setattr(shutil, "which", lambda program: "/usr/bin/rig")
    runtime = SeatRuntime(config, Settings(), execute)
    member = runtime.member("release", "alpha", "builder", "codex")
    token = runtime.worker_token(member, "codex", "gpt-6-luna", "worker:7", "development")
    assert (member.logical_id, member.target, member.provider, member.model, member.runtime) == ("alpha.builder", "alpha-builder@release", "codex", "gpt-6-luna", "codex")
    assert token.text == "seat-token"
    assert runtime.check_version() == "0.7.5"
    reason = "journal worker 7 starts a fresh context"
    runtime.launch(member, reason)
    assert calls[-1] == ["rig", "seat", "launch", member.target, "--fresh", "--stop", "--reason", reason,
                         "--operator", "journal", "--json"], "a fresh Role launch stops a stale live OpenRig seat"

    session = runtime.session(member)
    runtime.send(member, "write the patch")
    assert (session.pid, session.session, session.status) == (91, "thread-9", "running")
    assert session.activity_status == "running" and session.status_updated_at > 1_700_000_000
    assert ["rig", "ps", "--nodes", "--full", "--json", "--rig", "release"] in calls
    assert ["rig", "send", member.target, "write the patch", "--json"] in calls


@pytest.mark.parametrize(("rig_on_path", "installed", "expected"), [
    (False, "", "OpenRig's rig command is not on PATH"),
    (True, "", "could not read the installed OpenRig version"),
    (True, "0.7.4", "OpenRig is 0.7.4; workers.openrig_version requires 0.7.5"),
])
def test_boot_recovery_refuses_an_organization_seat_without_the_openrig_version_pinned_in_settings(app, tmp_path, monkeypatch, rig_on_path, installed, expected):
    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)

    class Settings:
        @staticmethod
        def option(option):
            return "0.7.5" if option == OrganizationOptions.OPENRIG_VERSION else ""

    calls, session_calls = [], []

    def execute(arguments, **_kwargs):
        calls.append(arguments)
        return subprocess.CompletedProcess(arguments, 0, f"rig version {installed}\n", "")

    monkeypatch.setattr(seat_runtime_module.shutil, "which", lambda _program: "/usr/bin/rig" if rig_on_path else None)
    runtime = SeatRuntime(SimpleNamespace(), Settings(), execute)
    runtime.session = lambda *_args: session_calls.append(True)
    member = SimpleNamespace(openrig_version="0.7.4", target="alpha-builder@release")
    runner = object.__new__(SeatRunner)
    identity = SeatJobIdentity.from_worker(worker)
    runner._guard = Lock()
    runner._finishing = set()
    runner._active = {worker.id}
    runner._active_jobs = {worker.id: identity}
    runner.workers = workers
    runner.runtime = runtime
    runner.config = SimpleNamespace(home=tmp_path)
    runner.scope = app.container.get(Scope)
    runner.member = lambda _worker: member

    runner.monitor_existing(worker, identity, actor, finisher.finish_seat)
    app.runtime().deferred.drain()

    with app.container.get(Scope).environment(worker.environment_id):
        current = workers.find(worker.row_id)
    assert current.run_end.startswith(f"seat failed: {expected}"), "boot recovery leaves a clear failure on the organization job"
    assert len(escalated) == 1 and expected in escalated[0][1], "the Domain agent receives the version refusal"
    assert session_calls == [] and not runner._active, "recovery refuses before attaching to a session and releases its monitor"
    assert calls == ([["rig", "--version"]] if rig_on_path else [])


@pytest.mark.parametrize(("rig_on_path", "installed"), [(False, ""), (True, "0.7.4")])
def test_a_solo_plan_agent_starts_when_openrig_is_missing_or_wrong(app, monkeypatch, rig_on_path, installed):
    launches = []
    monkeypatch.setattr(AgentLauncher, "start_in_worktree", lambda _self, environment, provider, resume, repositories=None: launches.append((environment, provider, resume)))
    which = shutil.which
    monkeypatch.setattr(seat_runtime_module.shutil, "which", lambda program, *args, **kwargs: ("/usr/bin/rig" if rig_on_path else None) if program == "rig" else which(program, *args, **kwargs))
    if rig_on_path:
        monkeypatch.setattr(SeatRuntime, "run", lambda _self, *args, **_kwargs: subprocess.CompletedProcess(["rig", *args], 0, f"rig version {installed}\n", ""))
    console = app.console()
    user, agent = Caller.user("main"), Caller.agent("main", "s1", "claude")

    with app.container.get(Scope).environment(1):
        user_set(app, "plans.plan_agents", True)
        user_set(app, "workers.openrig_version", "0.7.5")
        hook(app, "SessionStart")
        console.run(["environment", "overview"], agent)
        created = console.run(["plan", "create", "solo without OpenRig", "--brief", "the plan is done"], user)
        plan_id = int(created.text.split()[1].rstrip(":"))
        console.run(["plan", "add", str(plan_id), "the first solo step"], user)
        assert console.run(["plan", "approve", str(plan_id)], user).code == 0
        started = console.run(["plan", "start", str(plan_id)], user)
        app.runtime().deferred.drain()

    with app.container.get(Scope).environment(1):
        plan = app.container.get(Plans).find(plan_id)
    assert started.code == 0 and plan.mode == PlanMode.SOLO
    assert launches == [(f"plan-{plan_id}", "claude", ())], "a solo Plan agent still starts without invoking the pinned OpenRig runtime"


def _seat_failure_world(app, tmp_path):
    loaded(app, tmp_path)[1].reload()
    escalated = []

    class Escalated(Listener[RoleEscalated]):
        def handle(self, event: RoleEscalated) -> None:
            escalated.append((event.recipient, event.report))

    app.container.get(Bus).listen(RoleEscalated, Escalated())
    agents, domains, plans, workers, scope = (app.container.get(kind) for kind in (Agents, DomainRows, Plans, Workers, Scope))
    actor = Actor.system()
    with scope.environment(1):
        plan = plans.save(Plan(environment_id=1, title="alpha build"), actor)
        domain = agents.save(Agent(environment_id=1, session="domain-alpha", provider="codex", state="idle"), actor)
        domains.agent_linked("alpha", domain, actor)
        worker = workers.save(Worker(
            environment_id=1, name="Ada Lovelace", brief="patch", role="builder", plan_id=plan.id,
            profile="journal-senior", dispatcher="s1", provider="codex", model="gpt-6-luna",
            state=WorkerState.DISPATCHED, pid=91, session="thread-9", token_hash="seat-token",
        ).moved("dispatched", 100), actor)
    return worker, workers, escalated, actor


def _seat_failure_finisher(workers, tmp_path):
    runner = object.__new__(WorkerRunner)
    runner._locks = {}
    runner._locks_lock = Lock()
    runner.workers = workers
    runner.seats = SimpleNamespace(preserve=lambda *_args: None)
    runner.config = SimpleNamespace(home=tmp_path)
    runner.settings = SimpleNamespace(decimal=lambda _option: 1)
    runner.time_source = SimpleNamespace(seconds=lambda: 200)
    return runner


def _seat_monitor(worker, workers, runtime, now, timeout_minutes):
    runner = object.__new__(SeatRunner)
    runner._guard = Lock()
    runner._finishing = set()
    runner.workers = workers
    runner.tasks = SimpleNamespace(holder_task_ids=lambda _ref: (), finished_task_ids=lambda _ref: ())
    runner.time_source = SimpleNamespace(seconds=lambda: now)
    runner.settings = SimpleNamespace(decimal=lambda _option: timeout_minutes)
    runner.runtime = runtime
    return runner


def test_a_dead_seat_requeues_its_job_and_escalates_to_its_domain_agent(app, tmp_path, monkeypatch):
    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(seat_runner_module.ProcessCheck, "is_running", lambda _pid: False)
    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)
    seat = _seat_monitor(worker, workers, SimpleNamespace(session=lambda *_args: None), 101, 0)
    identity = SeatJobIdentity.from_worker(worker)

    with app.container.get(Scope).environment(worker.environment_id):
        seat.monitor(worker, identity, SimpleNamespace(target="alpha-builder@release"), worker.resume,
                     actor, finisher.finish_seat, worker.job_start_time())
    app.runtime().deferred.drain()

    with app.container.get(Scope).environment(worker.environment_id):
        current = workers.find(worker.row_id)
    assert current.state == WorkerState.UNFINISHED and "ended without clocking out" in current.run_end
    assert len(escalated) == 1 and escalated[0][0] == "domain-alpha" and "ended without clocking out" in escalated[0][1]


def test_a_stuck_seat_times_out_its_job_and_escalates_to_its_domain_agent(app, tmp_path, monkeypatch):
    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(seat_runner_module.ProcessCheck, "is_running", lambda _pid: True)
    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)
    stopped = []
    runtime = SimpleNamespace(
        session=lambda *_args: SimpleNamespace(pid=91, session="thread-9", activity_status="busy", status_updated_at=100),
        stop=lambda target, reason: stopped.append((target, reason)),
    )
    seat = _seat_monitor(worker, workers, runtime, 0, 1)
    samples = iter((100.5, 161))
    seat.time_source = SimpleNamespace(seconds=lambda: next(samples))
    seat.record_usage = lambda *_args: None
    identity = SeatJobIdentity.from_worker(worker)

    with app.container.get(Scope).environment(worker.environment_id):
        seat.monitor(worker, identity, SimpleNamespace(target="alpha-builder@release"), worker.resume,
                     actor, finisher.finish_seat, worker.job_start_time())
    app.runtime().deferred.drain()

    with app.container.get(Scope).environment(worker.environment_id):
        current = workers.find(worker.row_id)
    assert stopped and current.state == WorkerState.UNFINISHED and "without ending" in current.run_end
    assert len(escalated) == 1 and escalated[0][0] == "domain-alpha" and "without ending" in escalated[0][1]


def test_an_unreachable_openrig_times_out_and_requeues_without_leaving_a_monitored_job(app, tmp_path, monkeypatch):
    worker, workers, escalated, actor = _seat_failure_world(app, tmp_path)
    finisher = _seat_failure_finisher(workers, tmp_path)
    calls = []

    def unreachable(arguments, **kwargs):
        calls.append((arguments, kwargs))
        raise subprocess.TimeoutExpired(arguments, kwargs["timeout"])

    monkeypatch.setattr(seat_runtime_module.shutil, "which", lambda _program: "/usr/bin/rig")
    runtime = SeatRuntime(SimpleNamespace(home=tmp_path), SimpleNamespace(option=lambda _option: ""), unreachable)
    identity = SeatJobIdentity.from_worker(worker)
    seat = object.__new__(SeatRunner)
    seat._guard = Lock()
    seat._finishing = set()
    seat._active = {worker.id}
    seat._active_jobs = {worker.id: identity}
    seat.workers = workers
    seat.runtime = runtime
    seat.config = SimpleNamespace(home=tmp_path)
    seat.scope = app.container.get(Scope)
    seat.member = lambda _worker: SimpleNamespace(openrig_version="0.7.5")

    seat.monitor_existing(worker, identity, actor, finisher.finish_seat)
    app.runtime().deferred.drain()

    with app.container.get(Scope).environment(worker.environment_id):
        current = workers.find(worker.row_id)
    assert current.state == WorkerState.UNFINISHED and "seat failed:" in current.run_end
    assert len(escalated) == 1 and escalated[0][0] == "domain-alpha" and "OpenRig --version failed" in escalated[0][1]
    assert calls[0][0] == ["rig", "--version"] and calls[0][1]["timeout"] == 30 and not seat._active


def test_dispatch_to_a_role_honours_its_cardinality_one_instance_with_a_queue_for_journal_and_plan_and_a_worktree_of_its_own_for_many(app, tmp_path, monkeypatch):
    from journal.features.organization.support.role_instances import RoleInstances
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.models.support.ref import Ref
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    from journal.support.actor import Actor
    from journal.support.caller import Caller
    from tests.test_features import hook
    started = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture, organization = loaded(app, tmp_path)
    user_set(app, "plans.plan_agents", True)
    fixture.role("alpha", "steward", cardinality="journal", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.role("beta", "porter", cardinality="plan", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "steward"])
    fixture.domain("beta", roles=["keeper", "porter"])
    contracts = organization.reload()
    agent = Caller.agent("main", "s1", "claude")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    from journal.repositories.scope import Scope
    with app.container.get(Scope).environment(1):
        workers = app.container.get(Workers)
        send = lambda name, *argv: dispatched(console, [name, f"the job of {name}", "--changes", "the files of its task", *argv], agent)

        first = send("Ada Lovelace", "--role", "steward")
        assert first.code == 0 and len(started) == 1, first.error
        second = send("Grace Hopper", "--role", "steward")
        assert second.code == 0 and len(started) == 1 and len(workers.role_instances("steward")) == 1, "a second job for a journal Role starts no second instance"
        assert [task.id for task in app.container.get(Tasks).queue(Ref.build(workers.role_instances("steward")[0]))] == [2], "the second job waits in the one instance's queue"

        assert send("Ida Rhodes", "--role", "builder").code == 0 and send("Rosalind Franklin", "--role", "builder").code == 0 and len(started) == 3, "a many Role starts an instance for each job"

        instances = app.container.get(RoleInstances)
        porter = contracts.role("porter")
        task = app.container.get(Tasks).find(1)
        workers.save(Worker(environment_id=1, name="Edith Clarke", brief="b", role="porter", plan_id=7, state=WorkerState.REPORTED), Actor.system())
        workers.save(Worker(environment_id=1, name="Mary Kenneth", brief="b", role="porter", plan_id=8, state=WorkerState.DISPATCHED), Actor.system())
        assert instances.existing(contracts.role("builder"), task) is None, "many has no instance to join"
        assert instances.existing(porter, task) is None, "a task in no plan is a plan of its own, so a plan Role starts an instance for it"
        monkeypatch.setattr(RoleInstances, "plan_of", lambda self, task: 8)
        assert instances.existing(porter, task).name == "Mary Kenneth", "a plan Role has one instance for each plan"
        monkeypatch.setattr(RoleInstances, "plan_of", lambda self, task: 9)
        assert instances.existing(porter, task) is None, "and another plan gets its own"


def test_a_send_goes_only_along_the_hubs_and_a_send_from_one_role_to_another_is_refused_with_the_hub_to_use(app, tmp_path):
    from journal.features.organization.support.hub_routes import HubRoutes
    from journal.models.worker import Worker
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from journal.support.rejection import Rejection
    loaded(app, tmp_path)
    routes = app.container.get(HubRoutes)
    along = [("role:alpha/builder", "domain:alpha"), ("domain:alpha", "role:alpha/scout"), ("domain:alpha", "plan"), ("plan", "domain:beta"), ("plan", "main"), ("main", "plan")]
    across = [("role:alpha/builder", "role:alpha/scout"), ("role:alpha/builder", "domain:beta"), ("domain:alpha", "role:beta/keeper"), ("domain:alpha", "domain:beta"), ("role:alpha/scout", "plan"), ("main", "domain:alpha")]
    assert all(routes.allowed(*pair) for pair in along), "the hubs: Role and Domain agent, Domain agent and Plan agent, Plan agent and main agent"
    assert not any(routes.allowed(*pair) for pair in across), "anything else is sideways"
    with app.container.get(Scope).environment(1):
        workers = app.container.get(Workers)
        sender = workers.save(Worker(environment_id=1, name="Ada Lovelace", brief="b", role="builder", dispatcher="s1"), Actor.system())
        peer = workers.save(Worker(environment_id=1, name="Grace Hopper", brief="b", role="scout", dispatcher="s1"), Actor.system())
        plain = workers.save(Worker(environment_id=1, name="Ida Rhodes", brief="b", dispatcher="s1"), Actor.system())
        tasks = app.container.get(Tasks)
        task = tasks.save(Task(environment_id=1, title="Grace's task", state=TaskState.STARTED), Actor.system())
        tasks.handover(task, Ref.build(peer), Actor.system())
        refusal = routes.refusal(sender, peer)
        assert "Roles do not send to each other" in refusal and "domain:alpha" in refusal, refusal
        assert routes.refusal(sender, plain) == "" and routes.refusal(plain, peer) == "", "a worker with no Role is not Role traffic"
        with pytest.raises(Rejection, match="Roles do not send"):
            app.container.get(WorkerActions).peer_send(peer.id, "take the routed path", sender.id, Actor.system())


def test_a_changed_contract_is_reported_and_taken_up_by_new_jobs_only_while_the_version_a_job_began_on_is_kept(app, tmp_path):
    from journal.support.caller import Caller
    fixture, organization = loaded(app, tmp_path)
    began = organization.contracts().version
    assert not organization.is_stale(), "nothing changed since it was read"
    fixture.role("beta", "keeper", cardinality="journal", writes=False, tools=["read_files"], approval_required=["contract_change"], model=fixture.model("opus", False))
    agent = Caller.agent("main", "s1", "claude")
    assert organization.is_stale() and "the folder has changed since it was read" in app.console().run(["organization", "list"], agent).text, "a changed folder is reported where it is listed"
    assert organization.contracts().role("keeper").cardinality is Cardinality.PLAN, "a running journal keeps what it read until it is told to read again"
    changed = organization.reload().version
    assert changed != began and not organization.is_stale()
    assert organization.at(began).role("keeper").cardinality is Cardinality.PLAN and organization.at(changed).role("keeper").cardinality is Cardinality.JOURNAL, "a job that began on the first version still sees it; a new job sees the second"


def test_the_contracts_are_read_at_the_git_version_the_setting_names_and_a_version_that_is_not_there_is_reported(app, tmp_path):
    from journal.features.organization.support.organization import Organization
    from journal.support.inner_repositories import InnerRepositories
    from tests.organization_fixture import OrganizationFixture
    from tests.user_settings import user_set
    repository = tmp_path / "repository"
    fixture = OrganizationFixture(repository / "agentic-organization").write()
    git = lambda *argv: InnerRepositories.git(repository, "-c", "user.name=Test", "-c", "user.email=test@example.com", *argv)
    assert git("init", "-q").returncode == 0
    git("add", "-A")
    assert git("commit", "-q", "-m", "first").returncode == 0
    first = git("rev-parse", "HEAD").stdout.strip()
    fixture.role("beta", "keeper", cardinality="journal", writes=False, tools=["read_files"], approval_required=["contract_change"], model=fixture.model("opus", False))
    git("add", "-A")
    assert git("commit", "-q", "-m", "second").returncode == 0
    user_set(app, "workers.organization_folder", str(fixture.root))
    organization = app.container.get(Organization)
    assert organization.reload().role("keeper").cardinality is Cardinality.JOURNAL, "with no version the files as they are checked out"
    user_set(app, "workers.organization_version", first)
    read = organization.reload()
    assert read.problems == () and read.role("keeper").cardinality is Cardinality.PLAN and read.role("scout") is not None, "at the first version the Role was still a plan Role"
    user_set(app, "workers.organization_version", "no-such-version")
    problems = organization.reload().problems
    assert [problem.rule for problem in problems] == ["version"] and "not a commit" in problems[0].message


def test_a_task_handed_or_queued_to_a_role_is_tied_to_its_domain_and_each_domain_lists_its_plans_with_only_its_tasks(app, tmp_path):
    from datetime import datetime, timezone
    from journal.features.organization.support.domain_plans import DomainPlans
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from journal.support.caller import Caller
    loaded(app, tmp_path)[1].reload()
    tasks, workers, plans, links, domains, domain_plans = (app.container.get(kind) for kind in (Tasks, Workers, Plans, Links, DomainRows, DomainPlans))
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        built, kept, looked, loose = (tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), actor) for title in ("the build", "the contract", "the lookup", "the loose end"))
        for task in (built, kept, looked, loose):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        builder, keeper, senior = (workers.save(Worker(environment_id=1, name=name, brief="b", profile="journal-senior", role=role), actor) for name, role in (("Mr. Brunel", "builder"), ("Ms. Hopper", "keeper"), ("Mr. Babbage", "")))
        tasks.handover(built, Ref.build(builder), actor)
        tasks.queued(looked, Ref.build(builder), actor)
        tasks.queued(kept, Ref.build(keeper), actor)
        tasks.handover(loose, Ref.build(senior), actor)
        app.runtime().deferred.drain()
        alpha, beta = domain_plans.of("alpha"), domain_plans.of("beta")
        assert [(line.plan.id, [task.id for task in line.tasks]) for line in alpha] == [(plan.id, [built.id, looked.id])], "the plan lists under alpha with alpha's tasks alone, the one handed to no Role left out"
        assert [(line.plan.id, [task.id for task in line.tasks]) for line in beta] == [(plan.id, [kept.id])], "the same plan lists under beta with beta's task alone"
        assert alpha[0].is_active() and beta[0].is_active(), "a Role of each domain holds one of its tasks"
        tasks.save(tasks.find(kept.id).completed(datetime.now(timezone.utc), "kept"), actor)
        assert not domain_plans.of("beta")[0].is_active() and domain_plans.of("alpha")[0].is_active(), "beta's task done, no Role of beta holds the plan; alpha still does"
        domains.task_tied(tasks.find(looked.id), "beta", actor)
        assert [task.id for task in domain_plans.of("alpha")[0].tasks] == [built.id] and [task.id for task in domain_plans.of("beta")[0].tasks] == [kept.id, looked.id], "a task handed on to another domain's Role belongs to that domain alone"
    shown = app.console().run(["organization", "plans"], Caller.agent("main", "s1", "claude")).text
    assert f"domain alpha: Alpha\n  plan {plan.id} the floors, Planned, active: task {built.id} open\ndomain beta: Beta\n  plan {plan.id} the floors, Planned, active: task {kept.id} completed, task {looked.id} open" in shown


def test_a_plan_stands_in_the_phase_each_domains_tasks_reached_on_that_domains_board_by_the_names_the_domain_gives(app, tmp_path):
    from datetime import datetime, timezone
    from journal.events.bus import Bus
    from journal.events.listener import Listener
    from journal.events.rows.plan_entered_board_phase import PlanEnteredBoardPhase
    from journal.features.organization.support.domain_plans import DomainPlans
    from journal.models.board_phase import BoardPhase
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.models.worker_state import WorkerState
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from journal.support.caller import Caller
    fixture, organization = loaded(app, tmp_path)
    fixture.domain("alpha", roles=["scout", "builder"], board={"in_progress": "Being built", "done": "Implemented"})
    organization.reload()
    entered = []

    class Entered(Listener[PlanEnteredBoardPhase]):
        def handle(self, event: PlanEnteredBoardPhase) -> None:
            entered.append((event.plan_id, event.domain, event.phase))

    app.container.get(Bus).listen(PlanEnteredBoardPhase, Entered())
    tasks, workers, plans, links, domain_plans = (app.container.get(kind) for kind in (Tasks, Workers, Plans, Links, DomainPlans))
    actor, now = Actor.system(), datetime.now(timezone.utc)
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        built, kept, loose = (tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), actor) for title in ("the build", "the contract", "the loose end"))
        for task in (built, kept, loose):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        builder, keeper = (workers.save(Worker(environment_id=1, name=name, brief="b", profile="journal-senior", role=role), actor) for name, role in (("Mr. Brunel", "builder"), ("Ms. Hopper", "keeper")))
        tasks.handover(built, Ref.build(builder), actor)
        tasks.handover(kept, Ref.build(keeper), actor)
        app.runtime().deferred.drain()
        assert [line.phase() for line in (*domain_plans.of("alpha"), *domain_plans.of("beta"))] == [BoardPhase.PLANNED, BoardPhase.PLANNED], "a domain task exists in the plan and none is started"
        tasks.save(tasks.find(built.id).worker_started(now), actor)
        app.runtime().deferred.drain()
        tasks.save(tasks.find(kept.id).worker_started(now), actor)
        app.runtime().deferred.drain()
        workers.save(workers.find(keeper.id).with_(state=WorkerState.DELIVERED), actor)
        app.runtime().deferred.drain()
        assert (domain_plans.of("alpha")[0].phase(), domain_plans.of("beta")[0].phase()) == (BoardPhase.IN_PROGRESS, BoardPhase.IN_REVIEW), "alpha's task is worked; beta's worker clocked out and its proofs wait to be checked"
        tasks.save(tasks.find(kept.id).completed(now, "kept"), actor)
        app.runtime().deferred.drain()
        assert (domain_plans.of("alpha")[0].phase(), domain_plans.of("beta")[0].phase()) == (BoardPhase.IN_PROGRESS, BoardPhase.DONE), "beta is done with its task while alpha and a task of no domain are still open"
    app.runtime().deferred.drain()
    assert [(n, domain, phase) for n, domain, phase in entered if n == plan.id] == [(plan.id, "alpha", BoardPhase.PLANNED), (plan.id, "beta", BoardPhase.PLANNED), (plan.id, "alpha", BoardPhase.IN_PROGRESS), (plan.id, "beta", BoardPhase.IN_PROGRESS), (plan.id, "beta", BoardPhase.IN_REVIEW), (plan.id, "beta", BoardPhase.DONE)], "each phase a plan enters on a board fires once, in order"
    shown = app.console().run(["organization", "plans"], Caller.agent("main", "s1", "claude")).text
    assert f"domain alpha: Alpha\n  plan {plan.id} the floors, Being built, active: task {built.id} started\ndomain beta: Beta\n  plan {plan.id} the floors, Done: task {kept.id} completed" in shown, "each board names the phase by its domain's own name"


def test_a_role_that_is_stuck_refused_or_ends_without_clocking_out_is_reported_to_its_domain_agent_then_the_plan_agent_then_the_user(app, tmp_path):
    from journal.events.agent.impasse_report import ImpasseReport
    from journal.events.agent.line_delivered import LineDelivered
    from journal.events.bus import Bus
    from journal.events.listener import Listener
    from journal.events.rows.role_escalated import RoleEscalated
    from journal.features.organization.listeners.role_refusal_report import RoleRefusalReport
    from journal.features.organization.listeners.role_stuck_report import RoleStuckReport
    from journal.features.organization.organization_nudges import OrganizationNudges
    from journal.features.organization.support.role_escalation import ESCALATED_LINK
    from journal.models.agent import Agent
    from journal.models.plan import Plan
    from journal.models.worker import Worker
    from journal.repositories.agents import Agents
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.messages import Messages
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    loaded(app, tmp_path)[1].reload()
    escalated = []

    class Escalated(Listener[RoleEscalated]):
        def handle(self, event: RoleEscalated) -> None:
            escalated.append((event.recipient, event.report))

    app.container.get(Bus).listen(RoleEscalated, Escalated())
    agents, workers, plans, domains, links, scope = (app.container.get(kind) for kind in (Agents, Workers, Plans, DomainRows, Links, Scope))
    actor = Actor.system()
    with scope.environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        domain_agent, plan_agent, gone = (agents.save(Agent(environment_id=1, session=session, provider="claude", state=state), actor) for session, state in (("domain-alpha", "idle"), ("plan-1", "idle"), ("domain-beta", "ended")))
        domains.agent_linked("alpha", domain_agent, actor)
        domains.agent_linked("beta", gone, actor)
        plans.agent_linked(plan, plan_agent, actor)
        builder, keeper, franklin = (workers.save(Worker(environment_id=1, name=name, brief="b", profile="journal-senior", role=role, plan_id=plan_id, session=session, dispatcher="s1"), actor)
                                     for name, role, plan_id, session in (("Mr. Brunel", "builder", plan.id, "w-brunel"), ("Ms. Hopper", "keeper", plan.id, "w-hopper"), ("Ms. Franklin", "keeper", 0, "w-franklin")))
        brunel_agent = Agent(environment_id=1, session="w-brunel", provider="claude")
        app.container.get(RoleStuckReport).handle(ImpasseReport(agent=brunel_agent, reason="the schema is missing").placed(brunel_agent, None, 1.0))
        app.runtime().deferred.drain()
        assert escalated == [("domain-alpha", f"the Role builder of alpha is stuck: the schema is missing (worker {builder.id}, Mr. Brunel)")], "step one: a stuck Role is reported to its Domain agent"
        hopper_agent = Agent(environment_id=1, session="w-hopper", provider="claude")
        app.container.get(RoleRefusalReport).handle(LineDelivered(agent=hopper_agent, nudge=OrganizationNudges.ROLE_WRITES_NOTHING.key, values={"role": "keeper"}).placed(hopper_agent, None, 2.0))
        app.runtime().deferred.drain()
        assert escalated[-1] == ("plan-1", f"the Role keeper of beta was refused: your Role keeper has no write tool: change no file (worker {keeper.id}, Ms. Hopper)"), "step two: its Domain agent ended, a refused Role is reported to the Plan agent"
        workers.save(workers.find(franklin.id).unfinished(3.0, "stopped after 30 minutes without ending: (nothing printed)"), actor)
        app.runtime().deferred.drain()
        cards = [message for message in app.container.get(Messages).all() if message.text == "Role reported to you"]
    assert len(escalated) == 2 and len(cards) == 1 and cards[0].data["lines"] == ["the Role keeper of beta ended without clocking out", "stopped after 30 minutes without ending: (nothing printed)", f"worker {franklin.id}, Ms. Franklin"] and cards[0].session == "s1", "step three: with no Domain agent running and no plan, a Role that timed out is reported to the user in its dispatcher's chat"
    assert ([ref.id for ref in links.targets(builder, ESCALATED_LINK)], [ref.id for ref in links.targets(keeper, ESCALATED_LINK)]) == ([domain_agent.id], [plan_agent.id]), "each report to an agent is a link from the worker to it"


def test_a_seat_on_a_model_other_than_its_roles_contract_names_is_caught_and_one_on_it_is_not():
    from journal.features.organization.support.seat_model_guard import SeatModelGuard
    role = a_role(models=RoleModels("sonnet", "gpt-6-luna", "max"))
    assert SeatModelGuard.mismatch(role, "claude", "sonnet") == "" and SeatModelGuard.mismatch(role, "claude", "claude-sonnet-5-5") == "", "the contract's model, whole or in a full name, is right"
    assert SeatModelGuard.mismatch(role, "codex", "gpt-6-luna") == "", "and so on Codex"
    wrong = SeatModelGuard.mismatch(role, "claude", "opus")
    assert "runs on opus" in wrong and "names sonnet" in wrong and wrong.endswith("restart it on sonnet"), "a seat on another model is named with the model to restart it on"
    assert "no model" in SeatModelGuard.mismatch(role, "codex", ""), "a seat with no observed model is not trusted"


def test_a_codex_role_job_starts_with_the_reasoning_effort_its_contract_names_and_a_claude_one_with_none(app, tmp_path, monkeypatch):
    from journal.features.organization.support.role_boot import RoleBoot
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.providers.codex import Codex
    from journal.supervisor_link import SupervisorLink
    from journal.support.caller import Caller
    from tests.test_features import hook
    started = []
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture, organization = loaded(app, tmp_path)
    user_set(app, "plans.plan_agents", True)
    fixture.role("beta", "porter", cardinality="many", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("beta", roles=["keeper", "porter"])
    organization.reload()
    agent = Caller.agent("main", "s1", "claude")
    hook(app, "SessionStart")
    console = app.console()
    console.run(["environment", "overview"], agent)
    for provider in ("codex", "claude"):
        sent = dispatched(console, [f"Ada {provider}", "the job", "--changes", "the files of its task", "--role", "porter", "--provider", provider], agent)
        assert sent.code == 0, sent.error
    from journal.repositories.scope import Scope
    with app.container.get(Scope).environment(1):
        roles, runner = app.container.get(RoleBoot), app.container.get(WorkerRunner)
        codex, claude = started
        assert roles.effort(codex) == "max" and roles.effort(claude) == "", "only a Codex worker is given its Role's effort"
        command = Codex().worker_command(runner.instructed(codex), codex.model, codex.resume, codex.session, roles.effort(codex))
        assert command[-3:-1] == ["-c", "model_reasoning_effort=max"] and command[-1] == runner.instructed(codex), "the effort is set with -c before the brief"
        assert "model_reasoning_effort" not in " ".join(Codex().worker_command("brief", "gpt-6-luna", "", "")), "no effort named, none set"


def test_a_journal_role_queue_serves_a_second_plan_before_a_second_task_from_the_first(app, tmp_path):
    _fixture, organization = loaded(app, tmp_path)
    contracts = organization.reload()
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        plans, tasks, links, workers = (app.container.get(kind) for kind in (Plans, Tasks, Links, Workers))
        first_plan = plans.save(Plan(environment_id=1, title="First plan", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        second_plan = plans.save(Plan(environment_id=1, title="Second plan", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        first, next_first, last_first, next_second = (tasks.save(Task(environment_id=1, title=title, brief=title), actor)
                                                      for title in ("A1", "A2", "A3", "B1"))
        for task in (first, next_first, last_first):
            links.save(Link(source=Ref.build(task), target=Ref.build(first_plan), link_type=PLAN_LINK), actor)
        links.save(Link(source=Ref.build(next_second), target=Ref.build(second_plan), link_type=PLAN_LINK), actor)
        worker = workers.save(Worker(environment_id=1, name="Ada Lovelace", role="scout", contract=contracts.version,
                                     plan_id=first_plan.id, provider="claude", model="opus"), actor)
        holder = Ref.build(worker)
        tasks.handover(first, holder, actor)
        for task in (next_first, last_first, next_second):
            tasks.queued(task, holder, actor)
        app.runtime().deferred.drain()

        queue = [task.id for task in tasks.queue(holder)]
    assert queue == [next_second.id, next_first.id, last_first.id], "the second plan gets its turn before the first plan gets a second queued task"


def test_a_journal_role_job_carries_its_queued_plan_and_task(app, tmp_path):
    _fixture, organization = loaded(app, tmp_path)
    contracts = organization.reload()
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        plans, tasks, links, workers = (app.container.get(kind) for kind in (Plans, Tasks, Links, Workers))
        first_plan = plans.save(Plan(environment_id=1, title="First plan", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        second_plan = plans.save(Plan(environment_id=1, title="Second plan", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        task = tasks.save(Task(environment_id=1, title="Second plan task", brief="Work for the second plan."), actor)
        links.save(Link(source=Ref.build(task), target=Ref.build(second_plan), link_type=PLAN_LINK), actor)
        worker = workers.save(Worker(environment_id=1, name="Ada Lovelace", role="scout", contract=contracts.version,
                                     plan_id=first_plan.id, provider="claude", model="opus"), actor)
        tasks.queued(task, Ref.build(worker), actor)
        current, identity, prompt = app.container.get(SeatRunner).job_context(worker, "Work on the queued task.", actor)

    assert current.plan_id == second_plan.id and identity.plan_id == second_plan.id, "the worker's active plan follows the queued task"
    assert identity.task_id == task.id and f"task {task.id} ({task.title}) in plan {second_plan.id} ({second_plan.title})" in prompt, "the seat receives both the task and its plan"


def test_a_journal_role_job_uses_a_fresh_openrig_launch(app, monkeypatch):
    calls = []
    worker = Worker(id=18, name="Ada Lovelace", role="scout")
    member = SimpleNamespace(target="alpha-scout@organization-1")
    identity = SeatJobIdentity.from_worker(worker, task_id=57, plan_id=3)
    runner = app.container.get(SeatRunner)
    runner.runtime.launch = lambda seat, reason: calls.append((seat, reason))
    runner.launch_fresh(member, worker, identity)

    assert calls == [(member, "journal worker 18 starts task 57 with a fresh context")], "the Role runner uses the fresh-stop OpenRig launch for its job"


def test_a_dispatched_role_seat_starts_clocks_in_and_returns_its_clockout_to_its_domain_agent(app, tmp_path, monkeypatch):
    from journal.engine.states_catalogue import StatesCatalogue
    from journal.features.organization.support.rig_staffing import RigStaffing
    from journal.features.organization.support.seat_runtime import SeatSession
    from journal.features.tasks.states.external_wait import ExternalWait
    from journal.features.workers.support.worker_launch import WorkerLaunch
    from journal.features.workers.support.worker_reports import WorkerReports
    from journal.support.caller import Caller
    from tests.test_features import WORKER_RUNNER_START

    contracts = plan_contracts(app, tmp_path)
    user_set(app, "plans.plan_agents", True)
    user_set(app, "workers.openrig_version", "0.7.6")
    monkeypatch.setattr(WorkerRunner, "start", WORKER_RUNNER_START)

    threads, launches, sent = [], [], []

    class CapturedThread:
        def __init__(self, *, target, args, name, daemon):
            self.target, self.args, self.name, self.daemon = target, args, name, daemon

        def start(self):
            threads.append(self)

    monkeypatch.setattr(seat_runner_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(seat_runner_module.ProcessCheck, "is_running", lambda _pid: True)
    monkeypatch.setattr(SeatRunner, "record_usage", lambda *args: None)

    def run(_runtime, *arguments, check=True):
        output = "rig version 0.7.6\n" if arguments == ("--version",) else "{}"
        return subprocess.CompletedProcess(["rig", *arguments], 0, output, "")

    monkeypatch.setattr(SeatRuntime, "run", run)
    runtime = app.container.get(SeatRuntime)
    launch_state = {"started": False}
    seat_changes = []

    def launch(member, reason):
        launches.append((member, reason))
        launch_state["started"] = True

    def remove_node(rig, logical_id):
        seat_changes.append(("remove", rig, logical_id))
        launch_state["started"] = False

    def add_member(rig, pod, fragment, root):
        seat_changes.append(("add", rig, pod, fragment.name))

    def session(_member, _native_session=""):
        return SeatSession(4320 + len(launches), f"role-session-{len(launches)}", "running", 10) if launch_state["started"] else None

    def send(member, prompt):
        sent.append((member, prompt))
        session_id = f"role-session-{len(launches)}"
        status, answer = posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": session_id}, {
            "X-Journal-Env": member.environment,
            "X-Journal-Actor": member.actor,
            "X-Journal-Actor-Token": member.token,
        })
        assert status == 200, answer
        caller = Caller.worker(member.environment, worker.id, session_id, member.provider)
        clocked_in = app.console().run(["clock-in", "record"], caller)
        assert clocked_in.code == 0, clocked_in.error
        app.container.get(WorkerReports).delivered(app.container.get(Workers).find(worker.id), "The note is written.", caller.actor)

    runtime.launch = launch
    runtime.session = session
    runtime.send = send
    runtime.remove_node = remove_node
    runtime.add = add_member

    actor = Actor.system()

    def launch_worker(worker):
        with monkeypatch.context() as patch:
            patch.setattr(seat_runner_module.threading, "Thread", CapturedThread)
            return app.container.get(WorkerLaunch).launched(worker, actor)

    with app.container.get(Scope).environment(1):
        plans, tasks, links = (app.container.get(kind) for kind in (Plans, Tasks, Links))
        plan = plans.save(Plan(environment_id=1, title="Write the note", state=PlanState.STARTED, mode=PlanMode.ORGANIZATION), actor)
        app.container.get(RigStaffing).start_plan(plan, app.container.get(Environments).find(1), Agent(environment_id=1, provider="claude"), actor)
        domain_agent = app.container.get(Agents).save(Agent(environment_id=1, session="domain-session", provider="claude"), actor)
        app.container.get(DomainRows).agent_linked("alpha", domain_agent, actor)
        task = tasks.save(Task(environment_id=1, title="Write one note", brief="Write a short note."), actor)
        links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        worker = app.container.get(Workers).save(Worker(
            environment_id=1, name="Ada Lovelace", brief="Write a short note.", role="planner",
            contract=contracts.version, plan_id=plan.id, provider="claude", model="sonnet",
            dispatcher="domain-session",
        ).contacted(10), actor)
        tasks.handover(task, Ref.build(worker), actor)

        launched = launch_worker(worker)
        states = app.container.get(StatesCatalogue)
        waiting = states.stack(app.container.get(Agents).find(domain_agent.id)).top()
        assert launched.state == WorkerState.DISPATCHED and isinstance(waiting, ExternalWait), "dispatch is recorded before the Domain agent waits for its Role"
        assert len(threads) == 1
        threads[0].target(*threads[0].args)

        current = app.container.get(Workers).find(worker.id)
        returned = states.stack(app.container.get(Agents).find(domain_agent.id)).top()
        spec = json.loads((app.config.home / "runtime" / "rigs" / f"plan-{plan.id}" / "rig.yaml").read_text())
        pod = next(pod for pod in spec["pods"] if pod["id"] == "alpha")
        role_member = next(member for member in pod["members"] if member["id"] == "planner")
        pod_path = app.config.home / "runtime" / "rigs" / f"plan-{plan.id}" / "pods" / "alpha.json"
        first_pod = json.loads(pod_path.read_text())
        first_pod_role = next(member for member in first_pod["members"] if member["id"] == "planner")

        first_worker_id = worker.id
        first_role_actor = role_member["env"][ACTOR]
        first_role_token = role_member["env"][ACTOR_TOKEN]
        next_task = tasks.save(Task(environment_id=1, title="Write another note", brief="Write another short note."), actor)
        links.save(Link(source=Ref.build(next_task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        next_worker = app.container.get(Workers).save(Worker(
            environment_id=1, name="Ada Lovelace", brief="Write another short note.", role="planner",
            contract=contracts.version, plan_id=plan.id, provider="claude", model="sonnet",
            dispatcher="domain-session",
        ).contacted(20), actor)
        tasks.handover(next_task, Ref.build(next_worker), actor)
        worker = next_worker
        second_launched = launch_worker(next_worker)
        assert second_launched.state == WorkerState.DISPATCHED and len(threads) == 2
        threads[1].target(*threads[1].args)

        next_current = app.container.get(Workers).find(next_worker.id)
        next_returned = states.stack(app.container.get(Agents).find(domain_agent.id)).top()
        spec = json.loads((app.config.home / "runtime" / "rigs" / f"plan-{plan.id}" / "rig.yaml").read_text())
        pod = next(pod for pod in spec["pods"] if pod["id"] == "alpha")
        role_member = next(member for member in pod["members"] if member["id"] == "planner")
        pod_fragment = json.loads(pod_path.read_text())
        pod_role_member = next(member for member in pod_fragment["members"] if member["id"] == "planner")

    assert len(launches) == len(sent) == 2 and sent[0][0].actor == f"worker:{first_worker_id}" and sent[1][0].actor == f"worker:{worker.id}", "Journal launches and sends each dispatched worker to the generated Role seat"
    assert "Write a short note." in sent[0][1] and current.state == WorkerState.DELIVERED, "the Role clocks in, receives its brief, and clocks out"
    assert not isinstance(returned, ExternalWait), "the Role's clock-out resolves the Domain agent's wait through its worker report"
    assert next_current.state == WorkerState.DELIVERED and "another short note" in sent[1][1], "the rebound seat clocks in and returns the second worker's result"
    assert not isinstance(next_returned, ExternalWait), "the second clock-out resolves the Domain agent's wait"
    assert pod["edges"] == [{"kind": "delegates_to", "from": "domain-agent", "to": "planner"}], "staffing keeps the Domain-to-Role hub route"
    assert {"Bash(rig send *)", "Bash(rig queue *)"}.issubset(role_member["claude_permissions"]["deny"]), "the Role seat keeps the direct-send and queue denials"
    assert first_role_actor == f"worker:{first_worker_id}" and role_member["env"][ACTOR] == f"worker:{worker.id}", "the persistent plan Role member is rebound to the newly dispatched worker"
    assert role_member["env"][ACTOR_TOKEN] != first_role_token, "rebinding generates a token for the new worker actor"
    assert first_pod_role["env"][ACTOR] == f"worker:{first_worker_id}" and pod_role_member["env"][ACTOR] == f"worker:{worker.id}", "the incremental pod fragment tracks the Role actor as workers change"
    assert pod_role_member["env"][ACTOR_TOKEN] == role_member["env"][ACTOR_TOKEN], "the pod fragment keeps the rebound Role token"
    assert seat_changes == [
        ("remove", f"plan-{plan.id}", "alpha.planner"),
        ("add", f"plan-{plan.id}", "alpha", "alpha-planner.json"),
    ], "the running Role node is replaced before the next worker starts"


def test_the_queue_of_a_journal_role_keeps_its_order_across_a_restart_and_hands_no_job_to_a_second_instance(tmp_path, monkeypatch):
    from journal.config import Config
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.models.support.ref import Ref
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.supervisor_link import SupervisorLink
    from journal.support.caller import Caller
    from tests.main_journal import main_journal
    from tests.organization_fixture import OrganizationFixture
    from tests.test_features import hook
    from tests.user_settings import user_set
    started = []
    monkeypatch.setattr(Config, "status_home", property(lambda self: tmp_path / "status"))
    monkeypatch.setattr(SupervisorLink, "_send", lambda self, environment_id, verb, fields: None)
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: started.append(worker))
    fixture = OrganizationFixture(tmp_path / "organization").write()
    fixture.role("alpha", "steward", cardinality="journal", writes=True, tools=["read_files", "edit_files"], model=fixture.model("sonnet", True))
    fixture.domain("alpha", roles=["scout", "builder", "steward"])
    agent = Caller.agent("main", "s1", "claude")
    send = lambda console, name: dispatched(console, [name, f"the job of {name}", "--changes", "the files of its task", "--role", "steward"], agent)
    first = main_journal(Config(tmp_path, port=0))
    first.runtime().start()
    user_set(first, "workers.organization_folder", str(fixture.root))
    user_set(first, "plans.plan_agents", True)
    hook(first, "SessionStart")
    first.console().run(["environment", "overview"], agent)
    sent = [send(first.console(), name) for name in ("Ada Lovelace", "Grace Hopper", "Ida Rhodes")]
    assert [outcome.code for outcome in sent] == [0, 0, 0] and len(started) == 1, ([outcome.error for outcome in sent], "one instance, the other two jobs queued on it")
    first.runtime().stop()
    second = main_journal(Config(tmp_path, port=0))
    second.runtime().start()
    try:
        with second.container.get(Scope).environment(1):
            [instance] = second.container.get(Workers).role_instances("steward")
            queued = lambda: [task.id for task in second.container.get(Tasks).queue(Ref.build(instance))]
            assert queued() == [2, 3], "after the restart the queue keeps its order"
            assert send(second.console(), "Edith Clarke").code == 0 and len(started) == 1 and len(second.container.get(Workers).role_instances("steward")) == 1, "a job sent after the restart joins the one instance"
            assert queued() == [2, 3, 4] and len(set(queued())) == len(queued()), "at the end of the queue, and no job twice"
    finally:
        second.runtime().stop()


def test_the_organization_is_served_in_one_answer_and_each_domains_counts_are_a_row_that_follows_its_instances_queues_and_active_plans(app, tmp_path):
    from datetime import datetime, timezone
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.worker import Worker
    from journal.repositories.domain_counts import DomainCounts
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.workers import Workers
    from journal.support.actor import Actor
    from tests.in_process import answered, get_answer
    fixture, organization = loaded(app, tmp_path)
    git = lambda *args: InnerRepositories.git(fixture.root, "-c", "user.name=Test", "-c", "user.email=test@example.com", *args)
    assert git("init", "-q").returncode == 0
    git("add", "-A")
    assert git("commit", "-q", "-m", "organization").returncode == 0
    commit = git("rev-parse", "HEAD").stdout.strip()
    organization.reload()
    tasks, workers, plans, links, counts = (app.container.get(kind) for kind in (Tasks, Workers, Plans, Links, DomainCounts))
    actor, now = Actor.system(), datetime.now(timezone.utc)
    env = {"X-Journal-Env": "main"}
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="the floors"), actor)
        built, looked, kept = (tasks.save(Task(environment_id=1, title=title, brief=f"{title} reads"), actor) for title in ("the build", "the lookup", "the contract"))
        for task in (built, looked, kept):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        assert counts.all_matching() == [], "no count until a task is handed to a Role"
        builder = workers.save(Worker(environment_id=1, name="Mr. Brunel", brief="b", profile="journal-senior", role="builder", plan_id=plan.id), actor)
        keeper = workers.save(Worker(environment_id=1, name="Ms. Hopper", brief="b", profile="journal-senior", role="keeper", plan_id=plan.id), actor)
        tasks.handover(built, Ref.build(builder), actor)
        tasks.queued(looked, Ref.build(builder), actor)
        tasks.queued(kept, Ref.build(keeper), actor)
        app.runtime().deferred.drain()
        rows = {row.name: row for row in counts.all_matching()}
        assert (rows["alpha"].plans_active, rows["alpha"].roles) == (1, {"scout": {"instances": 0, "queued": 0}, "builder": {"instances": 1, "queued": 1}}), "alpha: one plan active, the builder running with one task queued for it"
        assert (rows["beta"].plans_active, rows["beta"].roles) == (1, {"keeper": {"instances": 1, "queued": 1}})
        tasks.save(tasks.find(kept.id).completed(now, "kept"), actor)
        workers.save(workers.find(keeper.id).with_(adopted=True, state="released"), actor)
        app.runtime().deferred.drain()
        assert {row.name: row.roles for row in counts.all_matching()}["beta"] == {"keeper": {"instances": 0, "queued": 0}}, "an instance that is released stops being counted, and so does its queue"
        assert {row.name: row.plans_active for row in counts.all_matching()}["beta"] == 0, "and beta's plan is no longer active once its task is done"
    status, shown = get_answer(app, "/journal/organization", env)
    assert shown["folder"] == str(fixture.root) and shown["commit"] == commit, "the page answer names the actual folder and the commit it reads"
    alpha = next(domain for domain in shown["domains"] if domain["id"] == "alpha")
    beta = next(domain for domain in shown["domains"] if domain["id"] == "beta")
    builder_role = next(role for role in alpha["roles"] if role["id"] == "builder")
    assert alpha["edges"] == [{"kind": "escalates_to", "to": "beta", "about": "a blocker"}]
    assert builder_role["edges"] == [{"kind": "delegates_to", "to": "scout", "about": "what to look up"}], "the organization response carries the domain and Role declarations used by the edge table"
    assert status == 200 and shown["version"] and shown["problems"] == [] and "guidance" not in builder_role, "the answer holds the version, the problems and the Roles without their long guidance"
    status, builder_contract = get_answer(app, "/journal/organization/roles/alpha/builder", env)
    assert status == 200 and builder_contract["guidance"] == "Guidance of builder.\n" and builder_contract["outputs"] == ["a report"], "a Role detail includes its AGENTS.md and whole contract"
    story_points = {"total": None, "done": None, "sized_tasks": 0, "unknown_tasks": 3}
    assert (alpha["plans_active"], builder_role["instances"], builder_role["queued"]) == (1, 1, 1) and alpha["plans"] == [{"id": plan.id, "title": "the floors", "phase": "planned", "phase_name": "Planned", "mode": "solo", "state": "draft", "active": True, "tasks": [built.id, looked.id], "done": 0, "story_points": story_points, "waits_on": "Role work", "waiting_on_you": False, "plan_agent_state": "not started", "chat": "", "estimated_api_cost_usd": None, "estimated_api_cost_status": "missing", "cost_cap_usd": 0}], "with the counts and the board of plans"
    assert beta["plans"] == [{"id": plan.id, "title": "the floors", "phase": "done", "phase_name": "Done", "mode": "solo", "state": "draft", "active": False, "tasks": [kept.id], "done": 1, "story_points": story_points, "waits_on": "", "waiting_on_you": False, "plan_agent_state": "not started", "chat": "", "estimated_api_cost_usd": None, "estimated_api_cost_status": "missing", "cost_cap_usd": 0}], "the same plan has a separate card in beta's phase with only beta's progress"
    listed = get_answer(app, "/journal/domain_counts", env)[1]["rows"]
    assert {row["name"] for row in listed} == {"alpha", "beta"}, "the counts are rows of a table the viewer's sync carries"
    status, reloaded = answered(app, "POST", "/journal/organization/reload", b"{}", env)
    assert status == 200 and reloaded["version"] == shown["version"]
    with app.container.get(Scope).environment(1):
        domains = app.container.get(DomainRows)
        domains.task_tied(tasks.find(built.id), "beta", actor)
        app.runtime().deferred.drain()
        assert {row.name: row.plans_active for row in counts.all_matching()} == {"alpha": 1, "beta": 1}, "alpha still holds the queued task"
        domains.task_tied(tasks.find(looked.id), "beta", actor)
        app.runtime().deferred.drain()
        assert {row.name: row.plans_active for row in counts.all_matching()} == {"alpha": 0, "beta": 1}, "a task handed on to another domain's Role leaves the domain it came from at once"
        queued = {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["queued"]
        tasks.unqueued(Ref.build(builder), actor)
        app.runtime().deferred.drain()
        assert tasks.queue(Ref.build(builder)) == [], "unqueuing removes every task from the shared Role's queue"
        assert queued == 1 and {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["queued"] == 0, "a queue emptied is counted again"
        assert {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["instances"] == 1, "the active builder instance is still counted before deletion"
        workers.delete(workers.find(builder.id), actor)
        app.runtime().deferred.drain()
        assert {row.name: row.roles for row in counts.all_matching()}["alpha"]["builder"]["instances"] == 0, "deleting an active instance immediately changes its domain's figure"


def test_organization_plan_cards_report_the_recorded_estimated_api_cost_or_none(app, tmp_path):
    from journal.features.organization.support.usage_ledger import UsageLedger
    from journal.models.link import Link
    from journal.models.support.ref import Ref
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.support.time_source import TimeSource
    from tests.in_process import get_answer

    loaded(app, tmp_path)
    plans, tasks, links, domains = (app.container.get(kind) for kind in (Plans, Tasks, Links, DomainRows))
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        reported = plans.save(Plan(environment_id=1, title="reported cost"), actor)
        missing = plans.save(Plan(environment_id=1, title="missing cost"), actor)
        for plan in (reported, missing):
            task = tasks.save(Task(environment_id=1, title=f"task for {plan.title}"), actor)
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
            domains.task_tied(task, "alpha", actor)
        now = app.container.get(TimeSource).seconds()
        app.container.get(UsageLedger).observe(reported.id, "builder@release", "native-session", 2.375, now)

    status, shown = get_answer(app, "/journal/organization", {"X-Journal-Env": "main"})
    alpha = next(domain for domain in shown["domains"] if domain["id"] == "alpha")
    cards = {plan["title"]: plan for plan in alpha["plans"]}
    assert status == 200 and cards["reported cost"]["estimated_api_cost_usd"] == 2.375, "the card carries the recorded estimated API cost"
    assert cards["missing cost"]["estimated_api_cost_usd"] is None, "a card without a recorded estimate says it is not reported"


def test_an_organization_plan_team_serves_its_rig_seats_states_costs_and_caps(app, tmp_path):
    from journal.features.organization.support.usage_ledger import UsageLedger
    from journal.models.link import Link
    from journal.models.rig import Rig
    from journal.models.support.ref import Ref
    from journal.repositories.links import Links
    from journal.repositories.plans import PLAN_LINK, Plans
    from journal.repositories.rigs import Rigs
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import Tasks
    from journal.repositories.workers import Workers
    from journal.support.time_source import TimeSource
    from tests.in_process import get_answer

    _fixture, organization = loaded(app, tmp_path)
    organization.reload()
    user_set(app, "workers.seat_cap", 7)
    user_set(app, "workers.cost_cap_dollars", 18.5)
    plans, rigs, tasks, workers, links = (app.container.get(kind) for kind in (Plans, Rigs, Tasks, Workers, Links))
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        plan = plans.save(Plan(environment_id=1, title="Lay the floors", mode=PlanMode.ORGANIZATION), actor)
        rig = rigs.save(Rig(environment_id=1, name=f"plan-{plan.id}"), actor)
        plans.rig_linked(plan, rig, actor)

        working = tasks.save(Task(environment_id=1, title="Lay the first boards"), actor)
        waiting = tasks.save(Task(environment_id=1, title="Check the boards"), actor)
        for task in (working, waiting):
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
        builder = workers.save(Worker(environment_id=1, name="Ada Lovelace", brief="Lay the boards", profile="journal-senior", role="builder", plan_id=plan.id), actor)
        scout = workers.save(Worker(environment_id=1, name="Grace Hopper", brief="Check the boards", profile="journal-medior", role="scout"), actor)
        tasks.handover(working, Ref.build(builder), actor)
        tasks.queued(waiting, Ref.build(scout), actor)

        spec = {
            "pods": [
                {"id": "plan", "members": [{"id": "plan-agent"}]},
                {"id": "alpha", "members": [
                    {"id": "domain-agent"},
                    {"id": f"builder-{builder.id}", "role": "builder"},
                ]},
                {"id": "beta", "members": [{"id": "domain-agent"}, {"id": "keeper", "role": "keeper"}]},
            ],
        }
        path = app.config.home / "runtime" / "rigs" / rig.name / "rig.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(spec))
        now = app.container.get(TimeSource).seconds()
        seat = f"alpha-builder-{builder.id}@{rig.name}"
        app.container.get(UsageLedger).observe(plan.id, seat, "native-session", 3.25, now)

    status, answer = get_answer(app, f"/journal/plans/{plan.id}/team", {"X-Journal-Env": "main"})
    assert status == 200
    domains = {domain["id"]: {seat["role_id"]: seat for seat in domain["seats"]} for domain in answer["domains"]}
    builder_seat = domains["alpha"]["builder"]
    scout_seat = domains["alpha"]["scout"]
    keeper_seat = domains["beta"]["keeper"]
    assert (builder_seat["state"], builder_seat["task_id"], builder_seat["task_title"]) == ("working", working.id, working.title)
    assert builder_seat["estimated_api_cost_usd"] == 3.25, "the many Role seat carries its recorded ledger estimate"
    assert (scout_seat["state"], scout_seat["task_id"], scout_seat["shared"]) == ("waiting", waiting.id, True), "a shared Role seat names the plan task waiting in its queue"
    assert (keeper_seat["state"], keeper_seat["task_id"], keeper_seat["estimated_api_cost_usd"]) == ("idle", None, None), "an unstated seat is idle and its unmeasured cost stays explicit"
    assert answer["seat_cap"] == 7 and answer["cost_cap_usd"] == 18.5
    assert answer["estimated_api_cost_usd"] == 3.25, "the plan estimate uses its recorded seat amount"

    from journal.http.sharing.shared_data import SharedData

    with app.container.get(Scope).environment(1):
        shared = app.container.get(SharedData).opened(Ref.build(plan))["plans"][0]
    assert shared["plan_team"] == answer, "a shared plan preloads the same Team projection for read-only viewing"


@pytest.mark.parametrize(
    ("schedule", "expected"),
    [
        ("daily", (2026, 10, 30)),
        ("weekly", (2026, 11, 2)),
        ("monthly", (2026, 11, 1)),
        ("quarterly", (2027, 1, 1)),
    ],
)
def test_plan_template_next_start_is_the_next_local_period(schedule, expected):
    from datetime import datetime
    from journal.models.template_schedule import TemplateSchedule

    last = datetime(2026, 10, 29, 15).astimezone()
    next_start = TemplateSchedule(schedule).next_start(last, last)
    assert (next_start.year, next_start.month, next_start.day) == expected and (next_start.hour, next_start.minute) == (0, 0)


def test_home_plan_board_lists_every_plan_with_its_recorded_cost_cap_and_scheduled_next_start(app, tmp_path):
    from journal.features.organization.support.usage_ledger import UsageLedger
    from journal.models.link import Link
    from journal.models.plan import Plan
    from journal.models.support.ref import Ref
    from journal.models.task import Task
    from journal.models.template import PLAN_TARGET, Template
    from journal.models.template_schedule import TemplateSchedule
    from journal.repositories.domain_rows import DomainRows
    from journal.repositories.links import Links
    from journal.repositories.plans import Plans
    from journal.repositories.scope import Scope
    from journal.repositories.tasks import PLAN_LINK, Tasks
    from journal.repositories.templates import Templates
    from journal.support.actor import Actor
    from journal.support.time_source import TimeSource
    from tests.in_process import get_answer
    from tests.user_settings import user_set

    loaded(app, tmp_path)
    user_set(app, "workers.cost_cap_dollars", 5)
    plans, tasks, links, domains, templates = (app.container.get(kind) for kind in (Plans, Tasks, Links, DomainRows, Templates))
    actor = Actor.system()
    with app.container.get(Scope).environment(1):
        domain_plan = plans.save(Plan(environment_id=1, title="Domain plan"), actor)
        solo_plan = plans.save(Plan(environment_id=1, title="Solo plan without a domain"), actor)
        for plan in (domain_plan, solo_plan):
            task = tasks.save(Task(environment_id=1, title=f"Task for {plan.title}"), actor)
            links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), actor)
            if plan == domain_plan:
                domains.task_tied(task, "alpha", actor)
        now = app.container.get(TimeSource).seconds()
        app.container.get(UsageLedger).observe(domain_plan.id, "builder@release", "native-session", 2.375, now)
        waiting_plan = plans.save(Plan(environment_id=1, title="Waiting for approval"), actor)
        plans.save(waiting_plan.ready(now), actor)
        scheduled = templates.save(Template(title="Nightly report", targets=(PLAN_TARGET,)).scheduled(TemplateSchedule.DAILY), actor)
        next_start = scheduled.schedule.next_start(scheduled.update_time, app.container.get(TimeSource).moment()).isoformat()

    status, shown = get_answer(app, "/journal/organization", {"X-Journal-Env": "main"})
    cards = {plan["title"]: plan for plan in shown["plans"]}
    assert status == 200 and set(cards) == {"Domain plan", "Solo plan without a domain", "Waiting for approval"}, "Home includes each plan once, including plans with no domain Role work"
    assert cards["Domain plan"]["estimated_api_cost_usd"] == 2.375 and cards["Domain plan"]["cost_cap_usd"] == 5.0
    assert cards["Domain plan"]["estimated_api_cost_status"] == "estimated" and cards["Domain plan"]["plan_agent_state"] == "not started"
    assert cards["Solo plan without a domain"]["estimated_api_cost_usd"] is None and cards["Solo plan without a domain"]["phase"] == "planned"
    assert cards["Waiting for approval"]["waiting_on_you"] and cards["Waiting for approval"]["waits_on"] == "your approval"
    assert shown["scheduled_plans"] == [{"id": scheduled.id, "title": "Nightly report", "schedule": "daily", "next_start": next_start}], "scheduled plan templates include their next start"
