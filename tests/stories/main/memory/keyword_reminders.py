from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reminder_its_keyword_names_is_typed_once_however_often_the_word_comes_up(story):
    story.agent_runs(story.agents.subject, "reminder create 'the login uses the old session store' --keywords login")
    login = story.created_number("reminder")
    story.agent_closes_its_turn(story.agents.subject, "I will look at the login next.")
    story.agent_closes_its_turn(story.agents.subject, "Still on the login.")
    story.expect_typed_nudge(MemoryNudges.MEMORY_READ_REQUEST, noun="reminder", n=login)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_struck_reminder_matches_no_keyword(story):
    story.agent_runs(story.agents.subject, "reminder create 'billing runs on the first of the month' --keywords billing")
    billing = story.created_number("reminder")
    story.agent_runs(story.agents.subject, f"reminder strike {billing}")
    story.agent_closes_its_turn(story.agents.subject, "Now the billing.")
    story.expect_typed_nudge(MemoryNudges.MEMORY_READ_REQUEST, count=0, noun="reminder", n=billing)
    story.expect_stack(story.agents.subject, Ready)
