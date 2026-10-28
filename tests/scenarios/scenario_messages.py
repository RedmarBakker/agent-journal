from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from tests.scenarios.builder.stack_states import FOLLOWING_SEQUENCE, IDLE
from tests.scenarios.builder.story_values import scenario, values, values_of
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
@values_of(MessagesOptions.TOOL_BLOCK_LIMIT)
def test_an_unanswered_message_holds_tools_until_the_reply(scenario, value):
    scenario.user_sets(MessagesOptions.TOOL_BLOCK_LIMIT, value)
    message = scenario.user_sends_message("are you there?")
    scenario.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=message)

    scenario.agent_runs(f"message read {message}")
    scenario.expect_agent_told(MessagesNudges.MESSAGE_READ, n=message)
    scenario.agent_consumes(MessagesOptions.TOOL_BLOCK_LIMIT)
    scenario.agent_reads()
    scenario.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK)

    scenario.agent_replies(message, "yes, on the footer")
    scenario.expect_agent_told(MessagesNudges.REPLY_REPEAT_WARNING, n=message)
    scenario.agent_reads()
    scenario.expect_allowed()


@scenario(AgentAtWork)
@values(range(1, 4))
def test_arriving_messages_count_down_to_the_write_hold(scenario, value):
    sent = [scenario.user_sends_message(f"message {count}") for count in range(value)]
    scenario.agent_reads()
    scenario.expect_agent_told(MessagesNudges.INBOX_COUNTDOWN, messages=", ".join(str(message) for message in sent))
    scenario.agent_runs("message unread")
    for message in sent:
        scenario.expect_agent_told(MessagesNudges.MESSAGE_READ, n=message)


@scenario(AgentAtWork, end=[IDLE, FOLLOWING_SEQUENCE])
def test_a_comment_on_a_document_asks_for_the_change_in_the_document(scenario):
    document = scenario.agent_writes_a_document("the footer", "## Layout\n\nThe footer holds the links.\n")
    comment = scenario.user_comments_on("docs", document, "put the copyright in the footer too")
    scenario.agent_runs(f"message read {comment}")
    scenario.expect_agent_told(MessagesNudges.COMMENT_READ, n=comment)


@scenario(AgentAtWork)
def test_the_users_reaction_to_a_reply_is_told_to_the_agent(scenario):
    message = scenario.user_sends_message("is the footer done?")
    reply = scenario.agent_replies_with_number(message, "it is")
    scenario.user_reacts(reply, "🎉")
    scenario.expect_agent_told(MessagesNudges.USER_REACTION, n=reply)


@scenario(AgentAtWork)
def test_an_unread_message_is_named_at_the_stop(scenario):
    message = scenario.user_sends_message("one more thing")
    scenario.agent_stops()
    scenario.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=message)
