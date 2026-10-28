from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EVERY = 3


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reminder_with_an_interval_is_sent_again_each_time_it_passes(story):
    story.agent_runs(f"reminder create 'commit what you have' --every-tool-uses {EVERY}")
    reminder = story.created_number("reminder")
    story.agent_reads(count=EVERY - 1)
    story.expect_agent_not_told(MemoryNudges.REMINDER_REPEATED, n=reminder)
    story.agent_reads()
    story.expect_agent_told(MemoryNudges.REMINDER_REPEATED, n=reminder)
    story.agent_reads(count=EVERY - 1)
    story.expect_agent_not_told(MemoryNudges.REMINDER_REPEATED, n=reminder)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_struck_reminder_is_never_sent_again_and_one_is_by_minutes_or_tool_uses_not_both(story):
    story.agent_runs(f"reminder create x --every-tool-uses {EVERY} --every-minutes 5")
    story.expect_command_refused()
    story.agent_runs(f"reminder create 'commit what you have' --every-tool-uses {EVERY}")
    reminder = story.created_number("reminder")
    story.agent_runs(f"reminder strike {reminder}")
    story.agent_reads(count=EVERY + 1)
    story.expect_agent_not_told(MemoryNudges.REMINDER_REPEATED, n=reminder)
    story.expect_stack(Ready)
