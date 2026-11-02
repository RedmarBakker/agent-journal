from pathlib import Path

from journal.engine.states.ended import Ended
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.plans_options import PlansOptions
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.supervisor_link import SupervisorLink
from journal.support.agent_role import AgentRole
from journal.support.worktree import Worktree
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.plan_agent_worktree_project import PlanAgentWorktreeProject
from tests.stories.fixtures.main.solo_plan_with_first_task_complete import SoloPlanWithFirstTaskComplete
from tests.stories.fixtures.main.started_solo_plan_branch import PLAN_AGENT_SESSION, StartedSoloPlanBranch


def write_installed_file(tree: Worktree, name: str, text: str) -> None:
    worktree_file = tree.path
    path = Path(name)
    for part in path.parts[:-1]:
        worktree_file /= part
        if worktree_file.is_symlink():
            worktree_file.unlink()
        worktree_file.mkdir(exist_ok=True)
    target = worktree_file / path.name
    if target.is_symlink():
        target.unlink()
    target.write_text(text)


def start_plan_agent(story, plan: int, source: str, source_session: str) -> tuple[str, str, Worktree]:
    root = story.app.config.root
    result = story.agent_in_runs(story.agents.subject, source, source_session, f"plan start {plan}")
    result.expect_command_passed()
    environment = story.app.container.get(Environments).existing(f"plan-{plan}")
    story.session_starts_in(environment.name, PLAN_AGENT_SESSION)
    tree = WorkspaceWorktree.chosen(root, environment.name)
    tree.created()
    result = story.agent_in_runs(story.agents.subject, environment.name, PLAN_AGENT_SESSION, f"plan start {plan}")
    result.expect_command_passed()
    return environment.name, PLAN_AGENT_SESSION, tree


def commit_plan_change(story, tree: Worktree) -> None:
    change = tree.path / "PLAN-AGENT-SMOKE.md"
    change.write_text("completed solo plan change\n")
    story.git_in(change.parent, "add", change.name)
    story.git_in(change.parent, "commit", "-q", "-m", "finish plan change")


def complete_plan_tasks(story, environment: str, session: str, tasks: tuple[int, ...]) -> None:
    for task in tasks:
        result = story.agent_in_runs(story.agents.subject, environment, session, f"task complete {task} --how done")
        result.expect_command_passed()


