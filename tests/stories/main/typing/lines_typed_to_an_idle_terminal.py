from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.message_to_stopped_agent import MessageToStoppedAgent
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(MessageToStoppedAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_woken_agents_prompt_carries_the_line_and_its_next_stop_is_woken_again_by_the_next_line(story):
    story.agent_is_woken_by_the_typed_line(story.agents.subject)
    story.expect_last_answer_carries(MessagesNudges.NEW_MESSAGE, n=story.messages.first)
    story.agent_runs(story.agents.subject, f"message read {story.messages.first}")
    story.agent_stops(story.agents.subject)
    story.user_sends_message("and the header?")
    story.expect_woken(1)
    story.expect_stack(story.agents.subject, Ready)


@story(MessageToStoppedAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_second_line_before_the_woken_agents_prompt_types_nothing_more_and_rides_that_prompt_with_the_first(story):
    second = story.user_sends_message("and the header?")
    story.expect_woken(0)
    story.agent_is_woken_by_the_typed_line(story.agents.subject)
    story.expect_last_answer_carries(MessagesNudges.NEW_MESSAGE, n=story.messages.first)
    story.expect_last_answer_carries(MessagesNudges.NEW_MESSAGE, n=second)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_line_for_a_working_agent_quiet_past_the_foreground_time_is_never_typed_and_rides_its_next_hook(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_is_quiet_past(story.agents.subject, FOREGROUND_OPTION.default)
    story.expect_woken(0)
    story.agent_reads(story.agents.subject)
    story.expect_last_answer_carries(MessagesNudges.NEW_MESSAGE, n=message)
    story.expect_stack(story.agents.subject, Ready)
