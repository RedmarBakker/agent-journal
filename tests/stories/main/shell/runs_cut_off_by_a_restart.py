from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ended_session import EndedSession


@story(EndedSession, subject=AgentRole.MAIN)
def test_a_session_start_after_a_restart_names_the_background_runs_it_cut_off(story):
    story.agent_starts_a_session(story.agents.subject)
    story.agent_looks_at_the_overview(story.agents.subject)
    output = story.agent_has_a_background_run_printing(story.agents.subject, "./scripts/migrate.sh")
    story.journal_starts_again()
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, BriefingNudges.INTERRUPTED_RUNS)
    story.expect_stack(story.agents.subject, Ready)
