from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from tests.scenarios.builder.story_values import values, values_of
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@values_of(MessagesOptions.TOOL_BLOCK_LIMIT)
def test_a_message_read_and_not_answered_holds_every_tool_after_its_grace_uses_until_the_agent_replies(scenario, value):
    scenario.starts_from(TaskInHand)
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


@values(range(1, 4))
def test_each_message_that_arrives_while_the_agent_works_is_counted_down_to_the_write_hold_at_its_next_tool_use(scenario, value):
    scenario.starts_from(TaskInHand)
    sent = [scenario.user_sends_message(f"message {count}") for count in range(value)]
    scenario.agent_reads()
    scenario.expect_agent_told(MessagesNudges.INBOX_COUNTDOWN, messages=", ".join(str(message) for message in sent))
    scenario.agent_runs("message unread")
    for message in sent:
        scenario.expect_agent_told(MessagesNudges.MESSAGE_READ, n=message)
