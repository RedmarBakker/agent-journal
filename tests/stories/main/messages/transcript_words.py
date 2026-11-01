from journal.features.messages.messages_options import MessagesOptions
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

TICK_SECONDS = 1


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_words_the_hooks_missed_are_swept_in_once_and_the_newest_are_left_to_the_next_hook(story):
    story.agent_has_written(story.agents.subject, "Hello.", seconds_ago=story.setting(MessagesOptions.TRANSCRIPT_SCAN_DELAY) * 3)
    story.agent_reads(story.agents.subject)
    story.agent_has_written(story.agents.subject, "Missed by every hook.", seconds_ago=story.setting(MessagesOptions.TRANSCRIPT_SCAN_DELAY) * 2)
    story.agent_has_written(story.agents.subject, "Still the hooks' to bring.")
    story.clock_ticks(TICK_SECONDS)
    story.clock_ticks(TICK_SECONDS)
    story.expect_agent_messages(2)
    story.expect_newest_agent_message("Missed by every hook.")
    story.agent_reads(story.agents.subject)
    story.expect_agent_messages(3)
    story.expect_newest_agent_message("Still the hooks' to bring.")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_words_written_before_a_tool_call_reach_the_chat_at_that_call_and_the_display_hook_adds_no_second(story):
    story.agent_has_written(story.agents.subject, "Here, and writing.")
    story.agent_writes(story.agents.subject, "a.py")
    story.expect_agent_messages(1)
    story.expect_newest_agent_message("Here, and writing.")
    story.agent_closes_its_turn(story.agents.subject, "Here, and writing.")
    story.expect_agent_messages(1)
    story.expect_stack(story.agents.subject, Ready)
