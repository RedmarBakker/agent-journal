from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage


@story(ReadMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_old_reply_tag_in_a_turn_is_stripped_answers_nothing_and_tells_the_agent(story):
    story.agent_closes_its_turn(story.agents.subject, f"[!reply:{story.fixture.message}]\nGood evening. At your service.")
    story.expect_newest_agent_message("Good evening. At your service.")
    story.expect_agent_told(story.agents.subject, MessagesNudges.RETIRED_TAGS)
    story.agent_closes_its_turn(story.agents.subject, '[!todo="Fix the footer"]\nThe footer overlaps the form.')
    story.expect_task_count(0)
    story.expect_stack(story.agents.subject, Ready)
