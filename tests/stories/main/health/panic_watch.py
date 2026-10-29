from journal.features.health.health_nudges import HealthNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ended_session import EndedSession
from tests.stories.fixtures.main.compacting_task import CompactingTask


@story(EndedSession, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_session_start_in_the_journals_own_repository_is_told_to_start_the_panic_watch(story):
    story.the_project_is_the_journals_own_repository()
    story.agent_starts_a_session(story.agents.subject)
    story.expect_agent_told(story.agents.subject, HealthNudges.PANIC_WATCH)
    story.expect_stack(story.agents.subject, Ready)


@story(EndedSession, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_session_start_in_any_other_project_is_never_told_of_the_panic_watch(story):
    story.agent_starts_a_session(story.agents.subject)
    story.expect_agent_not_told(story.agents.subject, HealthNudges.PANIC_WATCH)
    story.expect_stack(story.agents.subject, Ready)


@story(CompactingTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_session_start_after_a_compaction_is_never_told_of_the_panic_watch_again(story):
    story.the_project_is_the_journals_own_repository()
    story.compacted_session_starts()
    story.expect_agent_not_told(story.agents.subject, HealthNudges.PANIC_WATCH)
    story.expect_stack(story.agents.subject, Ready, Working, ReadingOverview)
