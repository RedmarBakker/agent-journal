from pathlib import Path

from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_shared_role_file_proved import OrganizationSharedRoleFileProved
from tests.stories.fixtures.main.organization_shared_role_task_clocked_in import OrganizationSharedRoleTaskClockedIn


@story(OrganizationSharedRoleFileProved, subject=AgentRole.MAIN)
def test_a_shared_role_commits_its_file_before_its_task_merges(story):
    worker, task, plan = story.agents.workers.first(), story.tasks.first, story.plans.first
    story.agent_clocks_out(worker, "the shared file is ready").expect_command_passed()

    root = story.app.config.root
    story.expect_commit_in(root, f"Task {task}: first")
    story.expect_project_file_is("SECURITY.md", "The shared Role result is ready.\n")

    domain = story.organization_seat_agent("domain:alpha")
    story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", f"worker check {worker} 1").expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", f"organization handoff {task} plan").expect_command_passed()
    plan_inbox = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox")
    plan_inbox.expect_command_passed()
    merged = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}")
    merged.expect_command_passed()

    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_stack(worker, Void)


@story(OrganizationSharedRoleTaskClockedIn, subject=AgentRole.MAIN)
def test_a_shared_role_that_changes_nothing_closes_without_a_commit(story):
    worker, task, plan = story.agents.workers.first(), story.tasks.first, story.plans.first
    story.agent_proves(worker, 1, "no file changed; the task is complete").expect_command_passed()
    story.agent_clocks_out(worker, "the task is complete without a file change").expect_command_passed()
    root = story.app.config.root
    story.expect_commit_in(root, "start")

    domain = story.organization_seat_agent("domain:alpha")
    story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", f"worker check {worker} 1").expect_command_passed()
    story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", f"organization handoff {task} plan").expect_command_passed()
    story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox").expect_command_passed()
    merged = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}")
    merged.expect_command_passed()

    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_commit_in(root, "start")
    story.expect_no_project_file("SECURITY.md")
    story.expect_stack(worker, Void)


@story(OrganizationSharedRoleFileProved, subject=AgentRole.MAIN)
def test_a_shared_role_commits_only_its_file_when_another_file_is_dirty(story):
    worker, task = story.agents.workers.first(), story.tasks.first
    story.the_project_holds_a_file("OTHER.md", b"another edit is still in progress\n")
    story.agent_clocks_out(worker, "the shared file is ready").expect_command_passed()

    root = story.app.config.root
    story.expect_commit_in(root, f"Task {task}: first")
    story.expect_commit_files_in(root, "SECURITY.md")
    story.expect_uncommitted_files_in(root, "OTHER.md")
    story.expect_project_file_is("SECURITY.md", "The shared Role result is ready.\n")
    story.expect_project_file_is("OTHER.md", "another edit is still in progress\n")
    story.expect_worker(worker, state=WorkerState.DELIVERED)
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_stack(worker, Void)


@story(OrganizationSharedRoleFileProved, subject=AgentRole.MAIN)
def test_a_shared_role_cannot_clock_out_changed_files_that_failed_to_commit(story):
    worker, task = story.agents.workers.first(), story.tasks.first
    hook = story.app.config.root / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    refused = story.agent_runs(worker, "clock-out 'the shared file is ready'")
    refused.expect_command_refused()
    refused.expect_command_text("still not committed after the journal's commit: SECURITY.md")

    story.expect_commit_in(story.app.config.root, "start")
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_worker(worker, state=WorkerState.READY)
    story.expect_project_file_is("SECURITY.md", "The shared Role result is ready.\n")
    story.expect_stack(worker, Void, WorkingTask)
