from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EVERY = 3


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_reminder_with_an_interval_is_sent_again_each_time_it_passes(story):
    story.agent_runs(story.agents.subject, f"reminder create 'commit what you have' --every-tool-uses {EVERY}")
    reminder = story.created_number("reminder")
    result = story.agent_reads(story.agents.subject, count=EVERY - 1)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.REMINDER_REPEATED, n=reminder)
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_told(story.agents.subject, MemoryNudges.REMINDER_REPEATED, n=reminder)
    result = story.agent_reads(story.agents.subject, count=EVERY - 1)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.REMINDER_REPEATED, n=reminder)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_struck_reminder_is_never_sent_again_and_one_is_by_minutes_or_tool_uses_not_both(story):
    result = story.agent_runs(story.agents.subject, f"reminder create x --every-tool-uses {EVERY} --every-minutes 5")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"reminder create 'commit what you have' --every-tool-uses {EVERY}")
    reminder = story.created_number("reminder")
    story.agent_runs(story.agents.subject, f"reminder strike {reminder}")
    result = story.agent_reads(story.agents.subject, count=EVERY + 1)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.REMINDER_REPEATED, n=reminder)
    story.expect_stack(story.agents.subject, Ready)
