from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_launcher_starts_a_new_environment_in_its_own_worktree_when_main_holds_the_branch(story):
    story.project_is_a_git_repository()
    result = story.launcher_starts_new_environment_with_live_main("smoke-1")
    result.expect_launcher_prompt(
        "Start smoke-1 in its own worktree?",
        "Yes, start in a worktree",
        "Choose another environment",
        default=0,
    )
    result.expect_launcher_started_in_worktree("smoke-1")
    story.expect_stack(story.agents.subject, Ready)
