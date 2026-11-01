from pathlib import Path

from journal.engine.states.void import Void
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.agent_token import AgentToken
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.organization_setup import OrganizationSetup
from tests.stories.main.plans.plan_agent_reads_its_plan import prepare_plan_agent_worktrees


WORKTREE_AGENT_SESSION = "worktree-organization-role-session"
TASK_BRIEF = "- write source/NOTES.md with the task result"
OLD_BRIEF = "the earlier task brief"


@story(OrganizationSetup, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_role_worker_on_a_worktree_plan_receives_its_job_and_can_prove_and_clock_out(story, monkeypatch):
    prepare_plan_agent_worktrees(story, monkeypatch)
    story.configure_simulated_openrig()
    story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)

    root = story.app.config.root
    environments = story.app.container.get(Environments)
    main = environments.existing("main")
    source = environments.made("worker-worktree", Actor.system(), main.key, "worker").name
    story.another_environment(source)
    WorkspaceWorktree.chosen(root, source).created()
    top, _, option = OrganizationOptions.FOLDER.key.partition(".")
    folder = str(Path(__file__).resolve().parents[3] / "stories" / "fixtures" / "main" / "organization_hub")
    story.user_presses_in(source, "/journal/settings", {top: {option: folder}}).expect_viewer_passed()
    story.user_presses_in(source, "/journal/organization/reload", {}).expect_viewer_passed()

    plan = story.user_creates_plan_in(source, "the worktree organization plan")
    task_result = story.user_presses_in(source, f"/journal/plans/{plan}/tasks", {
        "title": "write the worktree note", "brief": TASK_BRIEF, "domain": "alpha",
    })
    task_result.expect_viewer_passed()
    task = task_result.viewer_answer["id"]
    story.plans.first = plan
    story.tasks.first = task
    task = story.tasks.first

    story.session_starts_in(source, WORKTREE_AGENT_SESSION)
    result = story.agent_in_runs(story.agents.subject, source, WORKTREE_AGENT_SESSION, f"plan mode {plan} organization")
    result.expect_command_passed()
    story.user_presses_in(source, f"/journal/plans/{plan}/approve", {}).expect_viewer_passed()

    rig = story.plan_rig_name(plan)
    contracts = story.app.container.get(Organization).reload()
    provider = story.app.container.get(Providers).lookup(story.provider)
    domains = tuple(domain.id for domain in contracts.domains)
    story.app.container.get(RigSpecs).write(
        rig, contracts, domains, root,
        lambda seat: SeatWorker(Actor.agent(""), AgentToken(f"story-seat-{rig}-{seat.qualified}"), "main", seat.qualified, rig),
        provider,
    )

    result = story.agent_in_runs(story.agents.subject, source, WORKTREE_AGENT_SESSION, f"plan start {plan}")
    result.expect_command_passed()
    result.expect_command_text(f"plan {plan} started")
    story.agent_starts_plan_seat(story.agents.subject, plan).expect_allowed(story.agents.subject)
    story.expect_openrig_seat_environment(story.agents.subject, "plan")

    result = story.agent_runs_from_plan_organization_seat(
        story.agents.subject, "plan", f"organization handoff {task} domain:alpha",
    )
    result.expect_command_passed()
    domain = story.organization_seat_agent_in_plan("domain:alpha", plan)
    story.agent_starts_organization_seat_in_plan(domain, "domain:alpha", plan).expect_allowed(domain)
    inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
    inbox.expect_command_passed()
    inbox.expect_command_text(TASK_BRIEF)
    result = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    result.expect_command_passed()

    worker = StoryAgent(AgentRole.WORKER, number=story.newest_in("workers", source))
    story.expect_worker_role_job(worker, task, TASK_BRIEF, OLD_BRIEF)
    started = story.organization_role_seat_starts_a_session(worker, "role:alpha/builder")
    started.expect_allowed(worker)
    story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()
    read = story.agent_reads_from_organization_role_seat(worker, "role:alpha/builder", "source/NOTES.md")
    read.expect_allowed(worker)
    written = story.agent_writes_from_organization_role_seat(worker, "role:alpha/builder", "source/NOTES.md")
    written.expect_allowed(worker)
    story.expect_agent_session_in_environment(worker, source)
    story.expect_no_user_message_text_in(source, TASK_BRIEF)
    story.expect_role_job_prompt(worker, TASK_BRIEF, OLD_BRIEF, "journal clock-in")
    story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder", "proof 1 'source/NOTES.md:1; tests/stories/main/organization/role_worker_in_worktree_plan.py proves the worktree Role can prove its task'",
    ).expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/builder", "clock-out 'the worktree note is written'",
    ).expect_command_passed()
    story.expect_no_user_message_text_in(source, TASK_BRIEF)
    story.expect_stack(worker, Void)
