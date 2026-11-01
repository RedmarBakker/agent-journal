from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_open_viewer_tab_follows_the_environment_started_by_the_launcher(story):
    story.another_environment("task-1")
    result = story.user_opens_viewer_in("task-1")
    result.expect_viewer_shows("open", True)
    result = story.launcher_starts_viewer_in("main")
    result.expect_viewer_text("asked the open tab to use main")
    result = story.viewer_stream_receives_environment_switch("task-1")
    result.expect_viewer_text("environment-switch")
    result.expect_viewer_text("main")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_message_to_an_environment_without_a_live_agent_says_where_one_is_running(story):
    environment = story.another_environment("task-1")
    result = story.user_sends_message_in(environment, "Please start this work")
    result.expect_viewer_text("No agent is running in task-1. A live agent is running in main.")
    story.expect_stack(story.agents.subject, Ready)
