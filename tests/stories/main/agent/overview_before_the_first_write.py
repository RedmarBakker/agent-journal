from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(NewSession, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_write_before_the_overview_is_refused(story):
    story.agent_writes("footer.py")
    story.expect_refused(BriefingNudges.OVERVIEW_REQUEST)
    story.expect_stack(Ready)


@story(NewSession, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_reads_and_journal_commands_go_through_before_the_overview(story):
    story.agent_reads()
    story.expect_allowed()
    story.agent_runs_in_the_shell("journal task list")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(NewSession, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_overview_frees_the_writes(story):
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(NewSession, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_stop_before_the_overview_is_refused(story):
    story.agent_stops()
    story.expect_refused(BriefingNudges.OVERVIEW_STOP)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_resumed_session_needs_no_new_overview(story):
    story.agent_resumes_the_session()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_stack(Ready)
