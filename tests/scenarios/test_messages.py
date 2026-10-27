from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from tests.state_fixtures.task_in_hand import TaskInHand


def test_a_message_read_and_not_answered_holds_every_tool_until_the_agent_replies(scenario):
    scenario.starts_from(TaskInHand)
    scenario.user_sets(MessagesOptions.TOOL_BLOCK_LIMIT, 2)
    message = scenario.user_sends_message("are you there?")
    scenario.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=message)

    scenario.agent_runs(f"message read {message}")
    scenario.expect_agent_told(MessagesNudges.MESSAGE_READ, n=message)
    scenario.agent_reads("a.py")
    scenario.agent_reads("a.py")
    scenario.agent_reads("a.py")
    scenario.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK)

    scenario.agent_replies(message, "yes, on the footer")
    scenario.expect_agent_told(MessagesNudges.REPLY_REPEAT_WARNING, n=message)
    scenario.agent_reads("a.py")
    scenario.expect_allowed()
