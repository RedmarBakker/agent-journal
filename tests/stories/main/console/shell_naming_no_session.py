from journal.engine.states.ended import Ended
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ended_session import EndedSession
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_command_from_a_shell_naming_no_session_is_the_live_agents(story):
    story.command_from_a_shell_naming_no_session("task create 'the footer'")
    story.expect_task_made_by(story.agents.subject, story.task_number())
    story.expect_stack(story.agents.subject, Ready)


@story(EndedSession, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_command_from_a_shell_naming_no_session_with_no_agent_live_is_the_users(story):
    story.command_from_a_shell_naming_no_session("task create 'the footer'")
    story.expect_task(story.task_number(), creator="user:1")
    story.expect_stack(story.agents.subject, Ready, Ended)
