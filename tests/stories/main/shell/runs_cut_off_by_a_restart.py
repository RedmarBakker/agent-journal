from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.ended_session import EndedSession


@story(EndedSession, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_a_session_start_after_a_restart_names_the_background_runs_it_cut_off(story):
    story.agent_starts_a_session(story.agents.subject)
    story.agent_looks_at_the_overview(story.agents.subject)
    output = story.agent_runs_a_command(story.agents.subject, f"sh -c 'sleep {story.setting(FOREGROUND_OPTION) * 3}'")
    story.journal_starts_again()
    story.agent_starts_a_session(story.agents.subject)
    story.expect_agent_told(story.agents.subject, BriefingNudges.INTERRUPTED_RUNS)
    story.background_run_ends(output)
    story.expect_stack(story.agents.subject, Ready)
