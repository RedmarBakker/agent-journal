from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from tests.scenarios.builder.story_values import starts_from, values, values_of
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
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


@starts_from(TaskInHand)
@values(range(1, 4))
def test_arriving_messages_count_down_to_the_write_hold(scenario, value):
    sent = [scenario.user_sends_message(f"message {count}") for count in range(value)]
    scenario.agent_reads()
    scenario.expect_agent_told(MessagesNudges.INBOX_COUNTDOWN, messages=", ".join(str(message) for message in sent))
    scenario.agent_runs("message unread")
    for message in sent:
        scenario.expect_agent_told(MessagesNudges.MESSAGE_READ, n=message)
