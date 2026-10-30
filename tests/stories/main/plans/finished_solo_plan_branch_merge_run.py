"""Runs Git in a throwaway project to show a finished Plan agent's branch merged by the journal."""
import json

from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.builder.story_marks import BUILDER_MODE, setting, story
from tests.stories.fixtures.main.finished_solo_plan_with_branch import FinishedSoloPlanWithBranch
from tests.stories.fixtures.main.finished_solo_plan_with_branch_before_merge import FinishedSoloPlanWithBranchBeforeMerge
from tests.stories.fixtures.main.plan_approved import PlanApproved


def plan_worktree(story):
    return WorkspaceWorktree.chosen(story.app.config.root, f"plan-{story.plans.first}")


@story(FinishedSoloPlanWithBranch, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_solo_plan_merges_its_work_into_the_project(story):
    story.expect_project_file_is("PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_no_project_file(".claude/worktrees/plan-1")
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(FinishedSoloPlanWithBranchBeforeMerge, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_solo_plan_merges_while_leaving_its_generated_settings_out(story):
    tree = plan_worktree(story)
    settings = tree.path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps({
        "enableAllProjectMcpServers": True,
        "statusLine": {
            "type": "command",
            "command": f"sh {story.app.config.root}/.journal/src/journal/hooks/status.sh",
            "padding": 0,
        },
    }))
    hooks = tree.path / ".codex" / "hooks.json"
    hooks.parent.mkdir(parents=True, exist_ok=True)
    hooks.write_text("{}\n")
    story.observed("journal setup leaves generated settings in the plan worktree", None, None)
    merged = story.agent_runs(story.agents.main, f"plan merge {story.plans.first}")
    merged.expect_command_passed()
    merged.expect_command_text("left out its generated settings")
    story.expect_project_file_is("PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_no_project_file(".claude/worktrees/plan-1")
    story.expect_no_project_file(".claude/settings.json")
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(FinishedSoloPlanWithBranchBeforeMerge, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_solo_plan_with_uncommitted_work_keeps_its_worktree(story):
    tree = plan_worktree(story)
    leftover = tree.path / "uncommitted.txt"
    leftover.write_text("still being worked on\n")
    story.observed("the Plan agent leaves an uncommitted file", None, None)
    story.agent_runs(story.agents.main, f"plan merge {story.plans.first}").expect_command_refused()
    story.expect_no_project_file("PLAN-AGENT-SMOKE.md")
    story.expect_project_file_is(".claude/worktrees/plan-1/uncommitted.txt", "still being worked on\n")
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(FinishedSoloPlanWithBranchBeforeMerge, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_finished_solo_plan_keeps_uncommitted_project_settings_for_review(story):
    tree = plan_worktree(story)
    settings = tree.path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text('{"theme": "dark"}\n')
    story.observed("the Plan agent changes project settings", None, None)
    story.agent_runs(story.agents.main, f"plan merge {story.plans.first}").expect_command_refused()
    story.expect_no_project_file("PLAN-AGENT-SMOKE.md")
    story.expect_project_file_is(".claude/worktrees/plan-1/.claude/settings.json", '{"theme": "dark"}\n')
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(FinishedSoloPlanWithBranchBeforeMerge, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_conflict_leaves_the_finished_solo_plan_worktree(story):
    project_file = story.app.config.root / "PLAN-AGENT-SMOKE.md"
    project_file.write_text("the project version\n")
    story.git_in(project_file.parent, "add", project_file.name)
    story.git_in(project_file.parent, "commit", "-q", "-m", "project change")
    story.observed("the project changes the same file", None, None)
    story.agent_runs(story.agents.main, f"plan merge {story.plans.first}").expect_command_refused()
    story.expect_project_file_is("PLAN-AGENT-SMOKE.md", "the project version\n")
    story.expect_project_file_is(".claude/worktrees/plan-1/PLAN-AGENT-SMOKE.md", "completed solo plan change\n")
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_an_unfinished_plan_cannot_be_merged(story):
    story.agent_runs(story.agents.main, f"plan merge {story.plans.first}").expect_command_refused()
    story.expect_plan(story.plans.first, state=PlanState.APPROVED)
    story.expect_stack(story.agents.main, CoordinatingPlans)
