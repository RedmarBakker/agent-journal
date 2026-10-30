from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

STALE_DAYS = 9


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_keyword_brings_a_reminder_back_once_to_the_agent_that_names_it(story):
    story.user_types("reminder create 'the login uses the old session store' --keywords login,session")
    reminder = story.created_number("reminder")
    result = story.agent_closes_its_turn(story.agents.subject, "I will look at the login next.")
    result.expect_agent_told(story.agents.subject, MemoryNudges.MEMORY_READ_REQUEST, noun="reminder", n=reminder)
    result = story.agent_closes_its_turn(story.agents.subject, "Still on the login.")
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.MEMORY_READ_REQUEST, noun="reminder", n=reminder)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_fresh_start_asks_once_a_day_whether_an_old_reminder_still_holds_and_never_after_a_compaction(story):
    story.user_types("reminder create 'check the api on port 9'")
    story.time_travel(minutes=STALE_DAYS * 24 * 60)
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CHECK_STALE_MEMORY)
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.CHECK_STALE_MEMORY)
    result = story.context_is_compacted()
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.CHECK_STALE_MEMORY)
    story.agent_looks_at_the_overview(story.agents.subject)
    story.expect_stack(story.agents.subject, Ready)
