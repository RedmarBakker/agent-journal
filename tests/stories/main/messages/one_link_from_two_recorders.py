from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_made_after_a_reply_and_named_by_the_next_reply_is_one_link_of_the_message(story):
    message = story.user_sends_message("please fix the footer")
    story.agent_replies(story.agents.subject, message, "on it")
    task = story.agent_creates_task(story.agents.subject, "the footer")
    story.agent_runs(story.agents.subject, f"message send 'Filed as task {task}.' --reply-to {message} --confirm")
    story.expect_message(message, filed=[task])
    story.expect_stack(story.agents.subject, Ready)
