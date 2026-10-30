from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_users_face_on_a_message_shows_and_the_same_face_again_takes_it_off(story):
    message = story.user_sends_message("hello")
    story.user_presses(f"/journal/messages/{message}/react", {"emoji": "👍"})
    result = story.user_opens("/journal/reactions")
    result.expect_viewer_rows("rows", "emoji", ["👍"])
    story.user_presses(f"/journal/messages/{message}/react", {"emoji": "👍"})
    result = story.user_opens("/journal/reactions")
    result.expect_viewer_rows("rows", "emoji", [])
    story.expect_stack(story.agents.subject, Ready)