@story(StartedSoloPlanBranch, subject=AgentRole.MAIN)
def test_a_finished_plan_merges_past_updated_journal_files(story):
    root, plan = story.app.config.root, story.plans.first
    environment, session, tree = f"plan-{plan}", PLAN_AGENT_SESSION, WorkspaceWorktree.chosen(root, f"plan-{plan}")
    updated = (
        (".agents/skills/journal-plan/SKILL.md", "updated journal skill\n"),
        (".claude/skills/journal-plan/SKILL.md", "updated Claude journal skill\n"),
        (".codex/agents/journal-plan.toml", "updated journal profile\n"),
        (".claude/agents/journal-plan.md", "updated Claude agent profile\n"),
        (".codex/hooks.json", '{"hooks": {"journal": true}}\n'),
        ("AGENTS.md", "updated journal instructions\n"),
        ("CLAUDE.md", "@AGENTS.md\n"),
    )
    for name, text in updated:
        write_installed_file(tree, name, text)
    story.observed("the journal updates installed files in the plan worktree", None, None)
    complete_plan_tasks(story, environment, session, (story.tasks.first, story.tasks.second))

    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_project_file_is("PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_no_project_file(f".claude/worktrees/plan-{plan}")
    story.expect_stack(story.agents.subject, CoordinatingPlans)


@story(SoloPlanWithFirstTaskComplete, subject=AgentRole.MAIN)
def test_a_finished_plan_stops_its_running_agent_before_merging(story):
    plan = story.plans.first
    environment, session = f"plan-{plan}", PLAN_AGENT_SESSION
    plan_environment = story.app.container.get(Environments).existing(environment)
    running = True

    def agent_is_running(_link: SupervisorLink, environment_id: int) -> bool:
        return environment_id == plan_environment.row_id and running

    def stop_agent(_link: SupervisorLink, _environment_id: int) -> None:
        nonlocal running
        running = False

    story.monkeypatch.setattr(SupervisorLink, "runs", agent_is_running)
    story.monkeypatch.setattr(SupervisorLink, "stop", stop_agent)
    story.observed("the Plan agent's supervisor is running", None, None)
    complete_plan_tasks(story, environment, session, (story.tasks.second,))

    notice = (
        f"Plan {plan} branch merge failed: plan {plan}'s Plan agent is still running: wait for it to stop before merging. "
        f"Review the named files in the plan worktree and main, resolve the issue, then run `journal plan merge {plan}` in main."
    )
    result = story.user_opens_in("main", "/journal/messages")
    result.expect_viewer_passed()
    result.expect_viewer_rows_not_holding("rows", "text", notice)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_project_file_is("PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_no_project_file(f".claude/worktrees/{environment}")
    story.expect_stack(StoryAgent(AgentRole.MAIN, session=session), LeadingPlan, Ended)
    story.expect_stack(story.agents.subject, CoordinatingPlans)


@story(SoloPlanWithFirstTaskComplete, subject=AgentRole.MAIN)
def test_a_finished_plan_conflict_is_explained_in_both_chats(story):
    root, plan = story.app.config.root, story.plans.first
    environment, session = f"plan-{plan}", PLAN_AGENT_SESSION
    change = root / "PLAN-AGENT-SMOKE.md"
    change.write_text("the project version\n")
    story.git_in(root, "add", change.name)
    story.git_in(root, "commit", "-q", "-m", "project change")
    complete_plan_tasks(story, environment, session, (story.tasks.second,))

    notice = (
        f"Plan {plan} branch merge failed: plan {plan}'s work was not merged: conflict in PLAN-AGENT-SMOKE.md in the project. "
        f"Review the named files in the plan worktree and main, resolve the issue, then run `journal plan merge {plan}` in main."
    )
    result = story.user_opens_in("main", "/journal/messages")
    result.expect_viewer_passed()
    result.expect_viewer_rows_holding("rows", "text", notice)
    result = story.user_opens_in(environment, "/journal/messages")
    result.expect_viewer_passed()
    result.expect_viewer_rows_holding("rows", "text", notice)
    story.expect_plan(plan, state=PlanState.FINISHED)
    story.expect_project_file_is("PLAN-AGENT-SMOKE.md", "the project version\n")
    story.expect_project_file_is(f".claude/worktrees/{environment}/PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_stack(story.agents.subject, CoordinatingPlans)


@story(PlanAgentWorktreeProject, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_finished_plan_started_from_a_worktree_merges_into_that_environment_branch(story):
    root = story.app.config.root
    source = story.another_environment("smoke-1")
    source_tree = WorkspaceWorktree.chosen(root, source)
    source_tree.created()
    base = source_tree.path / "starting-environment.md"
    base.write_text("kept on the starting environment branch\n")
    story.git_in(base.parent, "add", base.name)
    story.git_in(base.parent, "commit", "-q", "-m", "starting environment work")

    result = story.user_presses_in(source, "/journal/plans", {"title": "the worktree plan", "brief": "complete its task"})
    result.expect_viewer_passed()
    plan = result.viewer_answer["id"]
    result = story.user_presses_in(source, f"/journal/plans/{plan}/tasks", {"title": "finish the work", "brief": "- the work is done"})
    result.expect_viewer_passed()
    task = result.viewer_answer["id"]
    result = story.user_presses_in(source, f"/journal/plans/{plan}/mode", {"mode": "solo"})
    result.expect_viewer_passed()
    result = story.user_presses_in(source, f"/journal/plans/{plan}/approve", {})
    result.expect_viewer_passed()

    source_session = "smoke-agent-session"
    story.session_starts_in(source, source_session)
    environment, session, tree = start_plan_agent(story, plan, source, source_session)
    commit_plan_change(story, tree)
    complete_plan_tasks(story, environment, session, (task,))

    story.expect_project_file_is(f".claude/worktrees/{source}/starting-environment.md", "kept on the starting environment branch\n")
    story.expect_project_file_is(f".claude/worktrees/{source}/PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_no_project_file("PLAN-AGENT-SMOKE.md")
    story.expect_no_project_file(f".claude/worktrees/{environment}")
    story.expect_stack(story.agents.subject, CoordinatingPlans)
