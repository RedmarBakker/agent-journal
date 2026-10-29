from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage


@story(ReadMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_closing_words_after_a_reply_in_the_same_turn_are_named_back_once_at_the_stop(story):
    story.agent_is_prompted(story.agents.subject, "is the footer done?")
    reply = story.agent_replies_with_number(story.agents.subject, story.messages.first, "the footer is done")
    story.expect_agent_told(story.agents.subject, MessagesNudges.REPLY_REPEAT_WARNING, n=story.messages.first, reply=reply)
    story.expect_message(reply, author="agent", reply_target=story.messages.first)
    story.agent_closes_its_turn(story.agents.subject, "next I start the header")
    story.agent_closes_its_turn(story.agents.subject, "and then the logo")
    story.agent_stops(story.agents.subject)
    story.expect_last_answer_carries(MessagesNudges.REPLY_CLOSING_WORDS, reply=reply)
    story.expect_newest_agent_message("the footer is done")
    story.agent_stops_again(story.agents.subject)
    story.expect_last_answer_without(MessagesNudges.REPLY_CLOSING_WORDS, reply=reply)
    story.expect_stack(story.agents.subject, Ready)


@story(ReadMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_closing_words_of_a_later_turn_than_the_reply_reach_the_chat_and_are_not_named_back(story):
    reply = story.agent_replies_with_number(story.agents.subject, story.messages.first, "the footer is done")
    story.agent_is_prompted_in_a_new_turn(story.agents.subject, "go on")
    story.agent_closes_its_turn(story.agents.subject, "next I start the header")
    story.expect_newest_agent_message("next I start the header")
    story.agent_stops(story.agents.subject)
    story.expect_last_answer_without(MessagesNudges.REPLY_CLOSING_WORDS, reply=reply)
    story.expect_stack(story.agents.subject, Ready)
