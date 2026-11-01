from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.task_state import TaskState
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.main_ready_plan import MainReadyPlan
from tests.stories.fixtures.main.main_user_plan import MainUserPlan

PLAN_AGENT_SESSION = "plan-agent-plan-read-session"
WORKTREE_AGENT_SESSION = "worktree-agent-plan-read-session"
WORKTREE_PLAN_AGENT_SESSION = "worktree-plan-agent-read-session"


def prepare_plan_agent_worktrees(story, monkeypatch) -> None:
    root = story.app.config.root
    story.project_is_a_git_repository()
    story.git_in(root, "config", "user.name", "Story")
    story.git_in(root, "config", "user.email", "story@example.com")
    monkeypatch.setattr(
        AgentEnvironments,
        "launched",
        lambda places, environment, agent, repositories=None: WorkspaceWorktree.chosen(root, environment.name, repositories).created(),
    )


def plan_agent_starts(story, plan: int, source: str, source_session: str, session: str) -> tuple[str, str]:
    result = story.agent_in_runs(story.agents.subject, source, source_session, f"plan start {plan}")
    result.expect_command_passed()
    result.expect_command_text(f"plan {plan} started")
    environment = f"plan-{plan}"
    story.session_starts_in(environment, session)
    result = story.agent_in_runs(story.agents.subject, environment, session, "environment overview")
    result.expect_command_passed()
    return environment, session


def plan_agent_lists_and_dispatches(story, environment: str, session: str, plan: int, tasks: tuple[int, ...], titles: tuple[str, ...], phase_title: str, source: str) -> None:
    result = story.agent_in_runs(story.agents.subject, environment, session, "task list")
    result.expect_command_passed()
    for title in titles:
        result.expect_command_text(title)

    result = story.agent_in_runs(story.agents.subject, environment, session, "plan list")
    result.expect_command_passed()
    result.expect_command_text(str(plan))

    result = story.agent_in_runs(story.agents.subject, environment, session, f"plan show {plan}")
    result.expect_command_passed()
    for title in titles:
        result.expect_command_text(title)
    if phase_title:
        result.expect_command_text(phase_title)

    result = story.agent_in_runs(
        story.agents.subject,
        environment,
        session,
        f"worker dispatch 'Lady Lovelace' --task {tasks[0]} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'",
    )
    result.expect_command_passed()
    result.expect_command_text("dispatched on")
    result = story.user_opens_in(source, f"/journal/tasks?ids={tasks[0]}")
    result.expect_viewer_passed()
    result.expect_viewer_rows("rows", "state", [TaskState.OPEN.value])
    result.expect_viewer_rows("rows", "delegated", [True])
    for task in tasks[1:]:
        story.expect_task_in(source, task, TaskState.OPEN.value)


@story(MainReadyPlan, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_plan_agent_started_from_main_reads_its_plan_and_dispatches_its_first_task(story, monkeypatch):
    prepare_plan_agent_worktrees(story, monkeypatch)
    plan, first = story.plans.first, story.tasks.slab
    result = story.agent_runs(story.agents.subject, f"task brief {first} 'the slab is complete'")
    result.expect_command_passed()
    result = story.user_approves_plan(plan)
    result.expect_viewer_passed()

    environment, session = plan_agent_starts(story, plan, "main", story.main_session(), PLAN_AGENT_SESSION)
    plan_agent_lists_and_dispatches(story, environment, session, plan, (first,), ("pour the slab",), "Lay the floor", "main")
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)


@story(MainUserPlan, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_plan_agent_started_from_a_worktree_reads_its_plan_and_dispatches_its_first_task(story, monkeypatch):
    prepare_plan_agent_worktrees(story, monkeypatch)
    root = story.app.config.root
    environments = story.app.container.get(Environments)
    main = environments.existing("main")
    source = environments.made("worker-worktree", Actor.system(), main.key, "worker").name
    story.another_environment(source)
    WorkspaceWorktree.chosen(root, source).created()

    plan = story.user_creates_plan_in(source, "the worktree plan")
    first_result = story.user_presses_in(source, f"/journal/plans/{plan}/tasks", {"title": "the first worktree task", "brief": "- the first task is done"})
    first_result.expect_viewer_passed()
    first = first_result.viewer_answer["id"]
    second_result = story.user_presses_in(source, f"/journal/plans/{plan}/tasks", {"title": "the second worktree task", "brief": "- the second task is done"})
    second_result.expect_viewer_passed()
    second = second_result.viewer_answer["id"]

    story.session_starts_in(source, WORKTREE_AGENT_SESSION)
    result = story.agent_in_runs(story.agents.subject, source, WORKTREE_AGENT_SESSION, f"plan phase {plan} Work --when 'the work is done'")
    result.expect_command_passed()
    result = story.agent_in_runs(story.agents.subject, source, WORKTREE_AGENT_SESSION, f"plan todos {plan} 1 {first} {second}")
    result.expect_command_passed()
    result = story.agent_in_runs(story.agents.subject, source, WORKTREE_AGENT_SESSION, f"plan ready {plan}")
    result.expect_command_passed()
    result = story.user_presses_in(source, f"/journal/plans/{plan}/approve", {})
    result.expect_viewer_passed()

    environment, session = plan_agent_starts(story, plan, source, WORKTREE_AGENT_SESSION, WORKTREE_PLAN_AGENT_SESSION)
    plan_agent_lists_and_dispatches(story, environment, session, plan, (first, second), ("the first worktree task", "the second worktree task"), "Work", source)
    story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
